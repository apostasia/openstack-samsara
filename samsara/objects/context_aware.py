# coding=utf-8
#
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

from oslo_utils import strutils
from oslo_utils import uuidutils
from oslo_versionedobjects import base as object_base

from samsara.common import exception
# from samsara.db import api as dbapi
from samsara.objects import base
from samsara.objects import fields as object_fields


@base.SamsaraObjectRegistry.register
class Host(base.SamsaraObject, object_base.VersionedObjectDictCompat):
    # Version 1.0: Initial version
    
    VERSION = '1.0'

    # dbapi = dbapi.get_instance()

    fields = {
        'id': object_fields.IntegerField(),
        'uuid': object_fields.UUIDField(nullable=True)
    }
    
    def __init__(self, *args, **kwargs):
            super(ContextAware, self).__init__(*args, **kwargs)
            self._reset_metadata_tracking() # from oslo_versionedobject
    
    @object_base.remotable_classmethod
    def get_host_info(cls):
        context_info = {'id':'Chablau'}
        return context_info