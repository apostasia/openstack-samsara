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

class VirtualMachineResourceUsage(base.BaseContext):

    def __init__(self):

        self.tag = "vm_resources_usage"

        self.context = collections.namedtuple(self.tag, ['uuid', 'compute_utilization','memory_utilization','created_at'])

    def getContext(self, vm_id):

        uuid                = sensors.VirtualMachineIdSensor(self.vm_id).read_value()

        compute_utilization = sensors.VirtualMachineComputeUsageSensor(self.vm_id).read_value()

        memory_utilization  = sensors.VirtualMachineMemoryUsageSensor(self.vm_id).read_value()

        created_at          = datetime.utcnow().isoformat()

        return self.context(uuid, compute_utilization, memory_utilization, created_at)

class ActiveVirtualMachines(base.BaseContext):
    """ Representing the active virtual machines in the host."""

    def __init__(self, context_tag):
        self.context = collections.namedtuple(context_tag, ['active_vms','created_at'])


    def getContext(self):

        active_vms = sensors.ActiveVirtualMachinesSensor.read_value()
        created_at = datetime.utcnow().isoformat()

        return self.context(active_vms, created_at)
