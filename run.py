import sys
import os.path
sys.path[0:0] = [os.path.join(os.path.dirname(__file__), 'src')]

import tornado.httpserver
import tornado.ioloop
import tornado.web

import ec.pages

settings = {
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "facebook_api_key": "6404a70cad8e247dd9a3f89c4aca56f8",
    "facebook_secret": "2074ea14556a918a1046993130301328",
}

application = tornado.web.Application([
    (r'/', ec.pages.FrontPage),
    (r'/login', ec.pages.LoginPage),
    (r'/logout', ec.pages.LogoutPage),
    (r'/home', ec.pages.HomePage),
], **settings)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
