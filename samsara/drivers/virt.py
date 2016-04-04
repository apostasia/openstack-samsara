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
from __future__ import print_function
from operator import sub
import time
import libvirt
import os,sys
import re
import pprint
from datetime import datetime
from lxml import etree,objectify
from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


libvirt_opts = [

    cfg.StrOpt('connection_uri',
               default='',
               help='Override the default libvirt URI '
                    '(which is dependent on virt_type)')
    # cfg.IntOpt('live_migration_bandwidth',
#                default=0,
#                help='Maximum bandwidth(in MiB/s) to be used during migration. '
#                     'If set to 0, will choose a suitable default. Some '
#                     'hypervisors do not support this feature and will return '
#                     'an error if bandwidth is not 0. Please refer to the '
#                     'libvirt documentation for further details')
    # cfg.StrOpt('sysinfo_serial',
#                default='auto',
#                choices=('none', 'os', 'hardware', 'auto'),
#                help='The data source used to the populate the host "serial" '
#                     'UUID exposed to guest in the virtual BIOS.')
    ]

CONF = cfg.CONF
CONF.register_opts(libvirt_opts, 'libvirt')

instances_vcpu_time = None

class LibvirtDriver(object):

    def __init__(self, uri=CONF.libvirt.connection_uri):

        self.uri = uri
        self.conn = self.get_connection()

    def get_connection(self):
        """Returns a connection to the hypervisor
           This method should be used to create and return a well
           configured connection to the hypervisor.
           :returns: a libvirt.virConnect object
        """
        global libvirt
        try:
            conn = libvirt.openReadOnly(self.uri)
            return conn
        except libvirt.libvirtError as ex:
                    LOG.exception("Connection to libvirt failed: %s", ex)



    def get_host_uuid(self):
        """Get a UUID from the host hardware
        Get a UUID for the host hardware reported by libvirt.
        This is typically from the SMBIOS data, unless it has
        been overridden in /etc/libvirt/libvirtd.conf. Return an object lxml
        """
        conn = self.get_connection()
        capabilities = objectify.fromstring(conn.getCapabilities())
        return capabilities.host.uuid


    def get_vm_usage_mips_percore(self,dom_id,interval=1):
        """ Return the usage mips per core/cpu for  an VM in the interval
        """

        host_compute_capacity_percore = get_max_mips_percore()
        host_maxfreq_percore          = get_max_freq_percore()
        host_currentfreq_percore      = get_current_freq_percore()
        vm_utilized_cputime_percore   = get_vbusytime_percore(dom_id,interval)

        usage_percore = []

        for compute_capacity,maxfreq,currentfreq,vm_utilized_cputime in zip(host_compute_capacity_percore,host_maxfreq_percore,host_currentfreq_percore,vm_utilized_cputime_percore):
            usage_percore.append(int((((currentfreq * compute_capacity)/maxfreq) * vm_utilized_cputime)))

        return usage_percore

    def get_vm_usage_perc(self,dom_id):
         host_compute_capacity_percore = get_max_mips_percore()
         vm_usage_mips_percore         = get_vm_usage_mips_percore(dom_id)

         usage_percore = []

         for host_compute_capacity,vm_usage_mips in zip(host_compute_capacity_percore,vm_usage_mips_percore):
             usage_percore.append((float(vm_usage_mips) * 100)/host_compute_capacity)

         return sum(usage_percore)

    def get_instance_allocated_memory(self,domain_id):

        conn = self.get_connection()
        dom  = conn.lookupByID(domain_id)
        return dom.maxMemory()

    def get_instance_uuid(self,domain_id):

        conn = self.get_connection()
        dom  = conn.lookupByID(domain_id)
        return dom.UUIDString()

    def list_instances(self):

        vm_list = []

        conn = self.get_connection()
        for domain_id in conn.listDomainsID():
           vm_list.append(conn.lookupByID(domain_id))

        return vm_list

    def get_active_instancesID(self):
        """ Return the active instaces ID list
        """
        return self.conn.listDomainsID()

    def get_active_instancesUUID(self):
        """ Return an list with the active instaces UUID
        """
        active_instances_uuid = []
        for instance_id in self.conn.listDomainsID():
            instance = self.conn.lookupByID(instance_id)
            active_instances_uuid.append(instance.UUIDString())

        return active_instances_uuid

    def get_vcpu_time_percore(self,domain_id):
        """ Return the busy time per core/cpu (in seconds) for an VM in the interval
        """
        conn = self.get_connection()
        dom  = conn.lookupByID(domain_id)

        #Get the cpu time intervals
        vcpu_time_percore  = [float(phys_cpu['cpu_time']) for phys_cpu in dom.getCPUStats(False,0)]

        return vcpu_time_percore

    def get_vcpu_time_instances(self):
        """ Return the vcpu time per core/cpu (in seconds) for all VMs
        """
        conn = self.get_connection()
        vcpu_times_percore  = {domain_id:self.get_vcpu_time_percore(domain_id) for domain_id in conn.listDomainsID()}
        return vcpu_times_percore

    def get_busytime_percore(self,domain_id):
        """ Return the busy time per core/cpu (in seconds) for an VM in the interval
        """
        conn = self.get_connection()
        dom  = conn.lookupByID(domain_id)

        global instances_vcpu_time
        if instances_vcpu_time == None:
            instances_vcpu_time = self.get_vcpu_time_instances()

        vcpu_time_t0 = [float(vcpu) for vcpu in instances_vcpu_time[domain_id]]
        vcpu_time_t1 = [float(phys_cpu['cpu_time']) for phys_cpu in dom.getCPUStats(False,0)]

        # compute the delta time for each cpu, convert nanoseconds (10^-9) to seconds and generate an list
        busytime_percore = [float(diff_time)/10000000000 for diff_time in map(sub,vcpu_time_t1,vcpu_time_t0)]

        return busytime_percore

    def update_vcpu_time_instances(self):
        """ Update the vcpu time per core/cpu (in seconds) for all VMs
        """
        global instances_vcpu_time
        instances_vcpu_time = self.get_vcpu_time_instances()
