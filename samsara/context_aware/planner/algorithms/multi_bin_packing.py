''' Partition a list into sublists whose sums don't exceed a maximum
    using a First Fit Decreasing algorithm. See
    http://www.ams.org/new-in-math/cover/bins1.html
    for a simple description of the method.
'''

from samsara.context_aware.contexts import cell

class BestFitDecreased(object):
    def generate_plan(self, hosts, instances, compute_threshold=0.7, memory_threshold=0.9):

        # Sort hosts in available compute increased order and filter fields
        hosts = [{'hostname': host.hostname, 'available_compute': host.available_compute * compute_threshold, 'available_memory': host.available_memory * memory_threshold} for host in sorted(hosts, key=lambda k: k.available_compute, reverse=True)]

        # Sort instances in used compute decreased order
        instances = sorted(instances, key=lambda k: k.used_compute)

        # Migration Plan
        plan = []

        for instance in instances:

            for host in hosts:

                # Try to fit item into a bin
                for instance in instances:
                    if  instance.used_compute <= host['available_compute'] and instance.used_memory <= host['available_memory']:

                        # Add Migration to plan
                        plan.append({'instance': instance.uuid, 'host_dest': host['hostname']})

                        # Decrement available resources
                        host['available_compute'] -= instance.used_compute
                        host['available_memory']  -= instance.used_memory

                        # Remove instances from instances list
                        instances.remove(instance)

        return plan
