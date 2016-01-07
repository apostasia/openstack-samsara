import sys
import socket

from oslo_config import cfg
from oslo_service import periodic_task
from oslo_service import service
from oslo_context import context
from oslo_log import log as log


# service_opts = [
#     cfg.IntOpt('periodic_interval',
#                default=60,
#                help=_('Seconds between running periodic tasks.')),
#     cfg.StrOpt('host',
#                default=socket.getfqdn(),
#                help=_('Name of this node.  This can be an opaque identifier. '
#                       'It is not necessarily a hostname, FQDN, or IP address. '
#                       'However, the node name must be valid within '
#                       'an AMQP key, and if using ZeroMQ, a valid '
#                       'hostname, FQDN, or IP address.')),
# ]

CONF = cfg.CONF

# CONF.register_opts(service_opts)

LOG = log.getLogger(__name__)

class Service(service.ServiceBase):
    
    def __init__(self, *args, **kwargs):
        super(Service, self).__init__()
        
        self.collector = Collector(CONF)
        
    def start(self):
        pass

    def wait(self):
        pass

    def stop(self):
        pass

    def reset(self):
        logging.setup(CONF, 'samsara')
        
    def periodic_tasks(self, raise_on_error=True):
        """Tasks to be run at a periodic interval."""
        ctxt = context.get_admin_context()
        return self.collector.periodic_tasks(ctxt, raise_on_error=raise_on_error)

class Collector(periodic_task.PeriodicTasks):
    
    def __init__(self, conf):
        super(Collector, self).__init__(conf)
        self.add_periodic_task(self.print_music)
    
    def periodic_tasks(self, context, raise_on_error=True):
        """Periodic tasks are run at pre-specified interval."""
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)
    
    @periodic_task.periodic_task(spacing=10, run_immediately=True, name="VacaFinal" )
    def print_music(self,context):
        LOG.info("FinalCowDown")
       
def process_launcher():
    return service.ProcessLauncher(CONF)


# NOTE(vish): the global launcher is to maintain the existing
#             functionality of calling service.serve +
#             service.wait
_launcher = None


def serve(server, workers=None):
    global _launcher
    if _launcher:
        raise RuntimeError(_('serve() can only be called once'))

    _launcher = service.launch(CONF, server, workers=workers)
    
def wait():
    _launcher.wait()    
        
    
def main():
    
    
    CONF(default_config_files=['/home/vagrant/samsara/samsara/conf/samsara.conf'])
    server = Service(CONF)
    server.periodic_tasks()
    serve(server, workers=3)
    wait()

    

if __name__ == "__main__":
    sys.exit(main()) 

        