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

import numpy as np
import os
import sys

# This is a backport of the subprocess standard library module from Python 3.2 &
# 3.3 for use on Python 2. It includes bugfixes and some new features. On POSIX
# systems it is guaranteed to be reliable when used in threaded applications. It
# includes timeout support from Python 3.3 but otherwise matches 3.2’s API. It has
#  not been tested on Windows

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

class DMMDriver(object):

    def get_consumption(self, time_frame=5):

        # Run dmm command and get output
        output = subprocess.check_output(['sudo','multimetro',str(time_frame)])

        # Get samples from output
        samples = [sample.split(',') for sample in output.splitlines()]

        # Get m0 value
        m0 = np.mean([float(sample[1]) for sample in samples if sample[0]=='0'])

        # Get m1 value
        m1 = np.mean([float(sample[1]) for sample in samples if sample[0]=='1'])

        # Return power in watts
        return m0*m1
