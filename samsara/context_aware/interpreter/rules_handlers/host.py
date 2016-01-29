from business_rules.engine import check_condition
from business_rules import export_rule_data
from business_rules.actions import rule_action
from business_rules.actions import BaseActions
from business_rules.variables import (BaseVariables,
                                      rule_variable,
                                      numeric_rule_variable,
                                      string_rule_variable,
                                      boolean_rule_variable,
                                      select_rule_variable,
                                      select_multiple_rule_variable)
from business_rules.fields import FIELD_TEXT, FIELD_NUMERIC, FIELD_SELECT
from oslo_log import log as logging

from samsara.context_aware.contexts import host as host_contexts
from samsara.context_aware.contexts import vm as vm_contexts
from samsara.common import utils

from samsara.context_aware.interpreter.rules_handlers import base

LOG = logging.getLogger(__name__)

# Variables
class HostVariables(BaseVariables):
    def __init__(self):
        # Instantiate Contexts Handlers
        self.host_resources_usage_handler = host_contexts.HostResourcesUsage()
        self.host_info_handler = host_contexts.HostInfo()

    @numeric_rule_variable
    def current_compute_resource_usage(self):
        host_info = self.host_info_handler.getContext()
        host_resources_usage = self.host_resources_usage_handler.getContext()

        current_compute_resource_usage = ( utils.to_percentage(host_resources_usage.compute_utilization,host_info.max_compute)/100)

        LOG.info('Load Host: %s', current_compute_resource_usage)

        return current_compute_resource_usage

# Action
class HostActions(BaseActions):

    @rule_action(params={"status":FIELD_TEXT})
    def notify_controller(self, status):
        LOG.info('Status: %s', status)

class HostRulesHandler(base.BaseRulesHandler):

        def __init__(self):
            # Load host rules
            rules = self.load_rules("host.json")
            super(HostRulesHandler,self).__init__(rules,HostVariables(), HostActions())
