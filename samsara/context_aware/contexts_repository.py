# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import abc
import collections
import dataset
from datetime import datetime
import time

from oslo_config import cfg
from oslo_log import log as logging

import sqlalchemy

from samsara import config
from samsara.common.utils import *

from samsara.context_aware import base
from samsara.context_aware import sensors

contexts_repository_group = cfg.OptGroup('context_aware')

contexts_repository_opts = [
    cfg.StrOpt('local_repository', default='sqlite:////var/lib/samsara/contexts_local_repository.db',
                                    help=("Connection to Local Store")),

    cfg.StrOpt('global_repository', default='postgresql://samsara:samsara@controller/samsara',
                                                                help=("Connection to Contexts Global Repository Store"))
]

CONF = cfg.CONF
CONF.register_group(contexts_repository_group)
CONF.register_opts(contexts_repository_opts, contexts_repository_group)

LOG = logging.getLogger(__name__)


class ContextsRepository(base.BaseContextsRepository):

    def __init__(self, database_connection):
        self.repository = dataset.connect(database_connection)

    def _create_catalog(self,context_tag):
        self.repository[context_tag]

    def store_context(self,context_instance):
        "Store context on contexts repository"

        context_tag = type(context_instance).__name__

        # Store context
        self.repository[context_tag].insert(context_instance._asdict(),{'created_at':sqlalchemy.DateTime})

    def upsert_context(self,context_instance, keys):
        "Update or Insert context on contexts repository."

        context_tag = type(context_instance).__name__
        data = context_instance._asdict()
        types = {'created_at':sqlalchemy.DateTime}

        # Update or Insert context
        self.repository[context_tag].upsert(data, keys, types)

    def retrieve_context():
        "Retrives an stored context"
        raise NotImplementedError()

    def retrieve_all_context(self,context_tag):
        "Retrives all stored context"
        return self.repository[context_tag].all()

    def list_context_vars(self,context_tag):
        return self.repository[context_tag].columns

    def retrieve_last_n_contexts(self,context_tag,limit=10):
        return self.repository[context_tag].find(_limit=limit,order_by=['-created_at'])


class LocalContextsRepository(ContextsRepository):

    def __init__(self):

        super(LocalContextsRepository, self).__init__(CONF.context_aware.local_repository)

    def retrieve_last_contexts_from_period(self,context_tag,period=60):
        """ Retrive last context from of determined period"""

        time_value = get_time_from_period(period)

        query = "select * from %(context)s where datetime(created_at) > datetime('%(time)s')" % {"context": context_tag, "time": time_value}

        LOG.info('Query: %s', query)

        return self.repository.query(query)

class GlobalContextsRepository(ContextsRepository):

    def __init__(self):

        super(GlobalContextsRepository, self).__init__(CONF.context_aware.global_repository)

    def retrieve_last_contexts_from_period(self,context_tag,period=60):
        """ Retrive last context from of determined period"""

        time_value = get_time_from_period(period)

        query = "select * from %(context)s where datetime(created_at) > datetime('%(time)s')" % {"context": context_tag, "time": time_value}

        return self.repository.query(query)

    def store_situation(self, situation_instance):
        "Store situation on contexts repository"

        tag = type(situation_instance).__name__

        # Prepare situation data
        situation_tuple = situation_instance.related_context

        # Add situation description to end tuple
        situation_tuple.update(situation=situation_instance.description)

        # Store situation
        self.repository[tag].insert(situation_tuple, {'created_at':sqlalchemy.DateTime})
