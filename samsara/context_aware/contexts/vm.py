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
import numpy as np
import time

from samsara.context_aware import base
from samsara.context_aware.sensors import virtual_machine as vm_sensors
from samsara.context_aware import contexts_repository as ctx_repository

class VirtualMachineContexts(base.BaseContext):

    def __init__(self, id):
        self.id = id
        self.ctx_repository = ctx_repository.LocalContextsRepository()

    def get_resources_usage(self):

        uuid                = vm_sensors.VirtualMachineIdSensor(self.id).read_value()

        used_compute = vm_sensors.VirtualMachineComputeUsageSensor(self.id).read_value()

        used_memory  = vm_sensors.VirtualMachineUsageMemorySensor(self.id).read_value()

        allocated_memory  = vm_sensors.VirtualMachineAllocatedMemorySensor(self.id).read_value()

        created_at          = datetime.utcnow().isoformat()

        tag = "vm_resources_usage"

        context = collections.namedtuple(tag,
        ['uuid',
        'used_compute',
        'allocated_memory',
        'used_memory',
        'created_at'])

        return context(uuid, used_compute, used_memory, created_at)

    def get_historical_compute_usage(self, limit=10):
        """ Get historical data about host compute usage from local context repository
            """
        pass

    @staticmethod
    def get_avg_compute_usage(vm_uuid, limit=10):
        """ Get stored data about host compute usage from local context repository
        """
        pass
