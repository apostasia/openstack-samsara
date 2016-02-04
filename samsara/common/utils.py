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

from __future__ import division
from datetime import datetime
from datetime import timedelta
import time


def to_percentage(value, total):
    """ Calculate a percentual of value.
    Args:
        value (float): Value to percentual calculate
        total (float): Referencial max value
    Returns:
        percentage value between 0 and 1
    """
    try:
        percentage = ((float(value*100) / float(total)) / 1000)

        return float(percentage)
    except ZeroDivisionError:
        return None

def get_time_from_period(period=60):
    """ Get the time moment from period ago
    Args:
        period (int): Period value in seconds.
    Returns:
        timestamp in UTC format
    """
    time = datetime.now() - timedelta(seconds=period)
    return time.isoformat()
