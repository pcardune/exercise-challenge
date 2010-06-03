from ec.db import get_conn

def dbget_user(uid):
    db = get_conn()
    return db.get("SELECT * FROM users WHERE id=%s", uid)

get_user = dbget_user


def dbget_user_by_fbid(fbid):
    db = get_conn()
    return db.get("SELECT * FROM users WHERE fbid=%s", fbid)

get_user_by_fbid = dbget_user_by_fbid


def create_user(fbid, fb_access_token):
    db = get_conn()
    return db.execute("INSERT INTO users (fbid, fb_access_token) VALUES (%s, %s)",
                      fbid, fb_access_token)
