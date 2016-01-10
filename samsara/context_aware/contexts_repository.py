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
from oslo_log import log

import sqlalchemy

from samsara import config

from samsara.context_aware import base
from samsara.context_aware import sensors
from samsara.context_aware import contexts


contexts_repository_group = cfg.OptGroup('contexts_repository')

contexts_repository_opts = [
    cfg.StrOpt('local_storage', default='sqlite:////var/lib/samsara/contexts_repository.db',
                                    help=("Connection to Local Store")),

    cfg.StrOpt('global_storage', default='sqlite:////var/lib/samsara/contexts_repository.db',
                                                                help=("Connection to Local Store"))
]

CONF = cfg.CONF
CONF.register_group(contexts_repository_group)
CONF.register_opts(contexts_repository_opts, contexts_repository_group)


class LocalContextsRepository(base.BaseContextsRepository):

    def __init__(self):
        self.repository = dataset.connect(CONF.contexts_repository.local_storage)

    def _create_catalog(self,context_tag):
        self.repository[context_tag]

    def store_context(self,context_instance):
        "Store context on contexts repository"

        context_tag = type(context_instance).__name__

        # Store context
        self.repository[context_tag].insert(context_instance._asdict(),{'created_at':sqlalchemy.DateTime})

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
