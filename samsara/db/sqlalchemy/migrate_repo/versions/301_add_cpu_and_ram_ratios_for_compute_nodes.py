# Copyright (c) 2015 Red Hat, Inc.
# All Rights Reserved.
#
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


from sqlalchemy import Float, Column, MetaData, Table


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    cn = Table('compute_nodes', meta, autoload=True)
    shadow_cn = Table('shadow_compute_nodes', meta, autoload=True)
    cn.create_column(Column('ram_allocation_ratio', Float, nullable=True))
    cn.create_column(Column('cpu_allocation_ratio', Float, nullable=True))
    shadow_cn.create_column(Column('ram_allocation_ratio', Float))
    shadow_cn.create_column(Column('cpu_allocation_ratio', Float))
