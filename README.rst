===============================
samsara
===============================

OpenStack Samsara: An Energy Aware Architecture for VM Consolidation

Please feel here a long description which must be at least 3 lines wrapped on
80 cols, so that distribution package maintainers can use it in their packages.
Note that this is a hard requirement.

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/samsara
* Source: http://git.openstack.org/cgit/openstack/samsara
* Bugs: http://bugs.launchpad.net/openstack-samsara


Instalation
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


### Vagrant Plugins:
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

Support Tools
-------------

* DB Browser for SQLite: http://sqlitebrowser.org/

sudo add-apt-repository ppa:linuxgndu/sqlitebrowser
sudo apt-get update
sudo apt-get dist-upgrade

* Ansible

sudo apt-get update
sudo apt-get install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install ansible

* PGAdmin3
sudo apt-get install pgadmin3

