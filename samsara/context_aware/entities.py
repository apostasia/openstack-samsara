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
from samsara.context_aware import base

class Host(base.BaseEntity):
    def __init__(self, **kwargs):
        "Host Identification"
        self.uuid     = None
        self.hostname = None
        self.ip       = None
           
        "Host Capacities"
        self.compute_capacity = ""
        self.memory_capacity  = ""
        self.network_capacity = ""
        pass
          
class VirtualMachine(base.BaseEntity):
    def __init__(self, **kwargs):
        "Virtual Machine Identification"
        self.uuid  = None
        pass