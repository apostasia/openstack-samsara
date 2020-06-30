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

from samsara.context_aware.contexts.cell import CellContexts
from samsara.context_aware.situations.base import Situation
from samsara.context_aware import contexts_repository
from samsara.context_aware.interpreter.reason_engines.eca import cell as cell_re

from samsara.local_controller import rpcapi as slc_rpcapi


LOG = logging.getLogger(__name__)

global_controller_opts = [
    cfg.IntOpt('task_collect_energy_consumption_period',
               default=30,
               help='How often (in seconds) to run periodic tasks in '
                    'the scheduler driver of your choice. '
                    'Please note this is likely to interact with the value '
                    'of service_down_time, but exactly how they interact '
                    'will depend on your choice of scheduler driver.'),
    cfg.IntOpt('cell_check_status_period',
               default=15,
               help='How often (in seconds) to run periodic tasks in.'),
]
CONF = cfg.CONF
CONF.register_opts(global_controller_opts, group='global_controller')


class GlobalControllerManager(manager.Manager):
    """Samsara Global Controller."""

    target = messaging.Target(version='1.0')

    def __init__(self, *args, **kwargs):
        super(GlobalControllerManager, self).__init__(service_name='samsara-global_controller',
                                               *args, **kwargs)


        # Get Global contexts repository
        self.global_repository = contexts_repository.GlobalContextsRepository()

        # Initiate Host Rules Handler
        self.cell_rules_handler = cell_re.CellReasonEngine()

        # Samsara Local Controller RPC API
        self.local_controller = slc_rpcapi.LocalControllerAPI()

        # Samsara Cell Contexts Handler
        self.cell_contexts = CellContexts()


    def update_host_info(self, context, host_name, instance_info):
        """Receives information about changes to a host's instances, and
        updates the driver's HostManager with that information.
        """
        self.driver.host_manager.update_instance_info(context, host_name, instance_info)

    def update_host_situation(self, context, host, situation):
        """Receives information about changes to a host situation, and
        updates Global Controller with that information.
        """

        # Deserialize JSON situation
        situation_tuple = jsonutils.loads(situation)

        situation_description = situation_tuple['description']
        related_context       = situation_tuple['related_context']

        LOG.info('Host %s Workload Situation: %s', host, situation_description.upper())

        LOG.debug('Host %s related context: %s', host, related_context)

        # Instantiate Host resources situation
        host_situation = Situation('host_situation', situation_description, related_context)

        # Update Host Situation
        self.cell_contexts.update_host_situation(host, host_situation)

    @periodic_task.periodic_task(spacing=CONF.global_controller.cell_check_status_period)
    def check_cell_status(self, context):
            # Run Host Rules Handler
            LOG.info('Run Cell Rules Handler')
            self.cell_rules_handler.reason()
