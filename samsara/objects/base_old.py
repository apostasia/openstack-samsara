#    Copyright 2013 IBM Corp.
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

"""Samsara common internal object model"""

from oslo_log import log as logging
from oslo_versionedobjects import base as object_base

from samsara.objects import fields as object_fields


LOG = logging.getLogger('object')


class SamsaraObjectRegistry(object_base.VersionedObjectRegistry):
    pass


class SamsaraObject(object_base.VersionedObject):
    """Base class and object factory.

    This forms the base of all objects that can be remoted or instantiated
    via RPC. Simply defining a class that inherits from this base class
    will make it remotely instantiatable. Objects should implement the
    necessary "get" classmethod routines as well as "save" object methods
    as appropriate.
    """

    OBJ_SERIAL_NAMESPACE = 'samsara_object'
    OBJ_PROJECT_NAMESPACE = 'samsara'

    # TODO(lintan) Refactor these fields and create PersistentObject and
    # TimeStampObject like Nova when it is necessary.
    fields = {
        'created_at': object_fields.DateTimeField(nullable=True),
        'updated_at': object_fields.DateTimeField(nullable=True),
    }

    def as_dict(self):
        return dict((k, getattr(self, k))
                    for k in self.fields
                    if hasattr(self, k))

    def obj_refresh(self, loaded_object):
        """Applies updates for objects that inherit from base.SamsaraObject.

        Checks for updated attributes in an object. Updates are applied from
        the loaded object column by column in comparison with the current
        object.
        """
        for field in self.fields:
            if (self.obj_attr_is_set(field) and
                    self[field] != loaded_object[field]):
                self[field] = loaded_object[field]


class SamsaraPersistentObject(object):
    """Mixin class for Persistent objects (Copied from Nova).

    This adds the fields that we use in common for most persistent objects.
    """
    fields = {
        'created_at': object_fields.DateTimeField(nullable=True),
        'updated_at': object_fields.DateTimeField(nullable=True),
        'deleted_at': object_fields.DateTimeField(nullable=True),
        'deleted': object_fields.BooleanField(default=False),
        }

class SamsaraTimestampObject(object):
    """Mixin class for db backed objects with timestamp fields (Copied from Nova).
    
    Sqlalchemy models that inherit from the oslo_db TimestampMixin will include
    these fields and the corresponding objects will benefit from this mixin.
    """
    fields = {
        'created_at': object_fields.DateTimeField(nullable=True),
        'updated_at': object_fields.DateTimeField(nullable=True),
        }


""" Implement the indirection API

FROM OSLO.VERSIONEDOBJECTS DOC: supports remotable method calls. These are 
calls of the object methods and classmethods which can be executed locally or 
remotely depending on the configuration. Setting the indirection_api as 
a property of an object relays the calls to decorated methods through 
the defined RPC API. The attachment of the indirection_api should be handled by 
configuration at startup time. Second function of the indirection API 
is backporting. When the object serializer attempts to deserialize an object 
with a future version, not supported by the current instance, it calls the 
object_backport method in an attempt to backport the object to a version which 
can then be handled as normal.
"""

class SamsaraObjectIndirectionAPI(object_base.VersionedObjectIndirectionAPI):
    def __init__(self):
        super(SamsaraObjectIndirectionAPI, self).__init__()
        # FIXME(xek): importing here due to a cyclical import error
        from samsara.conductor import rpcapi as conductor_api
        self._conductor = conductor_api.ConductorAPI()

    def object_action(self, context, objinst, objmethod, args, kwargs):
        return self._conductor.object_action(context, objinst, objmethod,
                                             args, kwargs)

    def object_class_action(self, context, objname, objmethod, objver,
                            args, kwargs):
        # NOTE(xek): This method is implemented for compatibility with
        # oslo.versionedobjects 0.10.0 and older. It will be replaced by
        # object_class_action_versions.
        versions = object_base.obj_tree_get_versions(objname)
        return self.object_class_action_versions(
            context, objname, objmethod, versions, args, kwargs)

    def object_class_action_versions(self, context, objname, objmethod,
                                     object_versions, args, kwargs):
        return self._conductor.object_class_action_versions(
            context, objname, objmethod, object_versions, args, kwargs)

    def object_backport_versions(self, context, objinst, object_versions):
        return self._conductor.object_backport_versions(context, objinst,
                                                        object_versions)


class SamsaraObjectSerializer(object_base.VersionedObjectSerializer):
    # Base class to use for object hydration
    OBJ_BASE_CLASS = SamsaraObject
