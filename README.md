# OpenStack Samsara: An Energy Aware Architecture for VM Consolidation

Please feel here a long description which must be at least 3 lines wrapped on
80 cols, so that distribution package maintainers can use it in their packages.
Note that this is a hard requirement.

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/samsara
* Source: http://git.openstack.org/cgit/openstack/samsara
* Bugs: http://bugs.launchpad.net/openstack-samsara


## Instalation
-----------


* Build package:

python setup.py build

* Instalation

sudo python setup.py install

* Uninstall

sudo pip uninstall samsara



Features
--------

* TODO



## Development


### Prerequisites

#### Vagrant

* Download and Instalation

*  Vagrant Plugins:
    * Vagrant Reload Provisioner:
        - Repositório: https://github.com/aidanns/vagrant-reload
        `
        $ vagrant plugin install vagrant-reload
        `
    * Vagrant Reload Provisioner:
        - Repositório: https://github.com/emyl/vagrant-triggers
        `
        $ vagrant plugin install vagrant-reload
        `
    * vagrant-triggers

#### Support Tools


* DB Browser for SQLite: http://sqlitebrowser.org/

    ```bash
    $ sudo add-apt-repository ppa:linuxgndu/sqlitebrowser
    $ sudo apt-get update
    $ sudo apt-get dist-upgrade
    ```
* Ansible

	```bash
    $ sudo apt-get update
    $ sudo apt-get install software-properties-common
    $ sudo apt-add-repository ppa:ansible/ansible
    $ sudo apt-get update
    $ sudo apt-get install ansible
    ```

* PGAdmin3
	```bash
    $ sudo apt-get install pgadmin3
    ```

## Usando o OpenStack Samsara

#### Iniciando os Serviços

* Nos compute nodes:

1. Inicializando o coletor de contextos:
```bash
# Inicializando o Samsara Collector
$ sudo start samsara-collector
```
Arquivo de log: `tail -f /var/log/samsara/samsara-collector.log`

2. Inicializando o Gerenciador Local
```bash
# Inicializando o Samsara Local Manager
$ sudo start samsara-local-manager
```
Arquivo de log: `tail -f /var/log/samsara/samsara-local-manager.log`

* No Controller Node

1. Inicializando o Samsara Global Manager

    ```bash
    # Inicializando o Samsara Global Manager
    $ sudo start samsara-global-manager
    ```
    Arquivo de log: `tail -f /var/log/samsara/samsara-global-manager.log`

## TODO

* Trocar 'algorithms' por 'policies' na estrutura do Planner
* Analisar Ferramentas para Desenvolver uma API
    * http://raml.org/
    * http://docs.themoviedb.apiary.io/#
