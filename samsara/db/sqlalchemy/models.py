# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Piston Cloud Computing, Inc.
# All Rights Reserved.
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
"""
SQLAlchemy models for nova data.
"""

from oslo_config import cfg
from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import (Column, Index, Integer, BigInteger, Enum, String,
                        schema, Unicode)
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float

from nova.db.sqlalchemy import types

CONF = cfg.CONF
BASE = declarative_base()


def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')


class SamsaraBase(models.SoftDeleteMixin,
               models.TimestampMixin,
               models.ModelBase):
    metadata = None

    def __copy__(self):
        """Implement a safe copy.copy().

        SQLAlchemy-mapped objects travel with an object
        called an InstanceState, which is pegged to that object
        specifically and tracks everything about that object.  It's
        critical within all attribute operations, including gets
        and deferred loading.   This object definitely cannot be
        shared among two instances, and must be handled.

        The copy routine here makes use of session.merge() which
        already essentially implements a "copy" style of operation,
        which produces a new instance with a new InstanceState and copies
        all the data along mapped attributes without using any SQL.

        The mode we are using here has the caveat that the given object
        must be "clean", e.g. that it has no database-loaded state
        that has been updated and not flushed.   This is a good thing,
        as creating a copy of an object including non-flushed, pending
        database state is probably not a good idea; neither represents
        what the actual row looks like, and only one should be flushed.

        """
        session = orm.Session()

        copy = session.merge(self, load=False)
        session.expunge(copy)
        return copy

    def save(self, session=None):
        from nova.db.sqlalchemy import api

        if session is None:
            session = api.get_session()

        super(SamsaraBase, self).save(session=session)


class Service(BASE, SamsaraBase):
    """Represents a running service on a host."""

    __tablename__ = 'services'
    __table_args__ = (
        schema.UniqueConstraint("host", "topic", "deleted",
                                name="uniq_services0host0topic0deleted"),
        schema.UniqueConstraint("host", "binary", "deleted",
                                name="uniq_services0host0binary0deleted")
        )

    id = Column(Integer, primary_key=True)
    host = Column(String(255))  # , ForeignKey('hosts.id'))
    binary = Column(String(255))
    topic = Column(String(255))
    report_count = Column(Integer, nullable=False, default=0)
    disabled = Column(Boolean, default=False)
    disabled_reason = Column(String(255))
    last_seen_up = Column(DateTime, nullable=True)
    forced_down = Column(Boolean, default=False)
    version = Column(Integer, default=0)


class ComputeNode(BASE, SamsaraBase):
    """Represents a running compute service on a host."""

    __tablename__ = 'compute_nodes'
    __table_args__ = (
        schema.UniqueConstraint(
            'host', 'hypervisor_hostname', 'deleted',
            name="uniq_compute_nodes0host0hypervisor_hostname0deleted"),
    )
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, nullable=True)

    # FIXME(sbauza: Host field is nullable because some old Juno compute nodes
    # can still report stats from an old ResourceTracker without setting this
    # field.
    # This field has to be set non-nullable in a later cycle (probably Lxxx)
    # once we are sure that all compute nodes in production report it.
    host = Column(String(255), nullable=True)
    vcpus = Column(Integer, nullable=False)
    memory_mb = Column(Integer, nullable=False)
    local_gb = Column(Integer, nullable=False)
    vcpus_used = Column(Integer, nullable=False)
    memory_mb_used = Column(Integer, nullable=False)
    local_gb_used = Column(Integer, nullable=False)
    hypervisor_type = Column(MediumText(), nullable=False)
    hypervisor_version = Column(Integer, nullable=False)
    hypervisor_hostname = Column(String(255))

    # Free Ram, amount of activity (resize, migration, boot, etc) and
    # the number of running VM's are a good starting point for what's
    # important when making scheduling decisions.
    free_ram_mb = Column(Integer)
    free_disk_gb = Column(Integer)
    current_workload = Column(Integer)
    running_vms = Column(Integer)

    # Note(masumotok): Expected Strings example:
    #
    # '{"arch":"x86_64",
    #   "model":"Nehalem",
    #   "topology":{"sockets":1, "threads":2, "cores":3},
    #   "features":["tdtscp", "xtpr"]}'
    #
    # Points are "json translatable" and it must have all dictionary keys
    # above, since it is copied from <cpu> tag of getCapabilities()
    # (See libvirt.virtConnection).
    cpu_info = Column(MediumText(), nullable=False)
    disk_available_least = Column(Integer)
    host_ip = Column(types.IPAddress())
    supported_instances = Column(Text)
    metrics = Column(Text)

    # Note(yongli): json string PCI Stats
    # '{"vendor_id":"8086", "product_id":"1234", "count":3 }'
    pci_stats = Column(Text)

    # extra_resources is a json string containing arbitrary
    # data about additional resources.
    extra_resources = Column(Text)

    # json-encode string containing compute node statistics
    stats = Column(Text, default='{}')

    # json-encoded dict that contains NUMA topology as generated by
    # objects.NUMATopoloogy._to_json()
    numa_topology = Column(Text)

    # allocation ratios provided by the RT
    ram_allocation_ratio = Column(Float, nullable=True)
    cpu_allocation_ratio = Column(Float, nullable=True)

class Instance(BASE, SamsaraBase):
    """Represents a guest VM."""
    __tablename__ = 'instances'
    __table_args__ = (
        Index('uuid', 'uuid', unique=True),
        Index('instances_project_id_deleted_idx',
              'project_id', 'deleted'),
        Index('instances_reservation_id_idx',
              'reservation_id'),
        Index('instances_terminated_at_launched_at_idx',
              'terminated_at', 'launched_at'),
        Index('instances_uuid_deleted_idx',
              'uuid', 'deleted'),
        Index('instances_task_state_updated_at_idx',
              'task_state', 'updated_at'),
        Index('instances_host_node_deleted_idx',
              'host', 'node', 'deleted'),
        Index('instances_host_deleted_cleaned_idx',
              'host', 'deleted', 'cleaned'),
        schema.UniqueConstraint('uuid', name='uniq_instances0uuid'),
    )
    injected_files = []

    id = Column(Integer, primary_key=True, autoincrement=True)

    @property
    def name(self):
        try:
            base_name = CONF.instance_name_template % self.id
        except TypeError:
            # Support templates like "uuid-%(uuid)s", etc.
            info = {}
            # NOTE(russellb): Don't use self.iteritems() here, as it will
            # result in infinite recursion on the name property.
            for column in iter(orm.object_mapper(self).columns):
                key = column.name
                # prevent recursion if someone specifies %(name)s
                # %(name)s will not be valid.
                if key == 'name':
                    continue
                info[key] = self[key]
            try:
                base_name = CONF.instance_name_template % info
            except KeyError:
                base_name = self.uuid
        return base_name

    @property
    def _extra_keys(self):
        return ['name']

    user_id = Column(String(255))
    project_id = Column(String(255))

    image_ref = Column(String(255))
    kernel_id = Column(String(255))
    ramdisk_id = Column(String(255))
    hostname = Column(String(255))

    launch_index = Column(Integer)
    key_name = Column(String(255))
    key_data = Column(MediumText())

    power_state = Column(Integer)
    vm_state = Column(String(255))
    task_state = Column(String(255))

    memory_mb = Column(Integer)
    vcpus = Column(Integer)
    root_gb = Column(Integer)
    ephemeral_gb = Column(Integer)
    ephemeral_key_uuid = Column(String(36))

    # This is not related to hostname, above.  It refers
    #  to the nova node.
    host = Column(String(255))  # , ForeignKey('hosts.id'))
    # To identify the "ComputeNode" which the instance resides in.
    # This equals to ComputeNode.hypervisor_hostname.
    node = Column(String(255))

    # *not* flavorid, this is the internal primary_key
    instance_type_id = Column(Integer)

    user_data = Column(MediumText())

    reservation_id = Column(String(255))

    # NOTE(sbiswas7): 'scheduled_at' is still in the database
    # and can be removed in the future release.

    launched_at = Column(DateTime)
    terminated_at = Column(DateTime)

    # This always refers to the availability_zone kwarg passed in /servers and
    # provided as an API option, not at all related to the host AZ the instance
    # belongs to.
    availability_zone = Column(String(255))

    # User editable field for display in user-facing UIs
    display_name = Column(String(255))
    display_description = Column(String(255))

    # To remember on which host an instance booted.
    # An instance may have moved to another host by live migration.
    launched_on = Column(MediumText())

    # NOTE(jdillaman): locked deprecated in favor of locked_by,
    # to be removed in Icehouse
    locked = Column(Boolean)
    locked_by = Column(Enum('owner', 'admin'))

    os_type = Column(String(255))
    architecture = Column(String(255))
    vm_mode = Column(String(255))
    uuid = Column(String(36), nullable=False)

    root_device_name = Column(String(255))
    default_ephemeral_device = Column(String(255))
    default_swap_device = Column(String(255))
    config_drive = Column(String(255))

    # User editable field meant to represent what ip should be used
    # to connect to the instance
    access_ip_v4 = Column(types.IPAddress())
    access_ip_v6 = Column(types.IPAddress())

    auto_disk_config = Column(Boolean())
    progress = Column(Integer)

    # EC2 instance_initiated_shutdown_terminate
    # True: -> 'terminate'
    # False: -> 'stop'
    # Note(maoy): currently Samsara will always stop instead of terminate
    # no matter what the flag says. So we set the default to False.
    shutdown_terminate = Column(Boolean(), default=False)

    # EC2 disable_api_termination
    disable_terminate = Column(Boolean(), default=False)

    # OpenStack compute cell name.  This will only be set at the top of
    # the cells tree and it'll be a full cell name such as 'api!hop1!hop2'
    cell_name = Column(String(255))
    internal_id = Column(Integer)

    # Records whether an instance has been deleted from disk
    cleaned = Column(Integer, default=0)


class InstanceInfoCache(BASE, SamsaraBase):
    """Represents a cache of information about an instance
    """
    __tablename__ = 'instance_info_caches'
    __table_args__ = (
        schema.UniqueConstraint(
            "instance_uuid",
            name="uniq_instance_info_caches0instance_uuid"),)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # text column used for storing a json object of network data for api
    network_info = Column(MediumText())

    instance_uuid = Column(String(36), ForeignKey('instances.uuid'),
                           nullable=False)
    instance = orm.relationship(Instance,
                            backref=orm.backref('info_cache', uselist=False),
                            foreign_keys=instance_uuid,
                            primaryjoin=instance_uuid == Instance.uuid)


class InstanceExtra(BASE, SamsaraBase):
    __tablename__ = 'instance_extra'
    __table_args__ = (
        Index('instance_extra_idx', 'instance_uuid'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    instance_uuid = Column(String(36), ForeignKey('instances.uuid'),
                           nullable=False)
    numa_topology = orm.deferred(Column(Text))
    pci_requests = orm.deferred(Column(Text))
    flavor = orm.deferred(Column(Text))
    vcpu_model = orm.deferred(Column(Text))
    migration_context = orm.deferred(Column(Text))
    instance = orm.relationship(Instance,
                            backref=orm.backref('extra',
                                                uselist=False),
                            foreign_keys=instance_uuid,
                            primaryjoin=instance_uuid == Instance.uuid)


class InstanceTypes(BASE, SamsaraBase):
    """Represents possible flavors for instances.

    Note: instance_type and flavor are synonyms and the term instance_type is
    deprecated and in the process of being removed.
    """
    __tablename__ = "instance_types"

    __table_args__ = (
        schema.UniqueConstraint("flavorid", "deleted",
                                name="uniq_instance_types0flavorid0deleted"),
        schema.UniqueConstraint("name", "deleted",
                                name="uniq_instance_types0name0deleted")
    )

    # Internal only primary key/id
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    memory_mb = Column(Integer, nullable=False)
    vcpus = Column(Integer, nullable=False)
    root_gb = Column(Integer)
    ephemeral_gb = Column(Integer)
    # Public facing id will be renamed public_id
    flavorid = Column(String(255))
    swap = Column(Integer, nullable=False, default=0)
    rxtx_factor = Column(Float, default=1)
    vcpu_weight = Column(Integer)
    disabled = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)

class Migration(BASE, SamsaraBase):
    """Represents a running host-to-host migration."""
    __tablename__ = 'migrations'
    __table_args__ = (
        Index('migrations_instance_uuid_and_status_idx', 'deleted',
              'instance_uuid', 'status'),
        # MySQL has a limit of 3072 bytes for an multi-column index. This
        # index ends up being larger than that using the utf-8 encoding.
        # Limiting the index to the prefixes will keep it under the limit.
        # FIXME(johannes): Is it MySQL or InnoDB that imposes the limit?
        Index('migrations_by_host_nodes_and_status_idx', 'deleted',
              'source_compute', 'dest_compute', 'source_node', 'dest_node',
              'status', mysql_length={'source_compute': 100,
                                      'dest_compute': 100,
                                      'source_node': 100,
                                      'dest_node': 100}),
    )
    id = Column(Integer, primary_key=True, nullable=False)
    # NOTE(tr3buchet): the ____compute variables are instance['host']
    source_compute = Column(String(255))
    dest_compute = Column(String(255))
    # nodes are equivalent to a compute node's 'hypervisor_hostname'
    source_node = Column(String(255))
    dest_node = Column(String(255))
    # NOTE(tr3buchet): dest_host, btw, is an ip address
    dest_host = Column(String(255))
    old_instance_type_id = Column(Integer())
    new_instance_type_id = Column(Integer())
    instance_uuid = Column(String(36), ForeignKey('instances.uuid'))
    # TODO(_cerberus_): enum
    status = Column(String(255))
    migration_type = Column(Enum('migration', 'resize', 'live-migration',
                                 'evacuation'),
                            nullable=True)
    hidden = Column(Boolean, default=False)

    instance = orm.relationship("Instance", foreign_keys=instance_uuid,
                            primaryjoin='and_(Migration.instance_uuid == '
                                        'Instance.uuid, Instance.deleted == '
                                        '0)')
