from ec import db
from ec import fb
from ec import cache
from ec.cache import cache_get

@cache.key
def _get_user_cache_key(uid):
    return "user:%s" % uid


def dbget_user(uid):
    return db.get("SELECT * FROM users WHERE id=%s", uid)

get_user = dbget_user
#def get_user(uid):
#    return cache_get(_get_user_cache_key,
#                     dbget_user,
#                     uid)

def get_users_with_fbids(fbids):
    return db.query("SELECT * FROM users WHERE fbid IN "+db.format_in(fbids), *fbids)

def dbget_user_by_fbid(fbid):
    return db.get("SELECT * FROM users WHERE fbid=%s", fbid)

get_user_by_fbid = dbget_user_by_fbid


def create_user(fbid, fb_access_token):
    return db.execute("INSERT INTO users (fbid, fb_access_token) VALUES (%s, %s)",
                      fbid, fb_access_token)

@cache.invalidates(_get_user_cache_key)
def clear_fb_access_token(uid):
    return db.execute("UPDATE users SET fb_access_token=null WHERE id=%s", uid)

def set_fb_access_token(uid, access_token):
    cache.remove(_get_user_cache_key(uid))
    return db.execute("UPDATE users SET fb_access_token=%s WHERE id=%s",
                      access_token, uid)
