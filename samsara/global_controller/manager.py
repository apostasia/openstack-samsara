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

from datetime import datetime

#from samsara.common import exception
from samsara.common import manager
from samsara.common.utils import *

from samsara.context_aware.contexts import vm as vm_contexts
from samsara.context_aware.situations import base as situations
from samsara.context_aware import contexts_repository
from samsara.context_aware.interpreter.rules_handlers import cell as cell_rh
from samsara.context_aware.planner.algorithms import multi_bin_packing

from samsara.local_controller import rpcapi as slc_rpcapi



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

        # Initiate Host Rules Handler
        self.cell_rules_handler = cell_rh.CellRulesHandler()

        # Samsara Local Controller RPC API
        self.local_controller = slc_rpcapi.LocalControllerAPI()


    def update_host_info(self, context, host_name, instance_info):
        """Receives information about changes to a host's instances, and
        updates the driver's HostManager with that information.
        """
        self.driver.host_manager.update_instance_info(context, host_name, instance_info)

    def update_host_situation(self, context, host, situation):
        """Receives information about changes to a host situation, and
        updates Global Controller with that information.
        """
        situation_tuple = jsonutils.loads(situation)

        LOG.info('Host Workload Situation: %s - %s', host, situation_tuple)

        situation_description = situation_tuple['description']
        related_context = situation_tuple['related_context']

        LOG.info('related_context: %s - %s', host, related_context)

        # Update if change situation host
        host = self.global_repository.get_situation('host_situation',uuid=related_context['uuid'])
        if host:
            if host['situation'] != situation_description:
                last_change_at = datetime.utcnow().isoformat()
                related_context.update({'last_change_at': last_change_at})
                LOG.info('Change Situation: before %s - actual %s', host['situation'], situation_description)
            else:
                last_change_at = host['last_change_at']
                related_context.update({'last_change_at': last_change_at})
        else:
            last_change_at = related_context['created_at']
            related_context.update({'last_change_at': last_change_at})

        # Instantiate Host resources situation
        host_situation = situations.Situation('host_situation', situation_description, related_context)

        # Store Situation in Global Repository
        self.global_repository.store_situation(host_situation.get_situation(), update_keys=['uuid'], historical=True)
        LOG.info('Store host situation into global repository')

    @periodic_task.periodic_task(spacing=CONF.task_period,
                          run_immediately=True)
    def check_cell_status(self, context):
            # Run Host Rules Handler
            LOG.info('Run Cell Rules Handler')
            self.cell_rules_handler.reason()


    def consolidate_workload(self, context, controller_hostname):
        """ Perform workload consolidation
        """
        LOG.info('Starting Consolidation Process')
        # Instantiate planner
        migration_planner = multi_bin_packing.BestFitDecreased()

        LOG.info('Generating Migration Plan')

        time.sleep(30)
        LOG.info('Consolidation Complete')

    def balance_workload(self, context, controller_hostname):
        """ Perform workload balancing
        """
        LOG.info('Starting Balance')
        time.sleep(30)
        LOG.info('Balance Complete')
