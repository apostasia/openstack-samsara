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

"""
Componente responsável por representar uma situação
"""
import collections

from samsara.context_aware import base


class Situation(base.BaseSituation):
    """  """
    def __init__(self, tag, description, related_context=[]):
        self.tag = tag
        self.description = description
        self.related_context = related_context

    def get_situation(self):
        self.situation = collections.namedtuple(self.tag, ['description','related_context'])

        return self.situation(self.description, self.related_context)
