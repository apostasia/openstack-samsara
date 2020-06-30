#!/bin/bash

BASE_DIR='/home/lups/experiments'
experiment_session_dir="session-$(date -u +%Y%m%d)"

unset adaptation_enable
while getopts ":a" opt; do
  case $opt in
    a) adaptation_enable=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

if [ $adaptation_enable ]
then
  echo "+--------------------------------------------------------------+"
  echo "|                  Adaptação Habilitada!                       |"
  echo "+--------------------------------------------------------------+"

  echo "[+] Copiando Arquivo de Regras da Célula"
  sudo cp /etc/samsara/rules/eca/samples/cell_adaptation_enable.json /etc/samsara/rules/eca/cell.json

  echo "[+] Ajustando Diretório das Amostras"
  samples_dir=$BASE_DIR"/adaptation_enable-nonrandom/"$experiment_session_dir


else
    echo "+--------------------------------------------------------------+"
    echo "|                  Adaptação Desabilitada!                     |"
    echo "+--------------------------------------------------------------+"

    echo "[+] Copiando Arquivo de Regras da Célula"
    sudo cp /etc/samsara/rules/eca/samples/cell_adaptation_disable.json /etc/samsara/rules/eca/cell.json

    echo "[+] Ajustando Diretório das Amostras"
    samples_dir=$BASE_DIR"/adaptation_disable-nonrandom/"$experiment_session_dir

fi

echo "[+] Criando Diretório das Amostras"
sudo mkdir -p $samples_dir
sudo chmod -R 777 $BASE_DIR

echo "+--------------------------------------------------------------+"
echo "|               Configurando Auth do OpenStack                 |"
echo "+--------------------------------------------------------------+"
# To use an OpenStack cloud you need to authenticate against the Identity
# service named keystone, which returns a **Token** and **Service Catalog**.
# The catalog contains the endpoints for all services the user/tenant has
# access to - such as Compute, Image Service, Identity, Object Storage, Block
# Storage, and Networking (code-named nova, glance, keystone, swift,
# cinder, and neutron).
#
# *NOTE*: Using the 2.0 *Identity API* does not necessarily mean any other
# OpenStack API is version 2.0. For example, your cloud provider may implement
# Image API v1.1, Block Storage API v2, and Compute API v2.0. OS_AUTH_URL is
# only for the Identity API served through keystone.
export OS_AUTH_URL=http://controller:35357/v3

# With the addition of Keystone we have standardized on the term **tenant**
# as the entity that owns the resources.
unset OS_TENANT_ID
unset OS_TENANT_NAME
unset OS_PROJECT_NAME
unset OS_PROJECT_DOMAIN_ID
unset OS_USER_DOMAIN_ID
unset OS_USERNAME

export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_ID=default
export OS_PROJECT_NAME=admin
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://controller:35357/v3


# In addition to the owning entity (tenant), OpenStack stores the entity
# performing the action as the **user**.
export OS_USERNAME="admin"

# With Keystone you pass the keystone password.
#echo "Please enter your OpenStack Password: "
#read -sr OS_PASSWORD_INPUT
#export OS_PASSWORD=$OS_PASSWORD_INPUT
export OS_PASSWORD="samsara"

# If your configuration has multiple regions, we set that information here.
# OS_REGION_NAME is optional and only valid in certain environments.
export OS_REGION_NAME="RegionOne"
# Don't leave a blank variable, unset it if it was empty
if [ -z "$OS_REGION_NAME" ]; then unset OS_REGION_NAME; fi


# Declarando o nodes do experimento
nodes=(10.0.1.21 10.0.1.22 10.0.1.23 10.0.1.24)

# Inicializa o data-collector em todos os compute nodes
#
echo "+--------------------------------------------------------------+"
echo "|                  Sincronizando nodos                         |"
echo "+--------------------------------------------------------------+"

echo "[+] controller"
sudo service ntp restart
date
echo  " "

echo "[+] compute-001"
sshpass -p lups999 ssh lups@10.0.1.21 'sudo /etc/init.d/ntp restart;date'
echo  " "

echo "[+] compute-002"
sshpass -p lups999 ssh lups@10.0.1.22 'sudo /etc/init.d/ntp restart;date'
echo  " "

echo "[+] compute-003"
sshpass -p lups999 ssh lups@10.0.1.23 'sudo /etc/init.d/ntp restart;date'
echo  " "

echo "[+] compute-004"
sshpass -p lups999 ssh lups@10.0.1.24 'sudo /etc/init.d/ntp restart;date'

# Executção das 15 rodadas de teste
for t in {1..15}
do
    echo "+--------------------------------------------------------------+"
    echo "|            Samsara: Parando os Serviços Locais               |"
    echo "+--------------------------------------------------------------+"


    for node in ${nodes[@]}
    do
    	echo "[-] Samsara compute node ($node): Parando Local Controller"
    	sshpass -p lups999 ssh lups@$node 'sudo stop samsara-local-controller'

        echo "[-] Samsara compute node ($node): Parando Coletor"
    	sshpass -p lups999 ssh lups@$node 'sudo stop samsara-collector'

    done

    # Cria vms no compute
    #
    echo "+--------------------------------------------------------------+"
    echo "|          Nova: Criando as Máquinas Virtuais                  |"
    echo "+--------------------------------------------------------------+"

    i=1
    network_id=$(nova network-list |grep net | cut -d"|" -f2)

    for i in {1..30}
    do
        nova boot --flavor m2.tiny \
            --image samsara-soul-2hours-nonrandom \
            --nic net-id=2449624e-6d38-40fa-b023-36261c7ed2fe \
            --security-group default \
            --key-name vilnei_at_lups \
            `printf samsara-soul-2hours-%02d $i` --poll

        instance_name=$(printf samsara-soul-2hours-%02d $i)
        nova stop $(nova list | grep $instance_name | cut -d"|" -f2)
    done

    sleep 15s
    nova list

    echo "[+] Espera 2 minutos para antes de iniciar as VMs"
    sleep 2m

    # Inicia as VMs nos computes
    #
    echo "+--------------------------------------------------------------+"
    echo "|           Nova: Iniciando as Máquinas Virtuais               |"
    echo "+--------------------------------------------------------------+"

    vms=$(nova list | grep samsara | cut -d"|" -f2)

    nova start $vms


    echo "[+] Espera 2 minutos para antes de iniciar os mecanismos do Samsara"
    sleep 2m

    echo "+--------------------------------------------------------------+"
    echo "|           Samsara: Iniciando Global Controller                |"
    echo "+--------------------------------------------------------------+"

    sudo start samsara-global-controller
    sudo start samsara-cell-collector

    echo "+--------------------------------------------------------------+"
    echo "|           Samsara: Iniciando os Serviços Locais              |"
    echo "+--------------------------------------------------------------+"

    for node in ${nodes[@]}
    do
    	echo "[+] Samsara compute node ($node): Iniciando Local Controller"
    	sshpass -p lups999 ssh lups@$node 'sudo start samsara-local-controller'

        echo "[+] Samsara compute node ($node): Iniciando Coletor"
    	sshpass -p lups999 ssh lups@$node 'sudo start samsara-collector'


    done

    echo "+--------------------------------------------------------------+"
    echo "|           Experimento: Status                                |"
    echo "+--------------------------------------------------------------+"

    nova list

    START_EXPERIMENT_AT=$(date -u +%Y-%m-%dT%H:%M:%S)

    CURRENT_TIME=$(date -u)
    PREV_LOCAL=$(date -d "now 120 minutes")
    PREV_UTC=$(date -u -d "now 120 minutes")

    echo "Rodada $t"
    echo "Relógio Atual (UTC): $CURRENT_TIME"
    echo "Previsão de término (Local): $PREV_LOCAL"
    echo "Previsão de término (UTC): $PREV_UTC"

    echo "[+] Make a Coffe. Much Coffe ;)"

    # Wait 120 minutes
    sleep 120m

    # Register end experiment
    END_EXPERIMENT_AT=$(date -u +%Y-%m-%dT%H:%M:%S)

    # Write round, start, end of experiment
    sudo su -c "printf '%s\n' $t $START_EXPERIMENT_AT $END_EXPERIMENT_AT | paste -sd ',' >> $samples_dir/experiment-start_end.csv"


    # Estados das VMs ao final da Rodada
    hosts=(compute-001 compute-002 compute-003 compute-004)
    for host in ${hosts[@]}
    do
        sudo su -c "printf '[*] Host %s at %s round\n' $host $t >> $samples_dir/vms_status.log"
        nova list --host $host | sudo tee -a $experiment_session_dir/vms_status.log > /dev/null
    done


    echo "+--------------------------------------------------------------+"
    echo "|           Samsara: Parando Global Controller                 |"
    echo "+--------------------------------------------------------------+"

    sudo stop samsara-global-controller
    sudo stop samsara-cell-collector

    echo "+--------------------------------------------------------------+"
    echo "|             Despertando Nodos Físicos                        |"
    echo "+--------------------------------------------------------------+"

    echo "[+] Wake compute-001"
    sudo /usr/bin/wakeonlan 74:86:7a:df:ac:16

    echo "[+] Wake compute-002"
    sudo /usr/bin/wakeonlan 74:86:7a:df:99:aa

    echo "[+] Wake compute-003"
    sudo /usr/bin/wakeonlan 74:86:7a:df:9b:24

    echo "[+] Wake compute-004"
    sudo /usr/bin/wakeonlan 74:86:7a:df:ab:da

    echo "[+] Wait 3 minutes before restart experiments"
    sleep 3m

    echo "+--------------------------------------------------------------+"
    echo "|            Samsara: Parando os Serviços Locais               |"
    echo "+--------------------------------------------------------------+"


    for node in ${nodes[@]}
    do
    	echo "[-] Samsara compute node ($node): Parando Local Controller"
    	sshpass -p lups999 ssh lups@$node 'sudo stop samsara-local-controller'

        echo "[-] Samsara compute node ($node): Parando Coletor"
    	sshpass -p lups999 ssh lups@$node 'sudo stop samsara-collector'


    done

    echo "+--------------------------------------------------------------+"
    echo "|             Exportando as Tabelas                            |"
    echo "+--------------------------------------------------------------+"


    TABLES=(cell_energy_consumption cell_events cell_situation historical_host_situation host_events host_info host_resources_usage host_native_resources_usage host_situation migration_events)

    round_samples_dir=$samples_dir"/"$START_EXPERIMENT_AT"-"$END_EXPERIMENT_AT

    sudo mkdir -p $round_samples_dir

    sudo chmod -R 777 $BASE_DIR

    for i in ${TABLES[@]}; do
            sudo su - postgres -c "psql -d samsara -c \"COPY $i TO '$round_samples_dir/$i.csv' DELIMITER ',' CSV HEADER;\""
    done

    # Move file with start and end experiment times
    mv $samples_dir/experiment-start_end.csv $round_samples_dir

    # Move file with vm status
    mv $samples_dir/vms_status.csv $round_samples_dir


    echo "+--------------------------------------------------------------+"
    echo "|                  Clean Samsara                               |"
    echo "+--------------------------------------------------------------+"

    echo "[-] Deletando Máquinas Virtuais"

    before_active_vms=$(nova list | grep samsara | cut -d"|" -f3 |wc -l)

    vms=$(nova list | grep samsara | cut -d"|" -f2)
    VMS_LIST=($vms)

    for vm in ${VMS_LIST[@]}
    do
    	nova reset-state --active $vm 1> /dev/null
    	nova delete $vm 1> /dev/null
    done

    actual_active_vms=$(nova list | grep samsara | cut -d"|" -f3 |wc -l)

    echo "[+] VMS ativas (antes)"
    echo $before_active_vms

    echo "[+] VMS ativas (agora)"
    echo $actual_active_vms

    nova list


    for node in ${nodes[@]}
    do
    	echo "[-] Samsara compute node ($node): Removendo Bases Locais"
    	sshpass -p lups999 ssh lups@$node 'sudo rm -f /var/lib/samsara/contexts_local_repository.db'
    done

    echo "[-] Samsara: Limpando Base de Dados do Global Controller"
    sudo su - postgres -c "psql -d samsara -c \"TRUNCATE cell_energy_consumption, cell_events, cell_situation, historical_host_situation, host_events, host_info, host_resources_usage, host_native_resources_usage, host_situation, migration_events RESTART IDENTITY;\""

    done
