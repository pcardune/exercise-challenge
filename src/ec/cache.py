import logging

_CACHE = {}

def set(key, val):
    logging.info("cache set: %r=%r", key, val)
    _CACHE[key] = val

def get(key, default=None):
    return _CACHE.get(key, default)
