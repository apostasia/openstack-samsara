#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from migrate.changeset.constraint import ForeignKeyConstraint
from migrate import UniqueConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    cell_mappings = Table('cell_mappings', meta, autoload=True)
    instance_mappings = Table('instance_mappings', meta,
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('id', Integer, primary_key=True, nullable=False),
        Column('instance_uuid', String(length=36), nullable=False),
        Column('cell_id', Integer, nullable=False),
        Column('project_id', String(length=255), nullable=False),
        UniqueConstraint('instance_uuid',
            name='uniq_instance_mappings0instance_uuid'),
        Index('project_id_idx', 'project_id'),
        ForeignKeyConstraint(columns=['cell_id'],
            refcolumns=[cell_mappings.c.id]),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    # NOTE(mriedem): DB2 creates an index when a unique constraint is created
    # so trying to add a second index on the instance_uuid column will fail
    # with error SQL0605W, so omit the index in the case of DB2.
    if migrate_engine.name != 'ibm_db_sa':
        Index('instance_uuid_idx', instance_mappings.c.instance_uuid)

    instance_mappings.create(checkfirst=True)
