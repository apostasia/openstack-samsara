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

"""Starter script for Samsara Cell Collector Agent."""

import sys
import eventlet
import time

from oslo_config import cfg
from oslo_log import log as logging

from samsara import config
from samsara.common import service
from samsara.common import utils
from samsara import version

from samsara.context_aware.contexts.cell import CellContexts
from samsara.context_aware import contexts_repository

CONF = cfg.CONF


# Get Global contexts repository
global_repository = contexts_repository.GlobalContextsRepository()

# Samsara Cell Contexts Handler
cell_contexts = CellContexts()


def main():
    config.parse_args(sys.argv)
    logging.setup(CONF,'samsara')

    LOG = logging.getLogger(__name__)

    while True:

        LOG.info('Check Energy Consumption')

        # Get Consume
        ctx_energy_consumption = cell_contexts.get_cell_energy_consumption()

        # Store Energy Consume Context
        global_repository.store_context(ctx_energy_consumption)


        #### Delay for 15 seconds ####
        time.sleep(15)
        
if __name__ == "__main__":
    sys.exit(main())
