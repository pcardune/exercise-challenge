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
                           args=(uid,))

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
                           args=(entry_id,))

def create_data_point(entry_id, measure_id, value):
    cache.remove(_get_data_points_for_entry(entry_id))
    return db.execute("INSERT INTO data_points "
                      "(entry_id, measure_id, `value`) VALUES "
                      "(%s, %s, %s)", entry_id, measure_id, value)


def get_entries_by_date(uid):
    """Given a user, get the user's entries by date."""
    from ec import et
    entries = get_entries_for_user(uid)
    by_date = {}
    for entry in entries:
        by_date.setdefault(entry.date, [])
        by_date[entry.date].append(entry)
        entry['exercise_type'] = et.get_exercise_type(entry.exercise_type)
        entry['data_points'] = get_data_points_for_entry(entry.id)
        for data_point in entry['data_points']:
            data_point['measure'] = et.get_measure(data_point.measure_id)

    return sorted(by_date.items(), reverse=True)

