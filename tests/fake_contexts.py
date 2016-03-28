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


import abc
import collections
from datetime import datetime
import random
import time
import uuid as uuid_func

from oslo_log import log as logging


#LOG = logging.getLogger(__name__)


def generate_hosts(hosts_number=2, compute_capacity=6000.50, min_compute=0, memory_capacity=2048, min_memory=128):

    hosts_list = []

    tag = "host"
    situation = collections.namedtuple(tag,
    ['hostname',
    'uuid',
    'used_compute',
    'available_compute',
    'used_memory',
    'available_memory',
    'created_at'])

    # Get basic host information

    for x in range(1, hosts_number):

        uuid_obj = uuid_func.uuid4()

        hostname          = "compute-00{0}".format(x)
        uuid              = str(uuid_obj)

        # Calculate average compute usage and compute available
        used_compute = round(random.uniform(min_compute, compute_capacity), 2)
        available_compute = compute_capacity - used_compute

        # Calculate average memory usage and memory available - TODO: mover para um método especializado
        used_memory      = random.randint(min_memory, memory_capacity)
        available_memory = memory_capacity - used_memory

        created_at          = datetime.utcnow().isoformat()

        hosts_list.append(situation(hostname,
                            uuid,
                            used_compute,
                            available_compute,
                            used_memory,
                            available_memory,
                            created_at))

    return hosts_list


def generate_instances(instances_number=2, min_compute=100, max_compute=100, min_memory=128, max_memory=128):

    instances = []

    tag = "instances"
    situation = collections.namedtuple(tag,
    ['uuid',
    'used_compute',
    'used_memory',
    'created_at'])

    # Get basic host information

    for x in range(0, instances_number):

        uuid_obj = uuid_func.uuid4()

        uuid         = str(uuid_obj)
        used_compute = round(random.uniform(min_compute, max_compute), 2)
        used_memory  = random.randint(min_memory, max_memory)
        created_at   = datetime.utcnow().isoformat()

        instances.append(situation(uuid, used_compute, used_memory, created_at))

    return instances
