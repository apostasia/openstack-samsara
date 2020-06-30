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
Samsara Cell Collector Manager
"""

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_serialization import jsonutils
from oslo_service import periodic_task
from oslo_utils import importutils

#from samsara.common import config
#from samsara.common import exception
from samsara.common import manager

from samsara.context_aware import entities
from samsara.context_aware import sensors
from samsara.context_aware.contexts.cell import CellContexts
from samsara.context_aware import contexts_repository


LOG = logging.getLogger(__name__)

collector_manager_opts = [
    cfg.IntOpt('collect_contexts_period',
               default=30,
               help='How often (in seconds) to run periodic cell contexts collect.'),
]
CONF = cfg.CONF
CONF.register_opts(collector_manager_opts, group='cell')

class CellCollectorManager(manager.Manager):
    """Samsara Cell Collector Agent."""

    def __init__(self, *args, **kwargs):
        super(CellCollectorManager, self).__init__(service_name='cell_collector',
                                               *args, **kwargs)

        self.global_repository = contexts_repository.GlobalContextsRepository()

    @periodic_task.periodic_task(spacing=CONF.cell.collect_contexts_period,
                          run_immediately=True)
    def check_cell_energy_consume(self,context):
        """ Perform Energy Consumption Evaluation
        """
        LOG.info('Check Energy Consumption')

        # Get Consume
        ctx_energy_consumption = self.cell_contexts.get_cell_energy_consumption()

        # Store Energy Consume Context
        self.global_repository.store_context(ctx_energy_consumption)
