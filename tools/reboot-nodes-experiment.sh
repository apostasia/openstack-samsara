#!/bin/bash

nodes=(10.0.1.21 10.0.1.22 10.0.1.23 10.0.1.24)

echo "+--------------------------------------------------------------+"
echo "|             Despertando Nodos Físicos                        |"
echo "+--------------------------------------------------------------+"

for node in ${nodes[@]}
do
	echo "[-] Samsara compute node ($node): Reboot"
	sshpass -p lups999 ssh lups@$node 'sudo shutdown -r now'
done

echo "[+] Wait 3 minutes before restart experiments"
sleep 3m

for node in ${nodes[@]}
do
	echo "[-] Samsara compute node ($node): Verificando atividade"
	ping -c 5 $node
done
