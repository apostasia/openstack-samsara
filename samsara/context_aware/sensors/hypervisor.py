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
    cfg.StrOpt('hypervisor_driver', default='LibvirtDriver',
                                    help=("HyperVisor Driver"))
]

CONF = cfg.CONF
CONF.register_opts(sensors_opts)

class ActiveVirtualMachinesSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the instance allocated memory"""
        driver = virt.LibvirtDriver()
        value = driver.get_active_instancesUUID()
        return value
