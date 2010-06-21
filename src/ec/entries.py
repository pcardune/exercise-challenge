from ec import db
from ec import cache

@cache.key
def _get_entries_for_user_cache_key(uid):
    return "entries:%s" % uid

@cache.key
def _get_data_points_for_entry_cache_key(entry_id):
    return "data_points:%s" % entry_id

def dbget_entries_for_user(uid):
    return db.query("SELECT * FROM entries WHERE user_id=%s", uid)

def translate(entry):
    entry['exercise_type_id'] = entry['exercise_type']
    del entry['exercise_type']
    return entry

def translate_many(entries):
    return [translate(entry) for entry in entries]


def get_entries_for_user(uid):
    return translate_many(cache.cache_get(_get_entries_for_user_cache_key,
                                          dbget_entries_for_user,
                                          args=(uid,)))

def create_entry(uid, date, exercise_type_id, comment):
    cache.remove(_get_entries_for_user_cache_key(uid))
    return db.execute("INSERT INTO entries "
                      "(user_id, date, exercise_type, comment) VALUES "
                      "(%s, %s, %s, %s)",
                      uid, date, exercise_type_id, comment)

def set_entry_shared(entry_id, fbshare_id):
    return db.execute("UPDATE entries "
                      "SET fbshare_id=%s WHERE id=%s",
                      fbshare_id, entry_id)

def get_entry(entry_id):
    return translate(db.get("SELECT * FROM entries WHERE id=%s", entry_id))

def delete_entry(entry_id):
    cache.remove(_get_data_points_for_entry_cache_key(entry_id))
    return db.execute("DELETE FROM entries WHERE id=%s", entry_id)

def dbget_data_points_for_entry(entry_id):
    return db.query("SELECT * FROM data_points WHERE entry_id=%s", entry_id)

def get_data_points_for_entry(entry_id):
    return cache.cache_get(_get_data_points_for_entry_cache_key,
                           dbget_data_points_for_entry,
                           args=(entry_id,))

def create_data_point(entry_id, measure_id, value):
    cache.remove(_get_data_points_for_entry_cache_key(entry_id))
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
        entry['exercise_type'] = et.get_exercise_type(entry.exercise_type_id)
        entry['data_points'] = get_data_points_for_entry(entry.id)
        for data_point in entry['data_points']:
            data_point['measure'] = et.get_measure(data_point.measure_id)

    return sorted(by_date.items(), reverse=True)


