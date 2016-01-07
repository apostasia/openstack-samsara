# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_log import log as logging
from sqlalchemy import Index, MetaData, Table

from nova.i18n import _LI

LOG = logging.getLogger(__name__)


INDEX_COLUMNS = ['deleted', 'allocated', 'updated_at']
INDEX_NAME = 'fixed_ips_%s_idx' % ('_'.join(INDEX_COLUMNS),)


def _get_table_index(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    table = Table('fixed_ips', meta, autoload=True)
    for idx in table.indexes:
        if idx.columns.keys() == INDEX_COLUMNS:
            break
    else:
        idx = None
    return meta, table, idx


def upgrade(migrate_engine):
    meta, table, index = _get_table_index(migrate_engine)
    if index:
        LOG.info(_LI('Skipped adding %s because an equivalent index'
                     ' already exists.'), INDEX_NAME)
        return
    columns = [getattr(table.c, col_name) for col_name in INDEX_COLUMNS]
    index = Index(INDEX_NAME, *columns)
    index.create(migrate_engine)
