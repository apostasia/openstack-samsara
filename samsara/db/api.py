# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""Defines interface for DB access.

Functions in this module are imported into the nova.db namespace. Call these
functions from nova.db namespace, not the nova.db.api namespace.

All functions in this module return objects that implement a dictionary-like
interface. Currently, many of these objects are sqlalchemy objects that
implement a dictionary interface. However, a future goal is to have all of
these objects be simple dictionaries.

"""

from oslo_config import cfg
from oslo_db import concurrency
from oslo_log import log as logging

# from nova.cells import rpcapi as cells_rpcapi
# from nova.i18n import _LE


db_opts = [
    cfg.BoolOpt('enable_new_services',
                default=True,
                help='Services to be added to the available pool on create'),
    cfg.StrOpt('instance_name_template',
               default='instance-%08x',
               help='Template string to be used to generate instance names'),
    cfg.StrOpt('snapshot_name_template',
               default='snapshot-%s',
               help='Template string to be used to generate snapshot names'),
]

CONF = cfg.CONF
CONF.register_opts(db_opts)

_BACKEND_MAPPING = {'sqlalchemy': 'nova.db.sqlalchemy.api'}


IMPL = concurrency.TpoolDbapiWrapper(CONF, backend_mapping=_BACKEND_MAPPING)

LOG = logging.getLogger(__name__)

# The maximum value a signed INT type may have
MAX_INT = 0x7FFFFFFF

###################


def constraint(**conditions):
    """Return a constraint object suitable for use with some updates."""
    return IMPL.constraint(**conditions)


def equal_any(*values):
    """Return an equality condition object suitable for use in a constraint.

    Equal_any conditions require that a model object's attribute equal any
    one of the given values.
    """
    return IMPL.equal_any(*values)


def not_equal(*values):
    """Return an inequality condition object suitable for use in a constraint.

    Not_equal conditions require that a model object's attribute differs from
    all of the given values.
    """
    return IMPL.not_equal(*values)


###################


def service_destroy(context, service_id):
    """Destroy the service or raise if it does not exist."""
    return IMPL.service_destroy(context, service_id)


def service_get(context, service_id, use_slave=False):
    """Get a service or raise if it does not exist."""
    return IMPL.service_get(context, service_id,
                            use_slave=use_slave)


def service_get_by_host_and_topic(context, host, topic):
    """Get a service by hostname and topic it listens to."""
    return IMPL.service_get_by_host_and_topic(context, host, topic)


def service_get_by_host_and_binary(context, host, binary):
    """Get a service by hostname and binary."""
    return IMPL.service_get_by_host_and_binary(context, host, binary)


def service_get_all(context, disabled=None):
    """Get all services."""
    return IMPL.service_get_all(context, disabled)


def service_get_all_by_topic(context, topic):
    """Get all services for a given topic."""
    return IMPL.service_get_all_by_topic(context, topic)


def service_get_all_by_binary(context, binary):
    """Get all services for a given binary."""
    return IMPL.service_get_all_by_binary(context, binary)


def service_get_all_by_host(context, host):
    """Get all services for a given host."""
    return IMPL.service_get_all_by_host(context, host)


def service_get_by_compute_host(context, host, use_slave=False):
    """Get the service entry for a given compute host.

    Returns the service entry joined with the compute_node entry.
    """
    return IMPL.service_get_by_compute_host(context, host,
                                            use_slave=use_slave)


def service_create(context, values):
    """Create a service from the values dictionary."""
    return IMPL.service_create(context, values)


def service_update(context, service_id, values):
    """Set the given properties on a service and update it.

    Raises NotFound if service does not exist.

    """
    return IMPL.service_update(context, service_id, values)


###################


def compute_node_get(context, compute_id):
    """Get a compute node by its id.

    :param context: The security context
    :param compute_id: ID of the compute node

    :returns: Dictionary-like object containing properties of the compute node

    Raises ComputeHostNotFound if compute node with the given ID doesn't exist.
    """
    return IMPL.compute_node_get(context, compute_id)


def compute_nodes_get_by_service_id(context, service_id):
    """Get a list of compute nodes by their associated service id.

    :param context: The security context
    :param service_id: ID of the associated service

    :returns: List of dictionary-like objects, each containing properties of
              the compute node, including its corresponding service and
              statistics

    Raises ServiceNotFound if service with the given ID doesn't exist.
    """
    return IMPL.compute_nodes_get_by_service_id(context, service_id)


def compute_node_get_by_host_and_nodename(context, host, nodename):
    """Get a compute node by its associated host and nodename.

    :param context: The security context (admin)
    :param host: Name of the host
    :param nodename: Name of the node

    :returns: Dictionary-like object containing properties of the compute node,
              including its statistics

    Raises ComputeHostNotFound if host with the given name doesn't exist.
    """
    return IMPL.compute_node_get_by_host_and_nodename(context, host, nodename)


def compute_node_get_all(context):
    """Get all computeNodes.

    :param context: The security context

    :returns: List of dictionaries each containing compute node properties
    """
    return IMPL.compute_node_get_all(context)


def compute_node_get_all_by_host(context, host, use_slave=False):
    """Get compute nodes by host name

    :param context: The security context (admin)
    :param host: Name of the host

    :returns: List of dictionaries each containing compute node properties
    """
    return IMPL.compute_node_get_all_by_host(context, host, use_slave)


def compute_node_search_by_hypervisor(context, hypervisor_match):
    """Get compute nodes by hypervisor hostname.

    :param context: The security context
    :param hypervisor_match: The hypervisor hostname

    :returns: List of dictionary-like objects each containing compute node
              properties
    """
    return IMPL.compute_node_search_by_hypervisor(context, hypervisor_match)


def compute_node_create(context, values):
    """Create a compute node from the values dictionary.

    :param context: The security context
    :param values: Dictionary containing compute node properties

    :returns: Dictionary-like object containing the properties of the created
              node, including its corresponding service and statistics
    """
    return IMPL.compute_node_create(context, values)


def compute_node_update(context, compute_id, values):
    """Set the given properties on a compute node and update it.

    :param context: The security context
    :param compute_id: ID of the compute node
    :param values: Dictionary containing compute node properties to be updated

    :returns: Dictionary-like object containing the properties of the updated
              compute node, including its corresponding service and statistics

    Raises ComputeHostNotFound if compute node with the given ID doesn't exist.
    """
    return IMPL.compute_node_update(context, compute_id, values)


def compute_node_delete(context, compute_id):
    """Delete a compute node from the database.

    :param context: The security context
    :param compute_id: ID of the compute node

    Raises ComputeHostNotFound if compute node with the given ID doesn't exist.
    """
    return IMPL.compute_node_delete(context, compute_id)


def compute_node_statistics(context):
    """Get aggregate statistics over all compute nodes.

    :param context: The security context

    :returns: Dictionary containing compute node characteristics summed up
              over all the compute nodes, e.g. 'vcpus', 'free_ram_mb' etc.
    """
    return IMPL.compute_node_statistics(context)


###################
