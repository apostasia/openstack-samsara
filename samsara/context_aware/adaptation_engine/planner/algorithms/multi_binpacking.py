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
from oslo_log import log as logging
from oslo_serialization import jsonutils

LOG = logging.getLogger(__name__)

class BestFitDecreased(object):

    def generate_consolidation_plan(self, active_hosts):

        """ Generate Consolidation Plan

        Args:

        Returns:
            If was possible create an Consoliadation Plan, return an dict with migration plan - an dict with instance and host destiny, and an list with host to deactivate. Else, return an empty dict.

        """
        LOG.info('Create Consolidation Plan Using Best Fit Decreased Algorithm')

        migration_plan      = []
        consolidation_plan  = []
        hosts_to_deactivate = []
        failed_allocation_hosts = []


        """ Generate Hosts Candidates List """
        # Select non overloaded and non underloaded hosts as candidates from active hosts list
        hosts_candidates = [host for host in active_hosts if host['situation'] == 'normal']

        # Select underloaded hosts from active hosts list
        underloaded_hosts = [host for host in active_hosts if host['situation'] == 'underloaded' or host['situation'] == 'idle']

        # Sort underloaded hosts in used compute increased order
        underloaded_hosts = sorted(underloaded_hosts, key=lambda k: k['used_compute'])

        # Execute allocation process
        while underloaded_hosts:

            # Migrations List
            migrations = []

            # Get an underloaded host
            underloaded_host = underloaded_hosts.pop(0)

            LOG.debug("Select Underload Host to Consolidation: %s", underloaded_host['hostname'])

            # Get instances underloaded host
            instances_to_migrate = jsonutils.loads(underloaded_host['instances'])

            # If underloaded host is not empty
            if instances_to_migrate:

                # Sort instances in used compute increased order
                instances_to_migrate = sorted(instances_to_migrate, key=lambda k: k['used_compute'], reverse=True)

                allocated_instances = 0

                LOG.info('Create Consolidation Migration Plan')
                for instance in instances_to_migrate:

                    # Define initial status
                    allocated = False

                    while not allocated:
                        for host in hosts_candidates:

                            LOG.info("Selected candidate host: %s", host['hostname'])

                            # If available resources exists, allocate instances to host
                            if host['available_compute'] >= instance['used_compute'] and host['available_memory'] >= instance['used_memory']:

                                LOG.info("Matching Host: %s", host['hostname'])

                                # Add Migration to Migratios List
                                migrations.append({'instance': instance['uuid'], 'host_dest': host['hostname']})

                                # Decrement host available resources
                                host['available_compute'] -= instance['used_compute']
                                host['available_memory']  -= instance['used_memory']

                                # Set allocated
                                allocated = True

                                # Decrement qtd instances_to_migrate
                                allocated_instances += 1

                                # To next instance
                                break

                            else:
                                LOG.info("Allocation Failed: no available resources")

                        if not allocated:

                            if underloaded_hosts:

                                LOG.info("Unavailable Hosts Candidates: Get an host from underloaded hosts")

                                # Select underloaded hosts from active hosts list
                                underloaded_hosts_candidates = [host for host in underloaded_hosts if host['uuid'] != underloaded_host['uuid']]

                                LOG.debug("Selected candidates hosts: %s", str(underloaded_hosts_candidates))

                                # Select least underloaded_hosts
                                least_underloaded_host = max(underloaded_hosts_candidates, key=lambda k: k['used_compute'])
                                LOG.debug("Selected new candidate host: %s", str(least_underloaded_host['hostname']))

                                # Add hosts candidates
                                hosts_candidates.append(least_underloaded_host)

                                # Remove host from underload hosts list
                                underloaded_hosts.remove(least_underloaded_host)

                                # Sort in available compute decreased order
                                hosts_candidates = sorted(hosts_candidates, key=lambda k: k['available_compute'], reverse=True)

                            else:
                                LOG.info("Unavailable Hosts Inactive: Failed Allocation!!!")
                                break

                # If all instances are allocated to host destiny
                if allocated_instances == len(instances_to_migrate):


                    # Add migrations to migration plan
                    migration_plan.extend(migrations)
                    LOG.info("All hosts allocated with success!")

                    # Add host to deactivation plan
                    hosts_to_deactivate.append(underloaded_host['hostname'])
                    LOG.info("Add %s host to deactivate list", underloaded_host['hostname'])

                else:

                    LOG.info("Failed Allocation host: %s", underloaded_host['hostname'])
                    LOG.info("Resting instances: %s", str(instances_to_migrate))

            else:
                # Remove from underloaded hosts list and add to deactivate hosts list, and go to next underload host analysis.
                LOG.info("No %s host instances to allocated", underloaded_host['hostname'])

                hosts_to_deactivate.append(underloaded_host['hostname'])
                LOG.info("Add %s host to deactivate list", underloaded_host['hostname'])

        if migration_plan or hosts_to_deactivate:
            # Return consolidation plan (migrantion plan + deactivation plan)
            return {'migration_plan': migration_plan, 'hosts_to_deactivate': hosts_to_deactivate}
        else:
            return {}


    def generate_load_balance_plan(self, active_hosts=[], inactive_hosts=[]):
        """ Generate Load Balance Plan

        Args:

        Returns:
            If was possible create an Load Balance Plan, return an dict with migration plan - an dict with intance and host destiny, and an list with host to activate. Else, return an empty dict.

        """

        LOG.info('Create Load Balance Plan Using Best Fit Decreased Algorithm')

        migration_plan    = []
        load_balance_plan = {}
        hosts_to_activate = []
        instances_to_migrate = []

        # Select overloaded hosts
        hosts_overloaded = [host for host in active_hosts if host['situation'] == 'overloaded']

        # Generate Hosts Candidates list
        # selecting non overloaded hosts from active hosts list

        non_overloaded_hosts = [host for host in active_hosts if host['situation'] != 'overloaded']

        # Sort in available compute increased order
        hosts_candidates = sorted(non_overloaded_hosts, key=lambda k: k['available_compute'])

        # For each instance in decreased used compute order, search an host to migrate
        LOG.info('Create Load Balance Migration Plan')
        for host in hosts_overloaded:

            # Get instances to migrate and sort in used compute decreased order
            instances = sorted(jsonutils.loads(host['instances']), key=lambda k: k['used_compute'], reverse=True)

            current_compute_load = host['used_compute']
            max_compute_load     = host['available_compute']

            while current_compute_load >= max_compute_load and instances:
                # Remove instance from host list
                instance_to_migrate = instances.pop()

                # Decrement current load host
                current_compute_load -= instance_to_migrate['used_compute']

                # Add instance to migrantion list
                instances_to_migrate.append(instance_to_migrate)

            # Start allocating instances process
            allocated_instances = 0
            for instance in sorted(instances_to_migrate, key=lambda k: k['used_compute'], reverse=True):
                allocated = False

                while not allocated:

                    for host in hosts_candidates:
                        LOG.info("Selected candidate host: %s", host['hostname'])

                        # If available resources exists, allocate instances to host
                        if host['available_compute'] >= instance['used_compute'] and host['available_memory'] >= instance['used_memory']:
                            LOG.info("Matching Host: %s", host['hostname'])

                            # Add Migration to plan
                            migration_plan.append({'instance': instance['uuid'], 'host_dest': host['hostname']})

                            # Decrement host available resources
                            host['available_compute'] -= instance['used_compute']
                            host['available_memory']  -= instance['used_memory']

                            # Set allocated
                            allocated = True

                            # Decrement qtd instances_to_migrate
                            allocated_instances += 1
                            break

                        else:
                            LOG.info("Allocation Failed")
                            break


                    if not allocated:
                        LOG.info("Unavailable Hosts Candidates: Search for Inactive Hosts...")

                        # Try activated new host.
                        if inactive_hosts:
                            # Select host from inactive host list
                            LOG.info("Get an host from inactive hosts")
                            host = inactive_hosts.pop()


                            # Add host to activation plan
                            LOG.info("Add %s to activation plan.", host['hostname'])
                            hosts_to_activate.append(host['hostname'])


                            # Add host to candidates list
                            LOG.info("Add %s host to candidates list.", host['hostname'])
                            hosts_candidates.append(host)

                            # Sort in available compute decreased order
                            LOG.info("Sort candidates list.")
                            hosts_candidates = sorted(hosts_candidates, key=lambda k: k['available_compute'], reverse=True)

                        else:
                            LOG.info("Unavailable Hosts Inactive: Failed Allocation!!!")
                            break

        # Return Load Balance plan if migrantion plan exists.
        if migration_plan:
             # Return consolidation plan (migrantion plan + deactivation plan)
             return {'migration_plan': migration_plan, 'hosts_to_activate': hosts_to_activate}
        else:
            return {}
