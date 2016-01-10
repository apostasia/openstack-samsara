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

class BaseEntity(object):
    __metaclass__  = abc.ABCMeta

class BaseContext(object):
    __metaclass__  = abc.ABCMeta

    # self.tag          = ""
    # self.timestamp    = ""
    # self.context_vars = {}

    @abc.abstractmethod
    def getContext():
        "Return an tuple with context vars and values"
        raise NotImplementedError()
    def retrieve(self):
        "Retrives an stored context"
        raise NotImplementedError()

class BaseSituation(object):
    __metaclass__  = abc.ABCMeta

class BaseSensor(object):
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def read_value(self):
         """Returns the sensor value."""

class BaseContextsRepository(object):
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def store_context():
        "Store context on contexts repository"
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_context():
        "Retrives an stored context"
        raise NotImplementedError()


    class BaseContextAnalizer(object):
        __metaclass__  = abc.ABCMeta

        @abc.abstractmethod
        def store_context():
            "Store context on contexts repository"
            raise NotImplementedError()

        @abc.abstractmethod
        def retrieve_context():
            "Retrives an stored context"
            raise NotImplementedError()
