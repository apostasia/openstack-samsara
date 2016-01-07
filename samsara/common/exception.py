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

"""Samsara base exception handling.

SHOULD include dedicated exception logging.

"""

from oslo_config import cfg
from oslo_log import log as logging
import six
from six.moves import http_client

from samsara.openstack.common._i18n import _
from samsara.openstack.common._i18n import _LE


LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help=_('Used if there is a formatting error when generating '
                       'an exception message (a programming error). If True, '
                       'raise an exception; if False, use the unformatted '
                       'message.')),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


def _cleanse_dict(original):
    """Strip all admin_password, new_pass, rescue_pass keys from a dict."""
    return dict((k, v) for k, v in original.items() if "_pass" not in k)


class SamsaraException(Exception):
    """Base Samsara Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = http_client.INTERNAL_SERVER_ERROR
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.message % kwargs
            except Exception as e:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception(_LE('Exception in string format operation'))
                for name, value in kwargs.items():
                    LOG.error("%s: %s" % (name, value))

                if CONF.fatal_exception_format_errors:
                    raise e
                else:
                    # at least get the core message out if something happened
                    message = self.message

        super(SamsaraException, self).__init__(message)

    def __str__(self):
        """Encode to utf-8 then wsme api can consume it as well."""
        if not six.PY3:
            return unicode(self.args[0]).encode('utf-8')

        return self.args[0]

    def __unicode__(self):
        """Return a unicode representation of the exception message."""
        return unicode(self.args[0])

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return six.text_type(self)


class NotAuthorized(SamsaraException):
    message = _("Not authorized.")
    code = http_client.FORBIDDEN


class OperationNotPermitted(NotAuthorized):
    message = _("Operation not permitted.")


class Invalid(SamsaraException):
    message = _("Unacceptable parameters.")
    code = http_client.BAD_REQUEST


class Conflict(SamsaraException):
    message = _('Conflict.')
    code = http_client.CONFLICT


class TemporaryFailure(SamsaraException):
    message = _("Resource temporarily unavailable, please retry.")
    code = http_client.SERVICE_UNAVAILABLE


class NotAcceptable(SamsaraException):
    # TODO(deva): We need to set response headers in the API for this exception
    message = _("Request not acceptable.")
    code = http_client.NOT_ACCEPTABLE


class InvalidState(Conflict):
    message = _("Invalid resource state.")


class NodeAlreadyExists(Conflict):
    message = _("A node with UUID %(uuid)s already exists.")


class MACAlreadyExists(Conflict):
    message = _("A port with MAC address %(mac)s already exists.")


class ChassisAlreadyExists(Conflict):
    message = _("A chassis with UUID %(uuid)s already exists.")


class PortAlreadyExists(Conflict):
    message = _("A port with UUID %(uuid)s already exists.")


class InstanceAssociated(Conflict):
    message = _("Instance %(instance_uuid)s is already associated with a node,"
                " it cannot be associated with this other node %(node)s")


class DuplicateName(Conflict):
    message = _("A node with name %(name)s already exists.")


class InvalidUUID(Invalid):
    message = _("Expected a uuid but received %(uuid)s.")


class InvalidUuidOrName(Invalid):
    message = _("Expected a logical name or uuid but received %(name)s.")


class InvalidName(Invalid):
    message = _("Expected a logical name but received %(name)s.")


class InvalidIdentity(Invalid):
    message = _("Expected an uuid or int but received %(identity)s.")


class InvalidMAC(Invalid):
    message = _("Expected a MAC address but received %(mac)s.")


class InvalidStateRequested(Invalid):
    message = _('The requested action "%(action)s" can not be performed '
                'on node "%(node)s" while it is in state "%(state)s".')


class PatchError(Invalid):
    message = _("Couldn't apply patch '%(patch)s'. Reason: %(reason)s")


class InstanceDeployFailure(SamsaraException):
    message = _("Failed to deploy instance: %(reason)s")

# Cannot be templated as the error syntax varies.
# msg needs to be constructed when raised.
class InvalidParameterValue(Invalid):
    message = _("%(err)s")


class MissingParameterValue(InvalidParameterValue):
    message = _("%(err)s")


class Duplicate(SamsaraException):
    message = _("Resource already exists.")


class NotFound(SamsaraException):
    message = _("Resource could not be found.")
    code = http_client.NOT_FOUND


class DHCPLoadError(SamsaraException):
    message = _("Failed to load DHCP provider %(dhcp_provider_name)s, "
                "reason: %(reason)s")


class DriverNotFound(NotFound):
    message = _("Could not find the following driver(s): %(driver_name)s.")

class NoValidHost(NotFound):
    message = _("No valid host was found. Reason: %(reason)s")


class InstanceNotFound(NotFound):
    message = _("Instance %(instance)s could not be found.")


class NodeNotFound(NotFound):
    message = _("Node %(node)s could not be found.")


class NodeAssociated(InvalidState):
    message = _("Node %(node)s is associated with instance %(instance)s.")


class PortNotFound(NotFound):
    message = _("Port %(port)s could not be found.")


class FailedToUpdateDHCPOptOnPort(SamsaraException):
    message = _("Update DHCP options on port: %(port_id)s failed.")


class FailedToGetIPAddressOnPort(SamsaraException):
    message = _("Retrieve IP address on port: %(port_id)s failed.")


class InvalidIPv4Address(SamsaraException):
    message = _("Invalid IPv4 address %(ip_address)s.")


class FailedToUpdateMacOnPort(SamsaraException):
    message = _("Update MAC address on port: %(port_id)s failed.")


class ChassisNotFound(NotFound):
    message = _("Chassis %(chassis)s could not be found.")


class NoDriversLoaded(SamsaraException):
    message = _("Conductor %(conductor)s cannot be started "
                "because no drivers were loaded.")


class ConductorNotFound(NotFound):
    message = _("Conductor %(conductor)s could not be found.")


class ConductorAlreadyRegistered(SamsaraException):
    message = _("Conductor %(conductor)s already registered.")


class PowerStateFailure(InvalidState):
    message = _("Failed to set node power state to %(pstate)s.")


class ExclusiveLockRequired(NotAuthorized):
    message = _("An exclusive lock is required, "
                "but the current context has a shared lock.")


class NodeMaintenanceFailure(Invalid):
    message = _("Failed to toggle maintenance-mode flag "
                "for node %(node)s: %(reason)s")

class NodeInMaintenance(Invalid):
    message = _("The %(op)s operation can't be performed on node "
                "%(node)s because it's in maintenance mode.")


class ChassisNotEmpty(Invalid):
    message = _("Cannot complete the requested action because chassis "
                "%(chassis)s contains nodes.")


class IPMIFailure(SamsaraException):
    message = _("IPMI call failed: %(cmd)s.")


class AMTConnectFailure(SamsaraException):
    message = _("Failed to connect to AMT service.")


class AMTFailure(SamsaraException):
    message = _("AMT call failed: %(cmd)s.")

class SSHConnectFailed(SamsaraException):
    message = _("Failed to establish SSH connection to host %(host)s.")


class SSHCommandFailed(SamsaraException):
    message = _("Failed to execute command via SSH: %(cmd)s.")


class UnsupportedDriverExtension(Invalid):
    message = _('Driver %(driver)s does not support %(extension)s '
                '(disabled or not implemented).')

class KeystoneUnauthorized(SamsaraException):
    message = _("Not authorized in Keystone.")


class KeystoneFailure(SamsaraException):
    pass


class CatalogNotFound(SamsaraException):
    message = _("Service type %(service_type)s with endpoint type "
                "%(endpoint_type)s not found in keystone service catalog.")


class ServiceUnavailable(SamsaraException):
    message = _("Connection failed")


class Forbidden(SamsaraException):
    message = _("Requested OpenStack Images API is forbidden")


class BadRequest(SamsaraException):
    pass


class InvalidEndpoint(SamsaraException):
    message = _("The provided endpoint is invalid")


class CommunicationError(SamsaraException):
    message = _("Unable to communicate with the server.")


class HTTPForbidden(Forbidden):
    pass


class Unauthorized(SamsaraException):
    pass


class HTTPNotFound(NotFound):
    pass


class ConfigNotFound(SamsaraException):
    message = _("Could not find config at %(path)s")


class NodeLocked(Conflict):
    message = _("Node %(node)s is locked by host %(host)s, please retry "
                "after the current operation is completed.")


class NodeNotLocked(Invalid):
    message = _("Node %(node)s found not to be locked on release")


class NoFreeConductorWorker(TemporaryFailure):
    message = _('Requested action cannot be performed due to lack of free '
                'conductor workers.')
    code = http_client.SERVICE_UNAVAILABLE


class VendorPassthruException(SamsaraException):
    pass


class ConfigInvalid(SamsaraException):
    message = _("Invalid configuration file. %(error_msg)s")


class DriverLoadError(SamsaraException):
    message = _("Driver %(driver)s could not be loaded. Reason: %(reason)s.")


class PasswordFileFailedToCreate(SamsaraException):
    message = _("Failed to create the password file. %(error)s")


class IBootOperationError(SamsaraException):
    pass


class IloOperationError(SamsaraException):
    message = _("%(operation)s failed, error: %(error)s")


class IloOperationNotSupported(SamsaraException):
    message = _("%(operation)s not supported. error: %(error)s")


class DracRequestFailed(SamsaraException):
    pass


class DracClientError(DracRequestFailed):
    message = _('DRAC client failed. '
                'Last error (cURL error code): %(last_error)s, '
                'fault string: "%(fault_string)s" '
                'response_code: %(response_code)s')


class DracOperationFailed(DracRequestFailed):
    message = _('DRAC operation failed. Message: %(message)s')


class DracUnexpectedReturnValue(DracRequestFailed):
    message = _('DRAC operation yielded return value %(actual_return_value)s '
                'that is neither error nor expected %(expected_return_value)s')


class DracPendingConfigJobExists(SamsaraException):
    message = _('Another job with ID %(job_id)s is already created  '
                'to configure %(target)s. Wait until existing job '
                'is completed or is canceled')


class DracInvalidFilterDialect(SamsaraException):
    message = _('Invalid filter dialect \'%(invalid_filter)s\'. '
                'Supported options are %(supported)s')


class FailedToGetSensorData(SamsaraException):
    message = _("Failed to get sensor data for node %(node)s. "
                "Error: %(error)s")


class FailedToParseSensorData(SamsaraException):
    message = _("Failed to parse sensor data for node %(node)s. "
                "Error: %(error)s")


class FileSystemNotSupported(SamsaraException):
    message = _("Failed to create a file system. "
                "File system %(fs)s is not supported.")





class PathNotFound(SamsaraException):
    message = _("Path %(dir)s does not exist.")


class DirectoryNotWritable(SamsaraException):
    message = _("Directory %(dir)s is not writable.")


class WolOperationError(SamsaraException):
    pass

