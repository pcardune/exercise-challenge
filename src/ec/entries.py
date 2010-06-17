from ec import db
from ec import cache

@cache.key
def _get_entries_for_user_cache_key(uid):
    return "entries:%s" % uid

@cache.key
def _get_data_points_for_entry(entry_id):
    return "data_points:%s" % entry_id

def dbget_entries_for_user(uid):
    return db.query("SELECT * FROM entries WHERE user_id=%s", uid)

def get_entries_for_user(uid):
    return cache.cache_get(_get_entries_for_user_cache_key,
                           dbget_entries_for_user,
                           uid)

def create_entry(uid, date, exercise_type_id):
    cache.remove(_get_entries_for_user_cache_key(uid))
    return db.execute("INSERT INTO entries "
                      "(user_id, date, exercise_type) VALUES "
                      "(%s, %s, %s)",
                      uid, date, exercise_type_id)

def dbget_data_points_for_entry(entry_id):
    return db.query("SELECT * FROM data_points WHERE entry_id=%s", entry_id)

def get_data_points_for_entry(entry_id):
    return cache.cache_get(_get_data_points_for_entry,
                           dbget_data_points_for_entry,
                           entry_id)

def create_data_point(entry_id, measure_id, value):
    cache.remove(_get_data_points_for_entry(entry_id))
    return db.execute("INSERT INTO data_points "
                      "(entry_id, measure_id, `value`) VALUES "
                      "(%s, %s, %s)", entry_id, measure_id, value)
