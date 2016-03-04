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

import glob
import multiprocessing
import os
import re
import socket
import fcntl
import struct
import sys
import time

from datetime import datetime
from operator import sub

from lxml import etree, objectify

import psutil
from oslo_log import log as logging

# This is a backport of the subprocess standard library module from Python 3.2 &
# 3.3 for use on Python 2. It includes bugfixes and some new features. On POSIX
# systems it is guaranteed to be reliable when used in threaded applications. It
# includes timeout support from Python 3.3 but otherwise matches 3.2’s API. It has
#  not been tested on Windows

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


# Create function to get CLOCK_MONOTONIC time
# CLOCK_MONOTONIC represents the absolute elapsed wall-clock time since some
# arbitrary, fixed point in the past. It isn't affected by changes in the system
# time-of-day clock.
_timer = getattr(time, 'monotonic', time.time)
_global_timestamp = _timer()

class BareMetalDriver(object):
    def __init__(self):
        # Count cpu busytime init
        self._last_busytime_percore = self.get_cpu_time_percore()

    def get_number_cpu(self):
        """ Get cpu number
        """
        return multiprocessing.cpu_count()

    def get_cpu_time_percore(self):
        """Return a (user, system) representing  the
        accumulated process time, in seconds.
        This is the same as os.times() but per-process.
        """
        return [float(t[0])+float(t[2]) for t in psutil.cpu_times(percpu=True)]


    def get_max_mips_percore(self):
        """Return the max mips percore
        """
        mips_percore = []
        with open("/proc/cpuinfo") as f:
            for line in f:
                if not line.startswith("bogomips"):
                    continue
                parts = line.split()
                mips_percore.append(float(parts[2]))

        return mips_percore

    def get_max_mips(self):
        """Get max MIPS
           Return an int value in MIPS
        """
        return sum(self.get_max_mips_percore())


    def get_max_freq_percore(self):
        """Get max frequency CPU per core
           Return an int value in MHz
        """
        if glob.glob("/sys/devices/system/cpu/**/cpufreq"):
            return self.get_max_freq_percore_by_cpufreq()
        else:
            return self.get_max_freq_percore_by_cpuinfo()

    def get_max_freq_percore_by_cpufreq(self):
        """Get máx frequency CPU per core
           Return an int value in MHz
        """
        max_freq_percore = []

        cpus = [cpu for cpu in os.listdir("/sys/devices/system/cpu") if re.match(r'\b(cpu)(\d+)\b',cpu)]
        for cpu in cpus:
            cmd = ["cat","/sys/devices/system/cpu/%s/cpufreq/cpuinfo_max_freq" % (cpu)]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            max_freq_percore.append(float(process.stdout.read().strip("\n"))/1000) # In MHz
        return max_freq_percore

    def get_max_freq_percore_by_cpuinfo(self):
        """Get max frequency CPU per core by cpuinfo file
           Return an int value in MHz
        """
        max_freq_percore = []
        with open("/proc/cpuinfo") as f:
            for line in f:
                if not line.startswith("model name"):
                    continue
                max_freq_string = re.match(r'model name\s+:\s+.*@\s(\d+\.*\d*)(GHz|MHz)',line)

                """ Split value and unit"""
                # Value
                max_freq_value = float(max_freq_string.group(1))

                # Unit
                max_freq_unit = max_freq_string.group(2)

                # Convert do MHz
                if max_freq_unit == "GHz":
                    max_freq = max_freq_value * 1000
                # elif maglobal_timestamp = _timer()x_freq_unit == "MHz":
                #     max_freq_value * 1
                else:
                    max_freq = max_freq_value

                max_freq_percore.append(max_freq)

        return max_freq_percore

    def get_current_freq_percore(self):
        """Get current frequency CPU per core
           Return an int value in MHz
        """
        if glob.glob("/sys/devices/system/cpu/**/cpufreq"):
            return self.get_current_freq_percore_by_cpufreq()
        else:
            return self.get_current_freq_percore_by_cpuinfo()


    def get_current_freq_percore_by_cpufreq(self):
        """Get current frequency CPU per core by cpufreq file
           Return an int value in MHz
        """
        current_freq_percore = []
        cpus = [cpu for cpu in os.listdir("/sys/devices/system/cpu") if re.match(r'\b(cpu)(\d+)\b',cpu)]

        for cpu in cpus:
            cmd = ["cat","/sys/devices/system/cpu/%s/cpufreq/scaling_cur_freq" % (cpu)]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            current_freq_percore.append(float(process.stdout.read().strip("\n"))/1000) # In MHz
        return current_freq_percore

    def get_current_freq_percore_by_cpuinfo(self):
        """Get current frequency CPU per core by cpuinfo file
           Return an int value in MHz
        """
        # Fix - Because Vbox Tests
        #  Guest not scaling:
        # https://forums.virtualbox.org/viewtopic.php?f=1&t=49456
        correction_factor = 1.00193

        freq_percore = []
        with open("/proc/cpuinfo") as f:
            for line in f:
                if not line.startswith("cpu MHz"):
                    continue
                parts = line.split()
                current_freq = round(float(parts[3]) * correction_factor, 3)
                freq_percore.append(current_freq)

        return freq_percore

    def get_current_usage_mips(self):
         """Get current usage CPU in MIPS for all cores
            Return an int value in MIPS
         """
         return sum(self.get_usage_mips_percore())

    def _get_busytime_percore(self, interval=0.1):
        """ Get current busytime CPU - Alternative
            Return an float value in Seconds
        """

        cpu_time_t0  = self.get_cpu_time_percore()
        time.sleep(interval)

        cpu_time_t1  = self.get_cpu_time_percore()

        # compute the delta time for each cpu and generate an list
        busytime_percore = map(sub,cpu_time_t1, cpu_time_t0)

        return busytime_percore

    def get_busytime_percore(self):
        """ Get current busytime CPU
            Return an float value in Seconds
        """
        #global last_busytime_percore
        cpu_time_t0  = self._last_busytime_percore
        cpu_time_t1  = self.get_cpu_time_percore()

        # update global vars
        self._last_busytime_percore = cpu_time_t1

        # compute the delta cpu time for each cpu and generate an list
        busytime_percore = map(sub,cpu_time_t1,cpu_time_t0)

        return busytime_percore


    def get_usage_mips_percore(self):
        """Returns an list with usage mips percore"""

        maxmips_percore               = self.get_max_mips_percore()
        maxfreq_percore               = self.get_max_freq_percore()
        currentfreq_percore           = self.get_current_freq_percore()
        busytime_percore              = self.get_busytime_percore()


        usage_percore = []

        for max_mips, max_freq, current_freq, busytime in zip(maxmips_percore, maxfreq_percore, currentfreq_percore, busytime_percore):
            try:
                # Calculate current_compute_capacity in BogoMips
		        current_compute_capacity = (current_freq * max_mips) / max_freq

		        # Calculate current cpu usage in bogomips
		        current_usage = current_compute_capacity * busytime

		        #usage_core = (((current_freq * max_mips)/max_freq) * busytime)

                #usage_core = ((max_freq * busytime) * current_freq) / max_freq

            except ZeroDivisionError:
                # interval was too low
                usage_percore.append(0.0)
            else:
                usage_percore.append(round(current_usage, 1))

        return usage_percore

    def get_usage_percentual(self):
        """Returns an list with usage percentual"""

        maxmips    = self.get_max_mips()
        usage_mips = self.get_current_usage_mips()

        usage = round((usage_mips * 100) / maxmips)

        return usage

    def get_current_usage_mips(self):
        """Get current total usage CPU percentual
           Return an float value mips
        """
        try:

            total_mips = sum(self.get_usage_mips_percore())
            delta_time = self.get_delta_time()

            avg_mips = total_mips / delta_time

        except ZeroDivisionError:
            # interval was too low
            return 0.0
        else:
            return round(avg_mips, 2)


    def get_max_memory(self):
        """ Get max memory in MBytes
        """
        max_memory = int(psutil.virtual_memory().total)/1024**2
        return max_memory

    def get_used_memory(self):
        """ Get max memory in MBytes
        """
        used_memory = int(psutil.virtual_memory().used)/1024**2
        return used_memory

    def get_host_nic_speed(self,nic):
        """ Get current speed for informed NIC
            Return an int value in Mbits per second (Mb/s)
        """
        try:
            file_path = "/sys/class/net/%s/speed"  % (nic)
            nic_speed = open(file_path,"r").read().strip("\n")
            return int(nic_speed)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

    def get_host_nic_rx_tx_bytes(self,nic):
        """ Get current status of Rx and Tx for informed NIC
            Return an dict of int value in bytes
        """
        nic_status = {}

        try:
            nic_status ['rx'] = open("/sys/class/net/%s/statistics/rx_bytes" % (nic),"r").read().strip("\n")
            nic_status ['tx'] = open("/sys/class/net/%s/statistics/tx_bytes" % (nic),"r").read().strip("\n")

            return nic_status
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

    def get_hostname(self):
        """ Return Node Hostname
        """
        return socket.getfqdn()

    def get_mac_address(self, nic):
        """ Return HW address to specific NIC
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', nic[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

    def get_delta_time(self):
            global _global_timestamp

            timestamp_t0     = _global_timestamp
            timestamp_t1     = _timer()
            time_interval    = timestamp_t1 - timestamp_t0
            _global_timestamp = _timer()

            return time_interval
