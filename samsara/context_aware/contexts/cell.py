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
from datetime import datetime
import numpy as np
import time
from oslo_config import cfg
from oslo_log import log as logging

from samsara.context_aware import base
from samsara.context_aware.sensors import host as host_sensors
from samsara.context_aware.sensors import hypervisor as hypervisor_sensors
from samsara.context_aware import contexts_repository
from samsara.context_aware.sensors.cell import *

from samsara.common.utils import *


LOG = logging.getLogger(__name__)


class CellContexts(base.BaseContext):
    """ Representing  the cloud cell contexts."""

    def __init__(self):

        # Global Repository
        self.ctx_global_repository = contexts_repository.GlobalContextsRepository()

        # Get Global Repository Handler
        self.global_repository_handler = self.ctx_global_repository.get_repository_handler()


    def get_active_hosts(self):
        context = collections.namedtuple('active_hosts', ['hosts','created_at'])

        hosts = self.get_hosts_by_situations(['normal', 'underloaded', 'overloaded', 'idle'])

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_all_situations_hosts(self):
        """ Get all situations hosts """

        context = collections.namedtuple('all_situations_hosts', ['hosts','created_at'])

        hosts = self.get_hosts_by_situations(['normal', 'underloaded', 'overloaded', 'sleeping', 'hibernate', 'off', 'idle'])

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_inactive_hosts(self):
        """ Return inactive hosts in the cloud cell"""

        context = collections.namedtuple('inactive_hosts', ['hosts','created_at'])

        hosts = self.get_hosts_by_situations(['sleeping', 'hibernate', 'off'])

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_overloaded_hosts(self):
        """ Return overloaded hosts in the cloud cell"""

        context = collections.namedtuple('overloaded_hosts', ['hosts','created_at'])

        hosts = self.get_hosts_by_situations(['overloaded'])

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_underloaded_hosts(self):
        """ Return underloaded hosts in the cloud cell"""

        context = collections.namedtuple('underloaded_hosts', ['hosts','created_at'])

        hosts = self.get_hosts_by_situations(['underloaded'])

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_idle_hosts(self):
        """ Return idle hosts in the cloud cell"""

        context = collections.namedtuple('idle_hosts', ['hosts','created_at'])

        hosts = self.get_hosts_by_situations(['idle'])

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_host_info(self, hostname):
        host_info = self.global_repository_handler['host_info'].find_one(hostname=hostname)
        return host_info

    def _get_host_info(self, uuid):
        host_info = self.global_repository_handler['host_info'].find_one(uuid=uuid)
        return host_info

    def get_host_situation(self, hostname):
        host_situation = self.global_repository_handler['host_situation'].find_one(hostname=hostname)

        return host_situation

    def _get_host_situation(self, uuid):
        host_situation = self.global_repository_handler['host_situation'].find_one(uuid=uuid)

        return host_situation

    def get_tasks_status(self):
        pass

    def get_hosts_by_situations(self, situations):
         """ Return host in the cloud cell by situation
         """

         info_fields      = ['id', 'created_at']
         situation_fields = ['id', 'uuid']

         hosts = []

         for host_situation in self.global_repository_handler['host_situation'].find(situation=situations):

             # Get host info with filtered fields
             info = self._get_host_info(host_situation['uuid'])

             # Filter host info and host situation by fields
             filtered_info = {k:v for k,v in info.items() if not k in info_fields}

             filtered_situation = {k:v for k,v in host_situation.items() if not k in situation_fields}

             hosts.append(dict(list(filtered_info.items()) + list(filtered_situation.items())))


         return hosts

    def update_host_situation(self, hostname, situation):

        last_situation = self.get_host_situation(hostname)

        if last_situation:

            # Update if change situation host
            if last_situation['situation'] != situation.description:
                # Set time change
                last_change_at = datetime.utcnow().isoformat()

                # Update last time change
                situation.related_context['previous_situation'] = last_situation['situation']

                situation.related_context['previous_situation_period'] = get_period_from_time(last_situation['last_change_at'], last_change_at)
                situation.related_context['last_change_at'] = last_change_at

                LOG.info('Change Situation (before, actual): %s -  %s', last_situation['situation'].upper(), situation.description.upper())

        # If new situation
        else:
            situation.related_context['last_change_at'] = datetime.utcnow().isoformat()

            situation.related_context['created_at'] = datetime.utcnow().isoformat()

        # Store Situation in Global Repository
        self.ctx_global_repository.store_situation(situation.get_situation(), update_keys=['uuid'], historical=True)

        LOG.info('Store host situation into global repository')

    def get_cell_energy_consumption(self):

        context = collections.namedtuple('cell_energy_consumption', ['energy_consumption','created_at'])

        energy_consumption = round(EnergyConsumptionSensor.read_value(),3)

        created_at = datetime.utcnow().isoformat()

        return context(energy_consumption, created_at)
