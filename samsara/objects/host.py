#    Copyright 2013 IBM Corp
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg
from oslo_serialization import jsonutils
from oslo_utils import versionutils
import six

#from samsara import db
from samsara.common import exception
from samsara import objects
from samsara.objects import base
from samsara.objects import fields

CONF = cfg.CONF

@base.SamsaraObjectRegistry.register
class Host(base.SamsaraObject):
    # Version 1.0: Initial version
    VERSION = '1.0'


    fields = {
        'id': fields.IntegerField(read_only=True),
        'host': fields.StringField(nullable=True),
        }

    # fields = {
    #     'id': fields.IntegerField(read_only=True),
    #     'service_id': fields.IntegerField(nullable=True),
    #     'host': fields.StringField(nullable=True),
    #     'vcpus': fields.IntegerField(),
    #     'memory_mb': fields.IntegerField(),
    #     'local_gb': fields.IntegerField(),
    #     'vcpus_used': fields.IntegerField(),
    #     'memory_mb_used': fields.IntegerField(),
    #     'local_gb_used': fields.IntegerField(),
    #     'hypervisor_type': fields.StringField(),
    #     'hypervisor_version': fields.IntegerField(),
    #     'hypervisor_hostname': fields.StringField(nullable=True),
    #     'free_ram_mb': fields.IntegerField(nullable=True),
    #     'free_disk_gb': fields.IntegerField(nullable=True),
    #     'current_workload': fields.IntegerField(nullable=True),
    #     'running_vms': fields.IntegerField(nullable=True),
    #     'cpu_info': fields.StringField(nullable=True),
    #     'disk_available_least': fields.IntegerField(nullable=True),
    #     'metrics': fields.StringField(nullable=True),
    #     'stats': fields.DictOfNullableStringsField(nullable=True),
    #     'host_ip': fields.IPAddressField(nullable=True),
    #     'numa_topology': fields.StringField(nullable=True),
    #     # NOTE(pmurray): the supported_hv_specs field maps to the
    #     # supported_instances field in the database
    #     'supported_hv_specs': fields.ListOfObjectsField('HVSpec'),
    #     # NOTE(pmurray): the pci_device_pools field maps to the
    #     # pci_stats field in the database
    #     'pci_device_pools': fields.ObjectField('PciDevicePoolList',
    #                                            nullable=True),
    #     'cpu_allocation_ratio': fields.FloatField(),
    #     'ram_allocation_ratio': fields.FloatField(),
    #     }

    @base.remotable
    def get_host_info_ob(self,context=None):
        return 'Host INfo: Chablau'
