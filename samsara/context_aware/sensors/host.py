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
from samsara.drivers import baremetal
from samsara.drivers import virt

sensors_opts = [
    cfg.StrOpt('mgmt_nic', default='eth0',
                                    help=("Management NIC")),

    cfg.StrOpt('hypervisor_driver', default='LibvirtDriver',
                                    help=("HyperVisor Driver"))
]

CONF = cfg.CONF
CONF.register_opts(sensors_opts)

baremetal_driver = baremetal.BareMetalDriver()

class HostIdSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the UUID identification for host provides by libvirt"""
        driver = virt.LibvirtDriver()
        host_uuid = str(driver.get_host_uuid())
        return host_uuid

class HostComputeCapacitySensor(base.BaseSensor):

    @staticmethod
    def read_value():
        """Returns the host compute capacity"""
        driver = baremetal.BareMetalDriver()
        compute_capacity = driver.get_max_mips()
        return compute_capacity

class HostCPUNumberSensor(base.BaseSensor):

    @staticmethod
    def read_value():
        """Returns the host cpu number available"""
        driver = baremetal.BareMetalDriver()
        cpu_number = driver.get_number_cpu()
        return cpu_number

class HostComputeUsageSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the host compute usage"""
        global baremetal_driver
        driver = baremetal_driver
        compute_usage = driver.get_current_usage_mips()
        return compute_usage

class HostMemoryCapacitySensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the host memory capacity"""
        driver = baremetal.BareMetalDriver()
        value = driver.get_max_memory()
        return value

class HostMemoryUsageSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the memory memory usage"""
        driver = baremetal.BareMetalDriver()
        value = driver.get_used_memory()
        return value

class HostNetworkNicCapacitySensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the nic capacity bandwith"""
        driver = baremetal.BareMetalDriver()
        value = driver.get_host_nic_speed(CONF.mgmt_nic)
        return value

class HostNetworkHostnameSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the network hostname"""
        driver = baremetal.BareMetalDriver()
        value = driver.get_hostname()
        return value

class HostNetworkNicHwAddressSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the mgmt nic hw address """
        driver = baremetal.BareMetalDriver()
        value = driver.get_mac_address(CONF.mgmt_nic)
        return value

class HostComputeNativeLoadSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the host native compute load in percentual"""
        global baremetal_driver
        driver = baremetal_driver
        compute_load = driver.get_sys_cpu_percentual()
        return compute_load
