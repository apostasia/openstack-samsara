#!/bin/bash

echo "+--------------------------------------------------------------+"
echo "|             Exportando as Tabelas                            |"
echo "+--------------------------------------------------------------+"


TABLES=(cell_energy_consumption cell_events cell_situation historical_host_situation host_events host_info host_resources_usage host_situation migration_events)

BASE_DIR='/home/lups/experiments'

DIR=$BASE_DIR'/'$(date -u +%Y-%m-%dT%H:%M:%S)

sudo mkdir -p $DIR

sudo chmod -R 777 $BASE_DIR

for i in ${TABLES[@]}; do
        sudo su - postgres -c "psql -d samsara -c \"COPY $i TO '$DIR/$i.csv' DELIMITER ',' CSV HEADER;\""
done

# Move file with start and end experiment times
mv $BASE_DIR/experiment-start_end.csv $DIR
