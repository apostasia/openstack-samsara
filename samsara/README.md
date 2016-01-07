# READ ME



### Object Folder
Is an oslo.versionedobjects library requirement. From library docs:

> The oslo.versionedobjects library provides a generic versioned object model that is RPC-friendly, with inbuilt serialization, field typing, and remotable method calls. It can be used to define a data model within a project independent of external APIs or database schema for the purposes of providing upgrade compatibility across distributed services.  Objects reside in the <project>/objects directory and this is the place from which all objects should be imported. 

#### Using

Start the implementation by creating objects/base.py with these main classes:

* Create base object with the project namespace: 'oslo_versionedobjects.base.VersionedObject'

The VersionedObject base class for the project. You have to fill up the OBJ_PROJECT_NAMESPACE property. OBJ_SERIAL_NAMESPACE is used only for backward compatibility and should not be set in new projects.

* Create other base objects if needed class: 'oslo_versionedobjects.base.VersionedPersistentObject'
A mixin class for persistent objects can be created, defining repeated fields like created_at, updated_at. Fields are defined in the fields property (which is a dict). If objects were previously passed as dicts (a common situation), a oslo_versionedobjects.base.VersionedObjectDictCompat can be used as a mixin class to support dict operations.


### RootWrap


#### Add samsara user in sudoers file
```bash
samsara ALL = (root) NOPASSWD: /usr/bin/samsara-rootwrap /etc/samsara/rootwrap.conf *

```


#### Filters

Filters definition files contain lists of filters that nova-rootwrap will use to allow or deny a specific command. They are generally suffixed by .filters. Since they are in the trusted security path, they need to be owned and writeable only by the root user. Their location is specified in the rootwrap.conf file.

It uses an INI file format with a [Filters] section and several lines, each with a unique parameter name (different for each filter you define)


Referências: 
http://docs.openstack.org/developer/oslo.versionedobjects/index.html