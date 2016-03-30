# Copyright (c) 2010 OpenStack Foundation
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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
from samsara.context_aware.contexts import host as host_contexts
from samsara.context_aware.contexts import vm as vm_contexts
from samsara.context_aware import contexts_repository
from samsara.context_aware.interpreter.rules_handlers import host as host_rl

#from samsara.common import exception
from samsara.common import manager
from samsara.common import rpc
from samsara.global_controller import rpcapi as sgc_rpcapi


LOG = logging.getLogger(__name__)

local_controller_opts = [
    cfg.IntOpt('task_period',
               default=10,
               help='How often (in seconds) to run periodic tasks in '
                    'the scheduler driver of your choice. '
                    'Please note this is likely to interact with the value '
                    'of service_down_time, but exactly how they interact '
                    'will depend on your choice of scheduler driver.'),
]
CONF = cfg.CONF
CONF.register_opts(local_controller_opts)


class LocalControllerManager(manager.Manager):
    """Samsara Local Agent."""

    target = messaging.Target(version='1.0')

    def __init__(self, *args, **kwargs):
        super(LocalControllerManager, self).__init__(service_name='local-controller',
                                               *args, **kwargs)
        # Get local contexts repository
        self.ctx_repository = contexts_repository.LocalContextsRepository()

        # Get Global contexts repository
        self.ctx_global_repository = contexts_repository.GlobalContextsRepository()

        # Instantiates Hosts Contexts
        self.host_contexts_handler = host_contexts.HostContexts()

        # Get Host Context Info
        ctx_host_info = self.host_contexts_handler.get_host_info()
        LOG.info('Get Host Info Context')

        # Update Cell Catalog Nodes Info
        self.ctx_global_repository.upsert_context(ctx_host_info, ['uuid'])
        LOG.info('Update Host Info Context Repository')

        # Samsara Global Controller RPC API
        self.global_controller = sgc_rpcapi.GlobalControllerAPI()


    @periodic_task.periodic_task(spacing=CONF.task_period,
                          run_immediately=True)
    def check_host_status(self, context):

        samples = str(self.host_contexts_handler.get_historical_compute_usage())
        LOG.info('Historical Compute Usage: %s', samples)

        # Initiate Host Rules Handler
        self.host_rules_handler = host_rl.HostRulesHandler()

        # Run Host Rules Handler
        LOG.info('Run Host Rules Handler')
        self.host_rules_handler.reason()


    def retrieve_active_instances(self, context):
         """Receives information about  to a host's active instances
         """
         return self.host_contexts_handler.get_active_instances()

    def call_actuactor(self, context, host_name, action):
        """ Call actuator """
        pass

    # @periodic_task.periodic_task(spacing=CONF.task_period,
    #                           run_immediately=True)
    # def _update_host_info(self, context):
    #     print ("Update host info")
    #     body = {'cpu_allocation_ratio': 30 }
    #     self.notifier.info(context, 'update_host_info', body)
    #
    #
    #
    #  @periodic_task.periodic_task(spacing=CONF.task_period,
    #                               run_immediately=True)
    #  def _run_periodic_tasks(self, context):
    #      self.driver.run_periodic_tasks(context)
    #
    # def update_host_info(self, context, host_name, instance_info):
    #     """Receives information about changes to a host's instances, and
    #     updates the driver's HostManager with that information.
    #     """
    #     self.driver.host_manager.update_instance_info(context, host_name,
    #                                                   instance_info)
    #
    # def update_instance_info(self, context, host_name, instance_info):
    #     """Receives information about changes to a host's instances, and
    #     updates the driver's HostManager with that information.
    #     """
    #     self.driver.host_manager.update_instance_info(context, host_name,
    #                                                   instance_info)
    #
    # def delete_instance_info(self, context, host_name, instance_uuid):
    #     """Receives information about the deletion of one of a host's
    #     instances, and updates the driver's HostManager with that information.
    #     """
    #     self.driver.host_manager.delete_instance_info(context, host_name,
    #                                                   instance_uuid)
    #
    # def sync_instance_info(self, context, host_name, instance_uuids):
    #     """Receives a sync request from a host, and passes it on to the
    #     driver's HostManager.
    #     """
    #     self.driver.host_manager.sync_instance_info(context, host_name,
    #                                                 instance_uuids)
    #
