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
from oslo_config import cfg
from oslo_context import context as os_context
from oslo_serialization import jsonutils

from samsara.context_aware.contexts import host as host_contexts
from samsara.context_aware.contexts import vm as vm_contexts
from samsara.context_aware.situations import base as situations
from samsara.common.authenticate import *
from samsara.common.credentials import *
from samsara.common.utils import *

from samsara.context_aware.interpreter.rules_handlers import base
from samsara.global_controller import rpcapi as sgc_rpcapi

import time

LOG = logging.getLogger(__name__)

# rules_handler_opts = [
# ]
# CONF = cfg.CONF
# CONF.register_opts(rules_handler_opts, 'rules_handler')


# Global Vars
host_resources_usage_ctx = None


class CellRulesHandler(base.BaseRulesHandler):
        """ Cell Rules Handler """

        def __init__(self):
            # Load cell rules
            rules = self.load_rules("cell.json")

            super(CellRulesHandler,self).__init__(rules,CellVariables(), CellActions())


# Variables
class CellVariables(BaseVariables):
    """ Class with variables (or conditions) to be reasoning """

    @string_rule_variable
    def hosts_underload(self):
        print help(self)
        return "True"


    @numeric_rule_variable
    def hosts_underload_time(self):
        return 60

    @string_rule_variable
    def hosts_overload(self):
        return "True"

    @numeric_rule_variable
    def hosts_overload_time(self):
        return 60

# Action
class CellActions(BaseActions):
    """ Class with actions """
    # def __init__(self):
    #
    #     # Samsara Global Controller RPC API
    #     self.global_controller = sgc_rpcapi.GlobalControllerAPI()

    @rule_action()
    def start_consolidation(self):
        """ Invoke workload consolidation process"""

        LOG.info('Consolidation Request')
        # Request Consolidation to Global Controller
        #self.global_controller.consolidate_workload(os_ctx, controller_hostname="controller")


    @rule_action()
    def start_load_balance(self):
        """ Invoke workload balance process"""

        LOG.info('Load Balance Request')
        # Request Load Balance to Global Controller
        #self.global_controller.balance_workload(os_ctx, controller_hostname="controller")
