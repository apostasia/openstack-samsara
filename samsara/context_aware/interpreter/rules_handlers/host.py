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

from samsara.context_aware.contexts import host as host_contexts
from samsara.context_aware.contexts import vm as vm_contexts
from samsara.common.utils import *

from samsara.context_aware.interpreter.rules_handlers import base

LOG = logging.getLogger(__name__)

rules_handler_opts = [
    cfg.IntOpt('compute_usage_time_frame_evaluation',
               default=60,
               help='Compute Usage time frame to evaluation (in seconds)'),
]
CONF = cfg.CONF
CONF.register_opts(rules_handler_opts, 'rules_handler')

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

        # Instantiate Contexts Handlers
        self.host_resources_usage_handler = host_contexts.HostResourcesUsage()

        # Instantiate Stored Host Compute Contexts Handlers
        self.stored_ctx_host = host_contexts.StoredHostComputeUsage()

        # Instantiate Host Info Handler
        self.host_info_handler = host_contexts.HostInfo()

        # # Get local contexts repository
        # self.ctx_repository = contexts_repository.LocalContextsRepository()

        # Get Global contexts repository
        # self.ctx_global_repository = contexts_repository.GlobalContextsRepository()

        # Contexts Stored in Local Repository
        self.ctx_host_compute_usage = host_contexts.StoredHostComputeUsage()

        # Get Host Info
        self.host_info = self.host_info_handler.getContext()

        # Time Frame
        self.time_frame = CONF.rules_handler.compute_usage_time_frame_evaluation

    @numeric_rule_variable
    def percentual_compute_resource_usage(self):

        host_resources_usage = self.host_resources_usage_handler.getContext()

        # Historical Compute Usage per periodo defined in time frame
        historical_compute_usage = self.stored_ctx_host.get_last_period_contexts(self.time_frame)

        # Calculate average compute usage
        compute_usage_avg = np.average(historical_compute_usage)

        percentual_compute_resource_usage = to_percentage(compute_usage_avg, self.host_info.compute_capacity)

        LOG.info('Compute Capacity in MIPS: %f', self.host_info.compute_capacity)
        LOG.info('Average Compute Usage in the last %d seconds in MIPS: %f', self.time_frame, compute_usage_avg)
        LOG.info('Average Host CPU Load in the last %d seconds: %f', self.time_frame, percentual_compute_resource_usage)

        return percentual_compute_resource_usage

# Action
class HostActions(BaseActions):
    """ Class with actions """

    @rule_action(params={"status":FIELD_TEXT})
    def notify_controller(self, status):
        LOG.info('Status: %s', status)
