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
Samsara Global Controller Manager
"""

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_serialization import jsonutils
from oslo_service import periodic_task
from oslo_utils import importutils

#from samsara.common import exception
from samsara.common import manager
from samsara.common.utils import *

from samsara.context_aware.contexts import host as host_contexts
from samsara.context_aware.contexts import vm as vm_contexts
from samsara.context_aware.situations import base as situations
from samsara.context_aware import contexts_repository

import yaml


LOG = logging.getLogger(__name__)

global_controller_opts = [
    cfg.IntOpt('task_period',
               default=10,
               help='How often (in seconds) to run periodic tasks in '
                    'the scheduler driver of your choice. '
                    'Please note this is likely to interact with the value '
                    'of service_down_time, but exactly how they interact '
                    'will depend on your choice of scheduler driver.'),
]
CONF = cfg.CONF
CONF.register_opts(global_controller_opts)


class GlobalControllerManager(manager.Manager):
    """Samsara Global Controller."""

    target = messaging.Target(version='1.0')

    def __init__(self, *args, **kwargs):
        super(GlobalControllerManager, self).__init__(service_name='samsara-global_controller',
                                               *args, **kwargs)


        # Get Global contexts repository
        self.global_repository = contexts_repository.GlobalContextsRepository()


    def update_host_info(self, context, host_name, instance_info):
        """Receives information about changes to a host's instances, and
        updates the driver's HostManager with that information.
        """
        # self.driver.host_manager.update_instance_info(context, host_name, instance_info)

    def update_host_situation(self, context, host, situation):
        """Receives information about changes to a host situation, and
        updates Global Controller with that information.
        """
        # situation_tuple = decode_unicode(jsonutils.loads(situation))

        LOG.info('Host Workload Situation: %s - %s', host, situation_tuple)

        situation_description = situation_tuple['description']
        related_context = situation_tuple['related_context']

        LOG.info('related_context: %s - %s', host, type(related_context))

        # # Instantiate Host resources situation
        # host_situation = situations.Situation('host_situation', situation_description, related_context)
        #
        # # Store Situation in Global Repository
        # self.global_repository.store_situation(situation)
        #
        # LOG.info('Store host situation into global repository')

    def workload_consolidate(self,context):
        """ Perform workload consolidation
        """

    def workload_balance(self,context):
        """ Perform worload balancing
        """

    # # @periodic_task.periodic_task(spacing=CONF.task_period,
    #                              run_immediately=True)
    # def listen_notify(self, context):
    #     self.driver.run_periodic_tasks(context)
    #
    # # @periodic_task.periodic_task(spacing=CONF.task_period,
    #                              run_immediately=True)
    # def _run_periodic_tasks(self, context):
    #     self.driver.run_periodic_tasks(context)
#
#     @messaging.expected_exceptions(exception.NoValidHost)
#     def select_destinations(self, context, request_spec, filter_properties):
#         """Returns destinations(s) best suited for this request_spec and
#         filter_properties.
#
#         The result should be a list of dicts with 'host', 'nodename' and
#         'limits' as keys.
#         """
#         dests = self.driver.select_destinations(context, request_spec,
#             filter_properties)
#         return jsonutils.to_primitive(dests)
#
#
#
#     def update_instance_info(self, context, host_name, instance_info):
#         """Receives information about changes to a host's instances, and
#         updates the driver's HostManager with that information.
#         """
#         self.driver.host_manager.update_instance_info(context, host_name,
#                                                       instance_info)
#
#     def delete_instance_info(self, context, host_name, instance_uuid):
#         """Receives information about the deletion of one of a host's
#         instances, and updates the driver's HostManager with that information.
#         """
#         self.driver.host_manager.delete_instance_info(context, host_name,
#                                                       instance_uuid)
#
#     def sync_instance_info(self, context, host_name, instance_uuids):
#         """Receives a sync request from a host, and passes it on to the
#         driver's HostManager.
#         """
#         self.driver.host_manager.sync_instance_info(context, host_name,
#                                                     instance_uuids)
