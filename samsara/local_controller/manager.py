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

"""
Samsara Local Controller Manager
"""

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_serialization import jsonutils
from oslo_service import periodic_task
from oslo_utils import importutils

#import simplejson as json
import json

from samsara.context_aware import entities
from samsara.context_aware import sensors
from samsara.context_aware.contexts.host import HostContexts
from samsara.context_aware.contexts.vm import VirtualMachineContexts

from samsara.context_aware.contexts_repository import GlobalContextsRepository, LocalContextsRepository

from samsara.context_aware.interpreter.reason_engines.eca.host import HostReasonEngine

#from samsara.common import exception
from samsara.common import manager
from samsara.common import rpc


LOG = logging.getLogger(__name__)

local_controller_opts = [
    cfg.IntOpt('task_period',
               default=30,
               help='How often (in seconds) to run periodic tasks in '
                    'the scheduler driver of your choice. '
                    'Please note this is likely to interact with the value '
                    'of service_down_time, but exactly how they interact '
                    'will depend on your choice of scheduler driver.'),
]
CONF = cfg.CONF
CONF.register_opts(local_controller_opts, group='local_controller')


class LocalControllerManager(manager.Manager):
    """Samsara Local Agent."""

    target = messaging.Target(version='1.0')

    def __init__(self, *args, **kwargs):
        super(LocalControllerManager, self).__init__(service_name='local-controller',
                                               *args, **kwargs)
        # Get local contexts repository
        self.local_ctx_repository = LocalContextsRepository()

        # Get Global contexts repository
        self.global_ctx_repository = GlobalContextsRepository()

        # Instantiates Hosts Contexts
        self.host_contexts = HostContexts()

        # Get Host Context Info
        ctx_host_info = self.host_contexts.get_host_info()
        LOG.info('Get Host Info Context')

        # Update Cell Catalog Nodes Info
        self.global_ctx_repository.upsert_context(ctx_host_info, ['uuid'])
        LOG.info('Update Host Info Context Repository')

    @periodic_task.periodic_task(spacing=CONF.local_controller.task_period, run_immediately=True)
    def check_host_status(self, context):
        """ Check host status
        """
        LOG.info('Check host status')

        LOG.info('Run Host Contexts Interpreter:')
        self.host_ctx_interpreter = HostReasonEngine()

        LOG.info('Analyzing Host Contexts...')
        self.host_ctx_interpreter.reason()

    def retrieve_active_instances(self, context):
         """ Receives information about  to a host's active instances
         """
         return self.host_contexts_handler.get_active_instances()
