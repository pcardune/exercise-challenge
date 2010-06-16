from ec.db import get_conn, cache_get
from ec import cache

def dbget_all_exercise_types():
    db = get_conn()
    return db.query("SELECT * FROM exercise_types")

@cache.key
def _get_all_exercise_types_cache_key():
    return "exercise_types"

def get_all_exercise_types():
    return cache_get(_get_all_exercise_types_cache_key,
                     dbget_all_exercise_types)

def create_exercise_type(name, description):
    cache.remove(_get_all_exercise_types_cache_key())
    db = get_conn()
    return db.execute("INSERT INTO exercise_types "
                      "(name, description) VALUES "
                      "(%s, %s)", name, description)
