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

"""Generic Node base class for all workers that run on hosts."""

from oslo_context import context as oslo_context
import os
import random
import socket
import sys

from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_service import service
from oslo_utils import importutils

from samsara.common import baserpc
from samsara.common import context
from samsara.common import exception
from samsara._i18n import _, _LE, _LI, _LW
from samsara import objects
from samsara.objects import base as objects_base
from samsara.common import rpc
from samsara import utils
from samsara import version

LOG = logging.getLogger(__name__)

service_opts = [
    cfg.IntOpt('report_interval',
               default=10,
               help='Seconds between nodes reporting state to datastore'),
    cfg.BoolOpt('periodic_enable',
               default=True,
               help='Enable periodic tasks'),
    cfg.IntOpt('periodic_fuzzy_delay',
               default=60,
               help='Range of seconds to randomly delay when starting the'
                    ' periodic task scheduler to reduce stampeding.'
                    ' (Disable by setting to 0)'),
    cfg.StrOpt('local_controller_manager',
               default='samsara.local_controller.manager.LocalControllerManager',
               help='Full class name for the Manager for local controller'),
    cfg.StrOpt('global_controller_manager',
               default='samsara.global_controller.manager.GlobalControllerManager',
               help='Full class name for the Manager for global controller'),
    cfg.StrOpt('collector_manager',
               default='samsara.collector.manager.CollectorManager',
               help='Full class name for the Manager for collector'),

    cfg.IntOpt('service_down_time',
               default=60,
               help='Maximum time since last check-in for up service'),
    ]

CONF = cfg.CONF
CONF.register_opts(service_opts)
CONF.import_opt('host', 'samsara.common.netconf')

class Service(service.Service):
    """Service object for binaries running on hosts.

    A service takes a manager and enables rpc by listening to queues based
    on topic. It also periodically runs tasks on the manager and reports
    its state to the database services table.
    """

    def __init__(self, host, binary, topic, manager, report_interval=None,
                 periodic_enable=None, periodic_fuzzy_delay=None,
                 periodic_interval_max=None,
                 *args, **kwargs):

        super(Service, self).__init__()


        self.host = host
        self.binary = binary
        self.topic = topic

        'Call Class Manager'

        self.manager_class_name = manager

        # Return class manager
        manager_class = importutils.import_class(self.manager_class_name)

        # Instance class
        self.manager = manager_class(host=self.host, *args, **kwargs)

        'Initial RPC config'
        self.rpcserver = None
        self.report_interval = report_interval

        # Periodic tasks settings'
        self.periodic_enable = periodic_enable
        self.periodic_fuzzy_delay = periodic_fuzzy_delay
        self.periodic_interval_max = periodic_interval_max

        self.saved_args, self.saved_kwargs = args, kwargs
        self.backdoor_port = None

    def start(self):
        verstr = version.version_string_with_package()

        LOG.info(_LI('Starting %(topic)s node (version %(version)s)'),
                  {'topic': self.topic, 'version': verstr})

        self.basic_config_check()
        self.manager.init_host()

        #TODO(REFACT)ctxt = context.get_admin_context()
        ctxt = oslo_context.get_admin_context()

        self.manager.pre_start_hook()

        if self.backdoor_port is not None:
            self.manager.backdoor_port = self.backdoor_port

        '''             Create RPC Service
        '''

        LOG.debug("Creating RPC server for service %s", self.topic)

        target = messaging.Target(topic=self.topic, server=self.host)

        #Define endpoints
        endpoints = [
            self.manager,
            baserpc.BaseRPCAPI(self.manager.service_name, self.backdoor_port)
        ]
        endpoints.extend(self.manager.additional_endpoints)

        # Define serializer
        # TODO - Refatorar SamsaraObjectSerializer
        serializer = objects_base.SamsaraObjectSerializer()

        # Get and start RPC server
        self.rpcserver = rpc.get_server(target, endpoints, serializer)
        self.rpcserver.start()

        self.manager.post_start_hook()


        if self.periodic_enable:
            if self.periodic_fuzzy_delay:
                initial_delay = random.randint(0, self.periodic_fuzzy_delay)
            else:
                initial_delay = None

            '''
                See http://docs.openstack.org/developer/oslo.service/api/threadgroup.html
            '''
            self.tg.add_dynamic_timer(self.periodic_tasks,
                                     initial_delay=initial_delay,
                                     periodic_interval_max=
                                        self.periodic_interval_max)

    def __getattr__(self, key):
        '''The __getattr__ method intercepts attribute references. It's called
         with the attribute name as a string whenever you try to qualify an
         instance with an undefined (nonexistent) attribute name. It is not
         called if Python can find the attribute using its inheritance tree
         search procedure.
         '''

        manager = self.__dict__.get('manager', None)
        return getattr(manager, key)

    @classmethod
    def create(cls, host=None, binary=None, topic=None, manager=None,
               report_interval=None, periodic_enable=None,
               periodic_fuzzy_delay=None, periodic_interval_max=None,
               db_allowed=True):
        """Instantiates class and passes back application object.

        :param host: defaults to CONF.host
        :param binary: defaults to basename of executable
        :param topic: defaults to bin_name - 'samsara-' part
        :param manager: defaults to CONF.<topic>_manager
        :param report_interval: defaults to CONF.report_interval
        :param periodic_enable: defaults to CONF.periodic_enable
        :param periodic_fuzzy_delay: defaults to CONF.periodic_fuzzy_delay
        :param periodic_interval_max: if set, the max time to wait between runs

        """
        if not host:
            host = CONF.host
        if not binary:
            binary = os.path.basename(sys.argv[0])
        if not topic:
            topic = binary.rpartition('samsara-')[2]
        if not manager:
            manager_cls = ('%s_manager' %
                           binary.rpartition('samsara-')[2])
            manager = CONF.get(manager_cls, None)
        if report_interval is None:
            report_interval = CONF.report_interval
        if periodic_enable is None:
            periodic_enable = CONF.periodic_enable
        if periodic_fuzzy_delay is None:
            periodic_fuzzy_delay = CONF.periodic_fuzzy_delay


        service_object = cls(host, binary, topic, manager,
                          report_interval=report_interval,
                          periodic_enable=periodic_enable,
                          periodic_fuzzy_delay=periodic_fuzzy_delay,
                          periodic_interval_max=periodic_interval_max)

        return service_object

    def kill(self):
        try:
            self.stop()
        except Exception:
            pass

    def stop(self):
        try:
            self.rpcserver.stop()
            self.rpcserver.wait()
        except Exception:
            pass

        try:
            self.manager.cleanup_host()
        except Exception:
            LOG.exception(_LE('Service error occurred during cleanup_host'))
            pass

        super(Service, self).stop()

    def periodic_tasks(self, raise_on_error=False):
        """Tasks to be run at a periodic interval."""

        #TODO(REFACT)ctxt = context.get_admin_context()
        ctxt = oslo_context.get_admin_context()
        return self.manager.periodic_tasks(ctxt, raise_on_error=raise_on_error)

    def basic_config_check(self):
        """Perform basic config checks before starting processing."""
        # Make sure the tempdir exists and is writable
        try:
            with utils.tempdir():
                pass
        except Exception as e:
            LOG.error(_LE('Temporary directory is invalid: %s'), e)
            sys.exit(1)



def process_launcher():
    return service.ProcessLauncher(CONF)


# NOTE(vish): the global launcher is to maintain the existing
#             functionality of calling service.serve +
#             service.wait
_launcher = None


def serve(server, workers=None):
    global _launcher
    if _launcher:
        raise RuntimeError(_('serve() can only be called once'))

    _launcher = service.launch(CONF, server, workers=workers)


def wait():
    _launcher.wait()
