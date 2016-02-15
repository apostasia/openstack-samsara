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

import numpy as np

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

LOG = logging.getLogger(__name__)

rules_handler_opts = [
    cfg.IntOpt('compute_usage_time_frame_evaluation',
               default=10,
               help='Compute Usage time frame to evaluation (in seconds)'),
]
CONF = cfg.CONF
CONF.register_opts(rules_handler_opts, 'rules_handler')


# Global Vars
host_resources_usage_ctx = None


class HostRulesHandler(base.BaseRulesHandler):
        """ Host Rules Handler """

        def __init__(self):
            # Load host rules
            rules = self.load_rules("host.json")

            super(HostRulesHandler,self).__init__(rules,HostVariables(), HostActions())


# Variables
class HostVariables(BaseVariables):
    """ Class with variables (or conditions) to be reasoning """

    def __init__(self):

        # Instantiates Host Contexts Handlers
        self.host_contexts_handler = host_contexts.HostContexts()

        # Get Host Info
        self.host_info = self.host_contexts_handler.get_host_info()

        # Time Frame
        self.time_frame = CONF.rules_handler.compute_usage_time_frame_evaluation

    @numeric_rule_variable
    def percentual_compute_resource_usage(self):

        global host_resources_usage_ctx

        # Get average 
        host_avg_resources_usage = self.host_contexts_handler.get_avg_resources_usage(self.time_frame)

        # Convert to percentual
        percentual_compute_resource_usage = to_percentage(host_avg_resources_usage.compute_usage_avg, self.host_info.compute_capacity)

        host_resources_usage_ctx = host_avg_resources_usage

        LOG.info('Compute Capacity in MIPS: %f', self.host_info.compute_capacity)

        LOG.info('Average Compute Usage in the last %d seconds in MIPS: %f', self.time_frame, host_avg_resources_usage.compute_usage_avg)

        LOG.info('Average Host CPU Load in the last %d seconds: %f', self.time_frame, percentual_compute_resource_usage)

        return percentual_compute_resource_usage

# Action
class HostActions(BaseActions):
    """ Class with actions """
    def __init__(self):

        # Samsara Global Controller RPC API
        self.global_controller = sgc_rpcapi.GlobalControllerAPI()

        # Instantiates Host Contexts Handlers
        self.host_contexts_handler = host_contexts.HostContexts()

        # Get Host Info
        self.host_info = self.host_contexts_handler.get_host_info()

    @rule_action(params={"situation":FIELD_TEXT})
    def notify_situation_to_controller(self, situation):

        global host_resources_usage_ctx

        LOG.info('Local Situation %s', situation)

        os_ctx = os_context.RequestContext()

        # Instantiate Host resources situation
        host_situation = situations.Situation('host_situation', situation, host_resources_usage_ctx._asdict())


        # Update Host Situation to Global Controller
        self.global_controller.update_host_situation(os_ctx,
                                                    self.host_info.hostname,
                                                    jsonutils.dumps(host_situation.get_situation()._asdict()))

        LOG.info('Situation Update')
