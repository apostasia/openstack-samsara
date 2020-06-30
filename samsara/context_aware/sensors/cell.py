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
from samsara.drivers.power_management.dmm.dmm import DMMDriver

import abc


# sensors_opts = [
#     cfg.IntOpt('sensor_time_frame', default=5,
#                                     help=("Management NIC")),
# ]
#
# CONF = cfg.CONF
# CONF.register_opts(sensors_opts, group='cell_sensors')


class EnergyConsumptionSensor(base.BaseSensor):
    @staticmethod
    def read_value():
        """Returns the energy consumption"""
        driver = DMMDriver()
        energy_consumption = driver.get_consumption()
        return energy_consumption
