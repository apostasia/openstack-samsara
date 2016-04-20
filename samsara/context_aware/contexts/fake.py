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

LOG = logging.getLogger(__name__)


class CellContexts(base.BaseContext):
    """ Representing  the cloud cell contexts."""

    def __init__(self):

        # Global Repository
        self.ctx_global_repository = contexts_repository.GlobalContextsRepository()

    def get_active_hosts(self):
        """ Return active host in the cloud cell"""

        context = collections.namedtuple('active_hosts', ['hosts','created_at'])

        repository_handler = self.ctx_global_repository.get_repository_handler()


        hosts = [ dict(host) for host in repository_handler['host_situation'].find(situation=['normal', 'underloaded', 'overloaded'])]

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_inactive_hosts(self):
        """ Return inactive hosts in the cloud cell"""

        context = collections.namedtuple('inactive_hosts', ['hosts','created_at'])

        repository_handler = self.ctx_global_repository.get_repository_handler()


        hosts = [ dict(host) for host in repository_handler['host_situation'].find(situation=['sleep', 'hibernate', 'off'])]

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_overloaded_hosts(self):
        """ Return overloaded hosts in the cloud cell"""

        context = collections.namedtuple('overloaded_hosts', ['hosts','created_at'])

        repository_handler = self.ctx_global_repository.get_repository_handler()


        hosts = [ dict(host) for host in repository_handler['host_situation'].find(situation=['overloaded'])]

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_underloaded_hosts(self):
        """ Return underloaded hosts in the cloud cell"""

        context = collections.namedtuple('underloaded_hosts', ['hosts','created_at'])

        repository_handler = self.ctx_global_repository.get_repository_handler()


        hosts = [ dict(host) for host in repository_handler['host_situation'].find(situation=['underloaded'])]

        created_at = datetime.utcnow().isoformat()

        return context(hosts, created_at)

    def get_tasks_status(self):
        pass



def generate_random_hosts(hosts_number=2, compute_capacity=6000.50, min_compute=0, memory_capacity=2048, min_memory=128):
    hosts_list = []
    # Generate fake hosts
    for x in range(1, hosts_number):
        uuid_obj = uuid_func.uuid4()
        host['hostname'] = "compute-00{0}".format(x)
        host['uuid']     = str(uuid_obj)
        host['used_compute'] = round(random.uniform(min_compute, compute_capacity), 2)
        host['available_compute'] = compute_capacity - used_compute
        host['used_memory']       = random.randint(min_memory, memory_capacity)
        host['available_memory']  = memory_capacity - used_memory
        host['created_at']        = datetime.utcnow().isoformat()
        hosts_list.append(host)
    return hosts_list


def generate_hosts(hosts_number=2, compute_capacity=6000.50, min_compute=0, memory_capacity=2048, min_memory=128, load=1.0):
    hosts_list = []
    # Generate fake hosts
    for x in range(1, hosts_number):
        uuid_obj = uuid_func.uuid4()

        host['hostname']          = "compute-00{0}".format(x)
        host['uuid']              = str(uuid_obj)
        host['used_compute']      = round(load*compute_capacity, 2)
        host['used_memory']       = load*memory_capacity
        host['available_compute'] = compute_capacity - used_compute
        host['available_memory']  = memory_capacity - used_memory
        host['created_at']        = datetime.utcnow().isoformat()
        hosts_list.append(host)
    return hosts_list


def generate_hosts_by_list(hosts_number=2, compute_capacity=6000.50, min_compute=0, memory_capacity=2048, min_memory=128, hosts):
    hosts_list = []
    # Generate fake hosts
    for x in range(1, hosts_number):
        uuid_obj = uuid_func.uuid4()

        host['hostname']          = "compute-00{0}".format(x)
        host['uuid']              = str(uuid_obj)
        host['used_compute']      = round(load*compute_capacity, 2)
        host['used_memory']       = load*memory_capacity
        host['available_compute'] = compute_capacity - used_compute
        host['available_memory']  = memory_capacity - used_memory
        host['created_at']        = datetime.utcnow().isoformat()
        hosts_list.append(host)
    return hosts_list
