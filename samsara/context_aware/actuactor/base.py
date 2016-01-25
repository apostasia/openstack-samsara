# -*- coding: utf-8 -*-



class BaseActuator(object):
    """Base Class to Actuator """

    __metaclass__  = abc.ABCMeta

    def migrate_to(instance, host):
        pass

    def wake(self, host):
        pass

    def sleep(self, host):
        pass
