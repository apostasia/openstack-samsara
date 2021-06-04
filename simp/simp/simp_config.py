''''' simp configuration class '''''
from configparser import ConfigParser
import pathlib

config = ConfigParser()
config.read(pathlib.Path('config.ini'))

psql_samsara = {
    "host": config.get('psql_samsara', 'host'),
    "user": config.get('psql_samsara', 'user'),
    "password": config.get('psql_samsara', 'password'),
    "database":config.get('psql_samsara', 'database')
}

sqlite_samsara = {
    "path": config.get('sqlite_samsara', 'path')
}

timescale_simp = {
    "host": config.get('timescale_simp', 'host'),
    "user": config.get('timescale_simp', 'user'),
    "password": config.get('timescale_simp', 'password'),
    "database":config.get('timescale_simp', 'database')
}

use_anonymous = True