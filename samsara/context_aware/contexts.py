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
import time

from samsara.context_aware import base
from samsara.context_aware import sensors
from samsara.context_aware import contexts_repository as ctx_repository


class HostInfo(base.BaseContext):

    def __init__(self,context_tag):
        self.context = collections.namedtuple(context_tag,
        ['hostname',
        'uuid',
        'cpu_number',
        'max_compute',
        'max_memory',
        'mgmt_nic_speed',
        'created_at'])

    def getContext(self):

        hostname       = sensors.HostNetworkHostnameSensor.read_value()
        uuid           = sensors.HostIdSensor.read_value()
        cpu_number     = sensors.HostCPUNumberSensor.read_value()
        max_compute    = sensors.HostComputeCapacitySensor.read_value()
        max_memory     = sensors.HostMemoryCapacitySensor.read_value()
        mgmt_nic_speed = sensors.HostNetworkNicCapacitySensor.read_value()

        created_at          = datetime.utcnow().isoformat()

        return self.context(hostname,
                            uuid,
                            cpu_number,
                            max_compute,
                            max_memory,
                            mgmt_nic_speed,
                            created_at)



class HostState(base.BaseContext):

    def __init__(self,context_tag):
        self.context = collections.namedtuple(context_tag,
        ['hostname',
        'uuid',
        'state',
        'created_at'])

    def getContext(self):

        hostname       = sensors.HostNetworkHostnameSensor.read_value()
        uuid           = sensors.HostIdSensor.read_value()
        state          = None
        created_at     = datetime.utcnow().isoformat()

        return self.context(hostname,
                            uuid,
                            state,
                            created_at)


class HostResourceUtilization(base.BaseContext):

    def __init__(self,context_tag):
        self.context = collections.namedtuple(context_tag, ['compute_utilization',
        'memory_utilization',
        'created_at'])

    def getContext(self):

        compute_utilization = sensors.HostComputeUsageSensor.read_value()
        memory_utilization  = sensors.HostMemoryUsageSensor.read_value()
        created_at          = datetime.utcnow().isoformat()

        return self.context(compute_utilization,
                            memory_utilization,
                            created_at)


class HistoricalHostComputeUsage(base.BaseContext):
    """ Host Compute Usage Historical Context """

    def __init__(self, context_tag):
        self.ctx_repository = ctx_repository.LocalContextsRepository()

    def getContext(self, limit=10):
        """ Get historical data about host compute usage from local context repository
        """

        historical_data = [ctx['compute_utilization'] for ctx in  self.ctx_repository.retrieve_last_n_contexts('host_resources_usage', limit)]

        return historical_data

class VirtualMachineResourceUtilization(base.BaseContext):

    def __init__(self, context_tag, vm_id):
        self.context = collections.namedtuple(context_tag, ['uuid', 'compute_utilization','memory_utilization','created_at'])
        self.vm_id   = vm_id
        #context_vars

    def getContext(self):

        uuid                = sensors.VirtualMachineIdSensor(self.vm_id).read_value()
        compute_utilization = sensors.VirtualMachineComputeUsageSensor(self.vm_id).read_value()
        memory_utilization  = sensors.VirtualMachineMemoryUsageSensor(self.vm_id).read_value()
        created_at          = datetime.utcnow().isoformat()

        return self.context(uuid, compute_utilization, memory_utilization, created_at)
