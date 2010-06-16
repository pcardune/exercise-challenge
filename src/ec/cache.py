import logging
import functools
import pickle

from ec.db import get_conn

_CACHE = {}

class SimpleCacheBackend(object):

    def __init__(self):
        self._CACHE = {}

    def set(self, key, val):
        logging.info("cache set: %r=%r", key, val)
        self._CACHE[key] = val

    def get(self, key, default=None):
        return self._CACHE.get(key, default)

    def remove(key):
        if key in self._CACHE:
            del self._CACHE[key]

    def multiremove(keys):
        for key in keys:
            self.remove(key)


class DatabaseCacheBackend(object):

    def set(self, key, val):
        db = get_conn()
        self.remove(key)
        db.execute("INSERT INTO cache (`key`, `value`) VALUES (%s, %s)",
                   key, pickle.dumps(val))

    def get(self, key, default=None):
        db = get_conn()
        r = db.get("SELECT * FROM cache WHERE `key`=%s", key)
        return pickle.loads(str(r.value)) if r else None

    def remove(self, key):
        db = get_conn()
        db.execute("DELETE FROM cache WHERE `key`=%s", key)

    def multiremove(self, keys):
        db = get_conn()
        db.execute("DELETE FROM cache WHERE `key` IN %s", keys)



BACKEND = SimpleCacheBackend()
BACKEND = DatabaseCacheBackend()

def set(key, val):
    return BACKEND.set(key, val)

def get(key, default=None):
    return BACKEND.get(key, default=default)

def remove(key):
    return BACKEND.remove(key)

def multiremove(keys):
    return BACKEND.multiremove(keys)


def key(func):
    """A cache key decorator.

    This will scope cache key functionss to the module they are in.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return "%s:%s" % (func.__module__,
                          func(*args, **kwargs))
    return wrapper

def invalidates(cachekey_func):
    """Generates a decorator that will invalidate cachekeys on success.

    Use like this:

      @invalidates(some_cache_key_func)
      def write_stuff_to_db(id, val):
          db.execute("UPDATE table SET value=%s WHERE id=%s", val, id)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            keys = list(cachekey_func(*args, **kwargs))
            multiremove(keys)
        return wrapper
    return decorator
