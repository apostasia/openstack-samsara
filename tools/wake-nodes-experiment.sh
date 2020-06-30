#!/bin/bash

nodes=(10.0.1.21 10.0.1.22 10.0.1.23 10.0.1.24)

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

echo "[+] Wait 5 minutes before restart experiments"
sleep 3m

for node in ${nodes[@]}
do
	echo "[-] Samsara compute node ($node): Verificando atividade"
	ping -c 5 $node
done
