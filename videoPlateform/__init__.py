import pymysql
from .mongo_setup import mongo_global_init

pymysql.install_as_MySQLdb()