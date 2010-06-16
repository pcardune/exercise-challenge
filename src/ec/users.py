from ec.db import get_conn, cache_get
from ec import fb
from ec import cache

@cache.key
def _get_user_cache_key(uid):
    return "user:%s" % uid


def dbget_user(uid):
    db = get_conn()
    return db.get("SELECT * FROM users WHERE id=%s", uid)

def get_user(uid):
    return cache_get(_get_user_cache_key,
                     dbget_user,
                     uid)

def dbget_user_by_fbid(fbid):
    db = get_conn()
    return db.get("SELECT * FROM users WHERE fbid=%s", fbid)

get_user_by_fbid = dbget_user_by_fbid


def create_user(fbid, fb_access_token):
    db = get_conn()
    return db.execute("INSERT INTO users (fbid, fb_access_token) VALUES (%s, %s)",
                      fbid, fb_access_token)

@cache.invalidates(_get_user_cache_key)
def clear_fb_access_token(uid):
    db = get_conn()
    return db.execute("UPDATE users SET fb_access_token=null WHERE id=%s", uid)

@cache.invalidates(_get_user_cache_key)
def set_fb_access_token(uid, access_token):
    db = get_conn()
    return db.execute("UPDATE users SET fb_access_token=%s WHERE id=%s",
                      access_token, uid)
