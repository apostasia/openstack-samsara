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

from samsara.context_aware.adaptation_engine.actuators.cell import CellActuator

from samsara.context_aware.contexts.cell import CellContexts
from samsara.context_aware.situations.base import Situation
from samsara.common.authenticate import *
from samsara.common.credentials import *
from samsara.common.utils import *

from samsara.context_aware.interpreter.reason_engines.eca import base
from samsara.context_aware.contexts_repository import GlobalContextsRepository

import time

LOG = logging.getLogger(__name__)

# rules_handler_opts = [
# ]
# CONF = cfg.CONF
# CONF.register_opts(rules_handler_opts, 'rules_handler')

class CellReasonEngine(base.BaseECAReasonEngine):
        """ Cell Rules Handler """
        def __init__(self):
            # Load cell rules
            rules = self.load_rules("cell.json")

            super(CellReasonEngine,self).__init__(rules,CellVariables(), CellActions())


# Variables
class CellVariables(BaseVariables):
    """ Class with variables (or conditions) to be reasoning """

    def __init__(self):
        # Instantiates Cell Contexts Handlers
        self.cell_contexts = CellContexts()


    @numeric_rule_variable
    def hosts_underload(self):
        """ Return underloaded hosts amount"""

        # Select underloaded or idle hosts from active hosts list
        hosts_underloaded = self.cell_contexts.get_hosts_by_situations(['underloaded','idle'])

        if not hosts_underloaded:
            return 0
        else:
            return len(hosts_underloaded)


    @numeric_rule_variable
    def hosts_underload_time(self):
        """ Return underloaded host period"""

        # Select underloaded or idle hosts from active hosts list
        hosts_underloaded = self.cell_contexts.get_hosts_by_situations(['underloaded','idle'])

        if hosts_underloaded:
            # Get underload period per host
            underload_period_per_host = [get_period_from_time(host['last_change_at'], host['created_at']) for host in hosts_underloaded]

            # Return greater than underload period
            LOG.info('Underload Period: %s', max(underload_period_per_host))

            return max(underload_period_per_host)

        else:
            return 0

    @numeric_rule_variable
    def hosts_overload(self):
        """ Return overloaded hosts amount"""

        # Get overloaded hosts
        hosts_overloaded = self.cell_contexts.get_overloaded_hosts()

        if not hosts_overloaded:
            return 0
        else:
            return len(hosts_overloaded.hosts)

    @numeric_rule_variable
    def hosts_overload_time(self):
        """ Return overloaded host period"""

        hosts_overloaded = self.cell_contexts.get_overloaded_hosts().hosts

        if hosts_overloaded:

            # Get overload period per host
            overload_period_per_host = [get_period_from_time(host['last_change_at'], host['created_at']) for host in hosts_overloaded]

            # Return greater than underload period
            greater_than_overload_period = max(overload_period_per_host)

            LOG.info('Overload Period: %s', greater_than_overload_period)

            return greater_than_overload_period

        else:
            return 0


# Action
class CellActions(BaseActions):
    """ Class with actions """
    def __init__(self):
        # Instantiates Cell Contexts Handlers
        self.cell_contexts = CellContexts()

        # Samsara Cell Actuator
        self.cell_actuator = CellActuator()

        # Samsara Global Contexts Repository
        self.global_ctx_repo = GlobalContextsRepository()

    @rule_action()
    def start_consolidation(self):
        """ Invoke workload consolidation process"""

        # Notify
        LOG.info('Cell Situation: Energy Inefficiency')
        self.notify_cell_situation("energy_inefficiency")

        # Invoke Adaptation Engine
        LOG.info('Request Consolidation to Samsara Adaptation Engine.')
        self.cell_actuator.consolidate_workload()

    @rule_action()
    def start_load_balance(self):
        """ Invoke workload balance process"""

        LOG.info('Cell Situation: SLA Violation')
        self.notify_cell_situation("sla_violation")

        # Request Load Balance Adaptation Engine
        LOG.info('Request Load Balance to Samsara Adaptation Engine.')
        self.cell_actuator.balance_workload()

    @rule_action(params={"situation_description":FIELD_TEXT})
    def notify_cell_situation(self, situation_description):

        cell_ctx = self.get_cell_contexts()
        self.set_cell_situation(situation_description, cell_ctx)

    def get_cell_contexts(self):

        cell_ctx_vars = dict()

        # Cell Hosts
        cell_ctx_vars['active_hosts']        = len(self.cell_contexts.get_active_hosts().hosts)
        cell_ctx_vars['inactive_hosts']      = len(self.cell_contexts.get_inactive_hosts().hosts)
        cell_ctx_vars['underloaded_hosts']   = len(self.cell_contexts.get_underloaded_hosts().hosts)
        cell_ctx_vars['overloaded_hosts']    = len(self.cell_contexts.get_overloaded_hosts().hosts)
        # cell_ctx_vars['energy_consumption']  = self.cell_contexts.get_cell_energy_consumption()
        cell_ctx_vars['created_at']          = datetime.utcnow().isoformat()

        return cell_ctx_vars

    def set_cell_situation(self, description, context_vars):

        # Instantiate Host resources situation
        cell_situation = Situation('cell_situation', description, context_vars)

        # Store Cell Situation
        self.global_ctx_repo.store_situation(cell_situation.get_situation())

        LOG.info('Store cell situation into global repository')
