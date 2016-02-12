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
from samsara.context_aware.sensors import virtual_machine as vm_sensors
from samsara.context_aware import contexts_repository as ctx_repository

class VirtualMachineResourceUsage(base.BaseContext):

    def __init__(self):

        self.tag = "vm_resources_usage"

        self.context = collections.namedtuple(self.tag, ['uuid', 'compute_utilization','memory_utilization','created_at'])

    def getContext(self, vm_id):

        uuid                = vm_sensors.VirtualMachineIdSensor(vm_id).read_value()

        compute_utilization = vm_sensors.VirtualMachineComputeUsageSensor(vm_id).read_value()

        memory_utilization  = vm_sensors.VirtualMachineMemoryUsageSensor(vm_id).read_value()

        created_at          = datetime.utcnow().isoformat()

        return self.context(uuid, compute_utilization, memory_utilization, created_at)

class AverageComputeUsage(base.BaseContext):
    """ Store Host Compute Usage Context """

    def __init__(self):
        context_tag = "store_host_compute_usage"
        self.ctx_repository = ctx_repository.LocalContextsRepository()

    def getContext(self, limit=10):
        """ Get stored data about host compute usage from local context repository
        """
        stored_data = [ctx['compute_utilization'] for ctx in  self.ctx_repository.retrieve_last_n_contexts('host_resources_usage', limit)]

        return stored_data

    def get_last_period_contexts(self,period):
        """ Get stored data about host compute usage from local context repository
        """
        stored_data = [ctx['compute_utilization'] for ctx in  self.ctx_repository.retrieve_last_contexts_from_period('host_resources_usage', period)]

        return stored_data
