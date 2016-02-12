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

from oslo_config import cfg

from samsara.context_aware import base

import abc
#import untangle
from samsara.drivers import baremetal
from samsara.drivers import virt

sensors_opts = [
    cfg.StrOpt('hypervisor_driver', default='LibvirtDriver',
                                    help=("HyperVisor Driver"))
]

CONF = cfg.CONF
CONF.register_opts(sensors_opts)


""" Virtual Machine Sensors"""

class VirtualMachineSensors(base.BaseSensor):

    def __init__(self,instance_id=None):
        self.instance_id = instance_id
    pass


class VirtualMachineComputeUsageSensor(base.BaseSensor):
    def __init__(self,instance_id=None):
        self.instance_id = instance_id

    def read_value(self,is_sum=1):
        """Returns the host compute usage"""
        baremetal_driver = baremetal.BareMetalDriver()
        virt_driver      = virt.LibvirtDriver()

        host_compute_capacity_percore = baremetal_driver.get_max_mips_percore()
        host_maxfreq_percore          = baremetal_driver.get_max_freq_percore()
        host_currentfreq_percore      = baremetal_driver.get_current_freq_percore()
        vm_utilized_cputime_percore   = virt_driver.get_busytime_percore(self.instance_id,5)

        compute_usage_percore = []

        for compute_capacity, maxfreq,currentfreq, vm_utilized_cputime in zip(host_compute_capacity_percore,
                                                                             host_maxfreq_percore,
                                                                             host_currentfreq_percore,
                                                                             vm_utilized_cputime_percore):

            compute_usage_percore.append(int((((currentfreq * compute_capacity)/maxfreq) * vm_utilized_cputime)))

        value = sum(compute_usage_percore) if is_sum else compute_usage_percore

        return value

class VirtualMachineMemoryUsageSensor(base.BaseSensor):
    def __init__(self,instance_id=None):
        self.instance_id = instance_id

    def read_value(self):
        """Returns the instance allocated memory"""
        driver = virt.LibvirtDriver()
        value = driver.get_instance_allocated_memory(self.instance_id)
        return value

class VirtualMachineIdSensor(base.BaseSensor):

    def __init__(self,instance_id=None):
        self.instance_id = instance_id

    def read_value(self):
        """Returns the instance allocated memory"""
        driver = virt.LibvirtDriver()
        value = driver.get_instance_uuid(self.instance_id)
        return value

###HyperVisor Sensors

class HyperVisorActiveVirtualMachinesSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the instance allocated memory"""
        driver = virt.LibvirtDriver()
        value = driver.get_active_instacesUUID()
        return value
