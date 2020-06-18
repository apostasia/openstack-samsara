# coding=utf-8

# Copyright 2013 Hewlett-Packard Development Company, L.P.
# Copyright 2013 International Business Machines Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Conduct all activity related to bare-metal deployments.

A single instance of :py:class:`ironic.conductor.manager.ConductorManager` is
created within the *ironic-conductor* process, and is responsible for
performing all actions on bare metal resources (Chassis, Nodes, and Ports).
Commands are received via RPCs. The conductor service also performs periodic
tasks, eg.  to monitor the status of active deployments.

Drivers are loaded via entrypoints by the
:py:class:`ironic.common.driver_factory` class. Each driver is instantiated
only once, when the ConductorManager service starts.  In this way, a single
ConductorManager may use multiple drivers, and manage heterogeneous hardware.

When multiple :py:class:`ConductorManager` are run on different hosts, they are
all active and cooperatively manage all nodes in the deployment.  Nodes are
locked by each conductor when performing actions which change the state of that
node; these locks are represented by the
:py:class:`ironic.conductor.task_manager.TaskManager` class.

A :py:class:`ironic.common.hash_ring.HashRing` is used to distribute nodes
across the set of active conductors which support each node's driver.
Rebalancing this ring can trigger various actions by each conductor, such as
building or tearing down the TFTP environment for a node, notifying Neutron of
a change, etc.
"""

import collections
import datetime
import inspect
import tempfile
import threading

import eventlet
from eventlet import greenpool
from oslo_concurrency import lockutils
from oslo_config import cfg
from oslo_context import context as ironic_context
# from oslo_db import exception as db_exception
from oslo_log import log
import oslo_messaging as messaging
from oslo_service import periodic_task
from oslo_utils import excutils
from oslo_utils import uuidutils


from samsara.common import exception
from samsara.common.i18n import _
from samsara.common.i18n import _LC
from samsara.common.i18n import _LE
from samsara.common.i18n import _LI
from samsara.common.i18n import _LW
from samsara.common import rpc
# from samsara.common import states
# from samsara.conductor import task_manager
# from samsara.conductor import utils
# from samsara.db import api as dbapi
from samsara import objects
from samsara.objects import base as objects_base

MANAGER_TOPIC = 'samsara.conductor_manager'
WORKER_SPAWN_lOCK = "conductor_worker_spawn"

LOG = log.getLogger(__name__)

conductor_opts = [
    cfg.IntOpt('periodic_max_workers',
               default=8,
               help=_('Maximum number of worker threads that can be started '
                      'simultaneously by a periodic task. Should be less '
                      'than RPC thread pool size.')),
    cfg.IntOpt('workers_pool_size',
               default=100,
               help=_('The size of the workers greenthread pool.')),
    cfg.IntOpt('node_locked_retry_attempts',
               default=3,
               help=_('Number of attempts to grab a node lock.')),
    cfg.IntOpt('node_locked_retry_interval',
               default=1,
               help=_('Seconds to sleep between node lock attempts.')),
]

CONF = cfg.CONF
CONF.register_opts(conductor_opts, 'conductor')

# SYNC_EXCLUDED_STATES = (states.DEPLOYWAIT, states.CLEANWAIT, states.ENROLL)

class ConductorManager(periodic_task.PeriodicTasks):
    """Ironic Conductor manager main class."""

    # NOTE(rloo): This must be in sync with rpcapi.ConductorAPI's.
    RPC_API_VERSION = '1.0'

    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host="teste-default-conductor"):
        super(ConductorManager, self).__init__(CONF)
        if not host:
            host = CONF.host
        self.host = host
        self.topic = topic
        # self.power_state_sync_count = collections.defaultdict(int)
        self.notifier = rpc.get_notifier()

    def init_host(self):

        self._keepalive_evt = threading.Event()
        """Event for the keepalive thread."""

        self._worker_pool = greenpool.GreenPool(
            size=CONF.conductor.workers_pool_size)
        """GreenPool of background workers for performing tasks async."""

        # Spawn a dedicated greenthread for the keepalive
        try:
            self._spawn_worker(self._conductor_service_record_keepalive)
            LOG.info(_LI('Successfully started conductor with hostname '
                         '%(hostname)s.'),
                     {'hostname': self.host})
        except exception.NoFreeConductorWorker:
            with excutils.save_and_reraise_exception():
                LOG.critical(_LC('Failed to start keepalive'))
                self.del_host()

    def periodic_tasks(self, context, raise_on_error=False):
        """Periodic tasks are run at pre-specified interval."""
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    
    @lockutils.synchronized(WORKER_SPAWN_lOCK, 'samsara-')
    def _spawn_worker(self, func, *args, **kwargs):

        """Create a greenthread to run func(*args, **kwargs).

        Spawns a greenthread if there are free slots in pool, otherwise raises
        exception. Execution control returns immediately to the caller.

        :returns: GreenThread object.
        :raises: NoFreeConductorWorker if worker pool is currently full.

        """
        if self._worker_pool.free():
            return self._worker_pool.spawn(func, *args, **kwargs)
        else:
            raise exception.NoFreeConductorWorker()

        
    def get_info(self, context, node_obj):
        pass
            