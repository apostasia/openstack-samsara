# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import print_function
import collections

from oslo_config import cfg
from oslo_log import log as logging

from samsara.context_aware.contexts import cell
from samsara.context_aware.planner.algorithms import multi_bin_packing

LOG = logging.getLogger(__name__)


class Planner(object):

    def __init__(self):
        self.cell_contexts_handler = cell.CellContexts()

    def generate_consolidation_plan(self):

        consolidation_plan = []
        hosts_to_deactivate = []

        # Select active hosts
        active_hosts = self.cell_contexts_handler.get_active_hosts.hosts

        # Select underloaded hosts
        hosts_underloaded = [host for host in active_hosts if host['situation'] == 'underloaded']

        # Get most underloaded host
        most_underloaded_host = min(hosts_underloaded, key=lambda k: k['used_compute'])

        # Generate hosts candidates without most underloaded host and without overloaded hosts
        hosts_candidates = [host for host in active_hosts if host != most_underload_host and host['situation'] != 'overloaded']

        # Instantiate planner
        migration_planner = multi_bin_packing.BestFitDecreased()

        # Generate migration plan
        migration_plan = migration_planner.generate_plan(hosts_candidates, instances)

        # Add host to deactivation plan
        hosts_to_deactivate.append(most_underloaded_host['hostname'])

        # Return consolidation plan (migrantion plan + deactivation plan)
        return {'migration_plan': migration_plan, 'hosts_to_deactivate': hosts_to_deactivate}




    def generate_load_balance_plan(self, instances):
        pass

    def generate_plan():
        pass
