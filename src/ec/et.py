from ec import cache
from ec import db
from ec.cache import cache_get

def dbget_all_exercise_types():
    return db.query("SELECT * FROM exercise_types")

@cache.key
def _get_all_exercise_types_cache_key():
    return "exercise_types"

@cache.key
def _get_exercise_type_cache_key(et_id):
    return "exercise_type:%s" % et_id

@cache.key
def _get_measure_for_exercise_type_cache_key(et_id):
    return "measure:exercise_type:%s" % et_id

@cache.key
def _get_measure_cache_key(measure_id):
    return "measure:%s" % measure_id

def get_all_exercise_types():
    return cache_get(_get_all_exercise_types_cache_key,
                     dbget_all_exercise_types)

def dbget_exercise_type(exercise_type_id):
    return db.get("SELECT * FROM exercise_types WHERE id=%s",
                  exercise_type_id)

def get_exercise_type(exercise_type_id):
    return cache.cache_get(_get_exercise_type_cache_key,
                           dbget_exercise_type,
                           args=(exercise_type_id,))

def create_exercise_type(name, description):
    cache.remove(_get_all_exercise_types_cache_key())
    return db.execute("INSERT INTO exercise_types "
                      "(name, description) VALUES "
                      "(%s, %s)", name, description)

def dbget_measures_for_exercise_type(exercise_type_id):
    return db.query("SELECT * FROM measures WHERE exercise_type_id=%s",
                    exercise_type_id)

def get_measures_for_exercise_type(exercise_type_id):
    return cache_get(_get_measure_for_exercise_type_cache_key,
                     dbget_measures_for_exercise_type,
                     args=(exercise_type_id,))

def dbget_measure(measure_id):
    return db.get("SELECT * FROM measures WHERE id=%s", measure_id)

def get_measure(measure_id):
    return cache.cache_get(_get_measure_cache_key,
                           dbget_measure,
                           args=(measure_id,))

