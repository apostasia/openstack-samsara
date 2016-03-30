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

from oslo_log import log as logging
from oslo_serialization import jsonutils

from samsara.context_aware.contexts import cell
from samsara.context_aware.planner import base

LOG = logging.getLogger(__name__)

class BestFitDecreased(base.Planner):

    def generate_consolidation_plan(self, compute_threshold=1, memory_threshold=1):

        migration_plan      = []
        consolidation_plan  = []
        hosts_to_deactivate = []

        # Select active hosts
        active_hosts = self.cell_contexts_handler.get_active_hosts().hosts

        # Select underloaded hosts
        hosts_underloaded = [host for host in active_hosts if host['situation'] == 'underloaded']

        # Get most underloaded host
        most_underloaded_host = min(hosts_underloaded, key=lambda k: k['used_compute'])

        # Generate hosts candidates without most underloaded host and without overloaded hosts
        hosts_candidates = [host for host in active_hosts if host != most_underloaded_host and host['situation'] != 'overloaded']

        # Get instances from most underloaded host
        instances = jsonutils.loads(most_underloaded_host['instances'])

        # Sort hosts in available compute increased order and filter fields
        hosts = [{'hostname': host['hostname'], 'available_compute': host['available_compute'] , 'available_memory': host['available_memory']} for host in sorted(hosts_candidates, key=lambda k: k['available_compute'], reverse=True)]

        # Sort instances in used compute decreased order
        instances = sorted(instances, key=lambda k: k['used_compute'])

        LOG.info('Create Migration Plan')
        for instance in instances:
            for host in hosts:
                #if  instance['used_compute'] <= (host['available_compute'] * compute_threshold) and instance['used_memory'] <= (host['available_memory'] * memory_threshold):
                if  instance['used_compute'] <= host['available_compute'] and instance['used_memory']:

                    # Add Migration to plan
                    migration_plan.append({'instance': instance['uuid'], 'host_dest': host['hostname']})

                    # Decrement available resources
                    host['available_compute'] -= instance['used_compute']
                    host['available_memory']  -= instance['used_memory']

                    # Remove instances from instances list
                    instances.remove(instance)

        # Add host to deactivation plan
        hosts_to_deactivate.append(most_underloaded_host['hostname'])

        # Return consolidation plan if all instances are allocated
        if instances:
             # Return consolidation plan (migrantion plan + deactivation plan)
             return {'migration_plan': migration_plan, 'hosts_to_deactivate': hosts_to_deactivate}
        else:
            return {}

    # def generate_load_balance_plan(self, compute_threshold=1, memory_threshold=1):
    #
    #     migration_plan    = []
    #     load_balance_plan = []
    #     hosts_to_activate = []
    #
    #     # Select active hosts
    #     active_hosts = self.cell_contexts_handler.get_active_hosts().hosts
    #
    #     # Select overloaded hosts
    #     hosts_overloaded = [host for host in active_hosts if host['situation'] == 'overloaded']
    #
    #     # Get most underloaded host
    #     most_underloaded_host = min(hosts_underloaded, key=lambda k: k['used_compute'])
    #
    #     # Generate hosts candidates without most underloaded host and without overloaded hosts
    #     hosts_candidates = [host for host in active_hosts if host != most_underloaded_host and host['situation'] != 'overloaded']
    #
    #     # Get instances from most underloaded host
    #     instances = jsonutils.loads(most_underloaded_host['instances'])
    #
    #     # Sort hosts in available compute increased order and filter fields
    #     hosts = [{'hostname': host['hostname'], 'available_compute': host['available_compute'] , 'available_memory': host['available_memory']} for host in sorted(hosts_candidates, key=lambda k: k['available_compute'], reverse=True)]
    #
    #     # Sort instances in used compute decreased order
    #     instances = sorted(instances, key=lambda k: k['used_compute'])
    #
    #     for instance in instances:
    #         for host in hosts:
    #             #if  instance['used_compute'] <= (host['available_compute'] * compute_threshold) and instance['used_memory'] <= (host['available_memory'] * memory_threshold):
    #             if  instance['used_compute'] <= host['available_compute'] and instance['used_memory']:
    #
    #                 # Add Migration to plan
    #                 migration_plan.append({'instance': instance['uuid'], 'host_dest': host['hostname']})
    #
    #                 # Decrement available resources
    #                 host['available_compute'] -= instance['used_compute']
    #                 host['available_memory']  -= instance['used_memory']
    #
    #                 # Remove instances from instances list
    #                 instances.remove(instance)
    #
    #     # Add host to deactivation plan
    #     hosts_to_deactivate.append(most_underloaded_host['hostname'])
    #
    #     # Return consolidation plan if all instances are allocated
    #     if instances:
    #          # Return consolidation plan (migrantion plan + deactivation plan)
    #          return {'migration_plan': migration_plan, 'hosts_to_deactivate': hosts_to_deactivate}
    #     else:
    #         return []
