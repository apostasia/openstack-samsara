# -*- coding: utf-8 -*-

from __future__ import print_function

from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

class BaseActuator(object):
    """Base Class to Actuator """

    def get_root_helper(self):
        conf='/etc/samsara/rootwrap.conf'
        return 'sudo samsara-rootwrap %s' % conf

    def execute(self, *cmd, **kwargs):

        kwargs['root_helper'] = self.get_root_helper()
        kwargs['run_as_root'] = True

        result = processutils.execute(*cmd, **kwargs)

        LOG.debug('Execution completed, command line is "%s"', ' '.join(map(str, cmd)))

        LOG.debug('CMD Stdout is: "%s"' % result[0])
        LOG.debug('CMD Stderr is: "%s"' % result[1])

        return result

    def trycmd(self, *cmd, **kwargs):

        kwargs['root_helper'] = self.get_root_helper()
        kwargs['run_as_root'] = True

        result = processutils.trycmd(*cmd, **kwargs)
        return result
