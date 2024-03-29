# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools
import samsara.cmd.collector
import samsara.cmd.global_controller
import samsara.cmd.local_controller

import samsara.common.baserpc
import samsara.common.exception
import samsara.paths
import samsara.common.service
import samsara.utils

def list_opts():
    return [
        ('DEFAULT',
         itertools.chain(
            samsara.paths.path_opts,
            samsara.common.service.service_opts,
         )),
        # ('database', samsara.db.sqlalchemy.api.oslo_db_options.database_opts),
        ('upgrade_levels',
         itertools.chain(
             [samsara.common.baserpc.rpcapi_cap_opt],
         )),
]
