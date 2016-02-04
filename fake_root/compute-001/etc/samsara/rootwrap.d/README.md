# Filters

Filters definition files contain lists of filters that nova-rootwrap will use to allow or deny a specific command. They are generally suffixed by .filters. Since they are in the trusted security path, they need to be owned and writeable only by the root user. Their location is specified in the rootwrap.conf file.

It uses an INI file format with a [Filters] section and several lines, each with a unique parameter name (different for each filter you define)
