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

def cache_get(keyfunc, dbfunc, *args, **kwargs):
    from ec import cache
    key = keyfunc(*args, **kwargs)
    result = cache.get(key)
    if result is None:
        result = dbfunc(*args, **kwargs)
        cache.set(key, result)
    return result
