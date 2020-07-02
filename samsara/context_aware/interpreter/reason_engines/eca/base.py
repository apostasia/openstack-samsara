# -*- coding: utf-8 -*-
"""Base Rules Handler class.

"""
from business_rules.engine import check_condition
from business_rules import export_rule_data
from business_rules.actions import rule_action, BaseActions
from business_rules.variables import (BaseVariables,
                                      rule_variable,
                                      numeric_rule_variable,
                                      string_rule_variable,
                                      boolean_rule_variable,
                                      select_rule_variable,
                                      select_multiple_rule_variable)
from business_rules.fields import FIELD_TEXT, FIELD_NUMERIC, FIELD_SELECT
from business_rules import run_all
from business_rules import export_rule_data

from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils

from samsara.context_aware import contexts_repository

json_rules_files_dir_path_opt = cfg.StrOpt('rules_location_dir',
                                            default='/etc/samsara/rules/eca',
                                            help='Rules JSON files location dir.')

CONF = cfg.CONF
CONF.register_opt(json_rules_files_dir_path_opt)

LOG = logging.getLogger(__name__)

class BaseECAReasonEngine(object):
    """Base class to ECA Reason Engines"""

    def __init__(self, rules, variables, actions):

        self.rules     = rules
        self.variables = variables
        self.actions   = actions

    def reason(self):
            LOG.info('Reason rules')

            run_all(rule_list=self.rules,
                    defined_variables=self.variables,
                    defined_actions=self.actions
               )

    def load_rules(self, filename):
        """ Load rules file"""

        dir_path = CONF.rules_location_dir
        path = "{0}/{1}".format(dir_path,filename)

        LOG.info('Load host rules')
        with open(path, 'r') as f:
            rules = jsonutils.loads(f.read())

        return rules
