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

import time

from oslo_log import log as logging
from oslo_config import cfg

from samsara.context_aware.contexts_repository import GlobalContextsRepository
from samsara.context_aware.adaptation_engine.actuators import base
from samsara.context_aware.adaptation_engine.actuators.host import HostActuator

from samsara.context_aware.contexts.cell import CellContexts
from samsara.context_aware.adaptation_engine.planner.base import Planner
from samsara.context_aware.situations.base import Situation

from samsara.drivers import openstack
from samsara.context_aware.adaptation_engine.actuators.drivers import network as samsara_network_driver

cell_actuator_opts = [
    cfg.IntOpt('activation_host_timeout',
               default=150,
               help='Timeout (in seconds) to waiting time for a host to change'
                    'the INACTIVE state to ACTIVE state. Default 150 seconds'
                     '(2 minutes).'),
    cfg.IntOpt('deactivation_host_timeout',
               default=150,
               help='Timeout (in seconds) to waiting time for a host to change'
                    'the ACTIVE state to INACTIVE state. Default 150 seconds'
                     '(2 minutes).'),
]
CONF = cfg.CONF
CONF.register_opts(cell_actuator_opts, group ='actuators')


LOG = logging.getLogger(__name__)


class CellActuator(base.BaseActuator):

    def __init__(self):

        # Cloud Driver
        self.cloud_driver = openstack.OpenStackDriver()

        # Global Repository
        self.global_ctx_repository = GlobalContextsRepository()

        # Get Global Repository Handler
        self.global_repository_handler = self.global_ctx_repository.get_repository_handler()

        # Host actuactors
        self.host_actuator = HostActuator()

        # Samsara Planner
        self.adaptation_planner = Planner()

        # Cell Contexts Handler
        self.cell_contexts = CellContexts()

        # Timeout
        self.activate_host_timeout = CONF.actuators.activation_host_timeout
        self.deactivate_host_timeout = CONF.actuators.deactivation_host_timeout

    def activate_host(self, hostname):
        """ Put physical node active state
        """
        # Get host info
        mgmt_nic_hwaddr = self.cell_contexts.get_host_info(hostname)['mgmt_nic_hwaddr']

        # Run WOL using physical address
        samsara_network_driver.NetworkDriver.wake_on_lan(mgmt_nic_hwaddr)

        # Start time counting
        start_time = time.time()

        # Check if host still alive
        timeout = time.time() + self.activate_host_timeout

        while True:
            if samsara_network_driver.NetworkDriver.host_is_alive(hostname):
                print("Set host %s to full power mode"% hostname)

                # Update related context
                related_context = dict()
                related_context['uuid'] = self.cell_contexts.get_host_info(hostname)['uuid']
                related_context['used_memory']       = 0
                related_context['used_compute']      = 0
                related_context['available_memory']  = 0
                related_context['available_compute'] = 0
                related_context['instances_number']  = 0
                related_context['instances']         = []

                # Create situation
                host_situation = Situation('host_situation','idle', related_context)

                # Update situation
                self.cell_contexts.update_host_situation(hostname, host_situation)

                # Register Event
                data = dict()
                data['host'] = hostname
                data['event'] = 'ACTIVATION'
                data['status'] = 'SUCCESS'
                data['elapsed time'] = (time.time() - start_time)

                self.global_ctx_repository.register_event('host', data)

                return True
            # Check if instance no migrate to destination host until expire timeout
            elif not samsara_network_driver.NetworkDriver.host_is_alive(hostname) and time.time() > timeout:
                print("Error to set hosts to full %s power mode"% hostname)

                # Update related context
                related_context = dict()
                related_context['uuid'] = self.cell_contexts.get_host_info(hostname)['uuid']
                related_context['used_memory']       = 0
                related_context['used_compute']      = 0
                related_context['available_memory']  = 0
                related_context['available_compute'] = 0
                related_context['instances_number']  = 0
                related_context['instances']         = []

                # Create situation
                host_situation = Situation('host_situation','ERROR', related_context)

                # Update situation
                self.cell_contexts.update_host_situation(hostname, host_situation)

                # Register Event
                data = dict()
                data['host'] = hostname
                data['event'] = 'ACTIVATION'
                data['status'] = 'ERROR'
                data['elapsed time'] = (time.time() - start_time)

                self.global_ctx_repository.register_event('host', data)

                return False


    def deactivate_host(self, hostname):
        """ Put physical node inactive state
        """

        return True
        
        actuactor_driver = samsara_network_driver.SSHDriver()
        command = 'systemctl hibernate'

        # TODO: update host situation method
        # If not instances on node
        if not self.cloud_driver.get_servers_by_host(hostname):

            # Run deactivate host command
            print("Set host {0} to low power mode with command {1}".format(hostname, command))
            actuactor_driver.run_cmd(hostname, command)

            # Start time counting
            start_time = time.time()

            # Set Timeout
            timeout = time.time() + self.deactivate_host_timeout

            # Check if host still alive
            while True:
                if not samsara_network_driver.NetworkDriver.host_is_alive(hostname):
                    print("Set host %s to low power mode"% hostname)

                    # Update related context
                    related_context = dict()
                    related_context['uuid'] = self.cell_contexts.get_host_info(hostname)['uuid']
                    related_context['used_memory']       = 0
                    related_context['used_compute']      = 0
                    related_context['available_memory']  = 0
                    related_context['available_compute'] = 0
                    related_context['instances']         = []

                    # Create situation
                    host_situation = Situation('host_situation','sleeping', related_context)

                    # Update situation
                    self.cell_contexts.update_host_situation(hostname, host_situation)

                    # Register Event
                    data = dict()
                    data['host'] = hostname
                    data['event'] = 'DEACTIVATION'
                    data['status'] = 'SUCCESS'
                    data['elapsed time'] = (time.time() - start_time)

                    self.global_ctx_repository.register_event('host', data)


                    return True
                # Check if instance no migrate to destination host until expire timeout
                elif samsara_network_driver.NetworkDriver.host_is_alive(hostname) and time.time() > timeout:

                    # Register Event
                    data = dict()
                    data['host'] = hostname
                    data['event'] = 'DEACTIVATION'
                    data['status'] = 'ERROR'
                    data['elapsed time'] = (time.time() - start_time)

                    self.global_ctx_repository.register_event('host', data)
                    print("Error to set hosts to low %s power mode"% hostname)
                    return False

    def migrate_instances(self, migration_plan):
        """ Migrate instances
        """
        retry_migrations = []
        start_time = time.time()

        # Start migration instances process
        for migration in migration_plan:

            # Execute migration instance and get result
            migration_result = self.cloud_driver.migrate_server(migration['instance'], migration['host_dest'], False)

            # Compute individual migration elapsed time
            migration_elapsed_time = (time.time() - start_time)

            if migration_result:

                # Register Event
                data = dict()
                data['host_dest'] = migration['host_dest']
                data['instance']   = migration['instance']
                data['status'] = 'SUCCESS'
                data['elapsed time'] = (time.time() - start_time)

                self.global_ctx_repository.register_event('migration', data)
                LOG.info("Migration Instance %s to %s host success.", migration['instance'], migration['host_dest'])

            else:

                LOG.info("Migration Instance %s to %s host failed...", migration['instance'], migration['host_dest'])

                # Register Event
                data = dict()
                data['host_dest'] = migration['host_dest']
                data['instance']   = migration['instance']
                data['status'] = 'SUCCESS'
                data['elapsed time'] = (time.time() - start_time)
                self.global_ctx_repository.register_event('migration', data)


    def consolidate_workload(self, compute_threshold = 0.8, memory_threshold  = 0.9):
        """
        """

        # Start time counting
        start_time = time.time()

        # Select active hosts
        active_hosts = self.cell_contexts.get_active_hosts().hosts

        # Generate Consolidation Plan
        consolidation_plan = self.adaptation_planner.generate_consolidation_plan(active_hosts,compute_threshold=compute_threshold, memory_threshold=memory_threshold)

        if consolidation_plan:
            migration_plan       = consolidation_plan['migration_plan']
            deactivate_host_plan = consolidation_plan['hosts_to_deactivate']

            if migration_plan:
                LOG.info("Start migration process %s", migration_plan)

                # Execute migrantion plan
                self.migrate_instances(migration_plan)

            if deactivate_host_plan:

                # Leave one host active
                if len(deactivate_host_plan) == len(active_hosts):
                    deactivate_host_plan.pop(0)

                # Set hosts to low power mode
                for host in deactivate_host_plan:
                    self.deactivate_host(host)

            # Register Event
            data = dict()
            data['event'] = "CONSOLIDATION"
            data['status'] = 'SUCCESS'
            data['elapsed time'] = (time.time() - start_time)
            self.global_ctx_repository.register_event('cell', data)

        else:
            LOG.info("Unable to generate a consolidation plan. Skipping...")
            # Register Event
            data = dict()
            data['event'] = "CONSOLIDATION"
            data['status'] = 'SKIPPING'
            data['elapsed time'] = (time.time() - start_time)
            self.global_ctx_repository.register_event('cell', data)

        LOG.info("Consolidation Process Complete after %s seconds.", (time.time() - start_time))


    def balance_workload(self, compute_threshold = 0.8, memory_threshold  = 0.9):

        # Start time counting
        start_time = time.time()

        # Select active hosts
        active_hosts = self.cell_contexts.get_active_hosts().hosts

        # Select inactive hosts
        inactive_hosts = self.cell_contexts.get_inactive_hosts().hosts

        # Generate Load Balance Plan
        load_balance_plan = self.adaptation_planner.generate_load_balance_plan(active_hosts, inactive_hosts, compute_threshold=compute_threshold, memory_threshold=memory_threshold)

        if load_balance_plan:
            LOG.info("Start migration process")

            # Set hosts to full power mode
            for host in load_balance_plan['hosts_to_activate']:
                if not self.activate_host(host):
                    return

            # Run migrations
            self.migrate_instances(load_balance_plan['migration_plan'])

            # Register Event
            data = dict()
            data['event'] = "LOAD_BALANCE"
            data['status'] = 'SUCCESS'
            data['elapsed time'] = (time.time() - start_time)
            self.global_ctx_repository.register_event('cell', data)

        else:
            LOG.info("Unable to generate a load balance plan. Skipping...")
            print("Unable to generate a load balance plan. Skipping...")
            # Register Event
            data = dict()
            data['event'] = "LOAD_BALANCE"
            data['status'] = 'SKIPPING'
            data['elapsed time'] = (time.time() - start_time)
            self.global_ctx_repository.register_event('cell', data)


        # The end
        LOG.info("Load Balance Process Complete at:", (time.time() - start_time))

        print("Load Balance Process Complete at: %s seconds." % (time.time() - start_time))
