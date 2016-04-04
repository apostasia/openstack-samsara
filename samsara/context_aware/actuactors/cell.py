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

from samsara.context_aware.actuactors import base
from samsara.drivers import openstack



LOG = logging.getLogger(__name__)


class CellActuactor(base.BaseActuator):

    def __init__(self):
        self.cloud_driver = openstack.OpenStackDriver()

    def _wake_host(self, host):
            pass

    def _sleep_host(self, host):
            pass

    def consolidate(self, consolidation_plan):

        migration_plan    = consolidation_plan['migration_plan']
        hosts_to_activate = consolidation_plan['hosts_to_deactivate']

        LOG.info("Start migration process")
        print("Start migration process")
        self._migrate_instances(migration_plan)

        LOG.info("Set hosts to low power mode")
        print("Set hosts to low power mode")
        #self._deactivate_hosts(hosts_to_deactivate)


    def balance(self, load_balance_plan):
            pass


    def _migrate_instances(self, migration_plan):
        """ Migrate instance list
        """
        retry_migrations = []
        for migration in migration_plan:

            migration_result = self.cloud_driver.migrate_server(migration['instance'], migration['host_dest'], False)

            if not migration_result:
                retry_migrations.append(migration)

        # Retry Failed Migrations
        if retry_migrations:
            LOG.info("Retry Failed Migrations")
            for migration in retry_migrations:
                migration_result = self.cloud_driver.migrate_server(migration['instance'], migration['host_dest'], False)
