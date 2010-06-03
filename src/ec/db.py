import tornado.database

def get_conn():
    return tornado.database.Connection("localhost", "exercise", user="root")
