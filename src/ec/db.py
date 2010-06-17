from tornado import database
from tornado.options import define, options

define("mysql_host", default="localhost")
define("mysql_db", default="exercise")
define("mysql_user", default="root")
define("mysql_passwd", default="")

def get_conn():
    return database.Connection(
        options.mysql_host,
        options.mysql_db,
        user=options.mysql_user,
        password=options.mysql_passwd)

def get(*args):
    return get_conn().get(*args)

def execute(*args):
    return get_conn().execute(*args)

def query(*args):
    return get_conn().query(*args)
