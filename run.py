import sys
import os.path
sys.path[0:0] = [os.path.join(os.path.dirname(__file__), 'src')]

from tornado.options import define, options
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

import ec.pages

settings = {
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "facebook_api_key": "6404a70cad8e247dd9a3f89c4aca56f8",
    "facebook_secret": "2074ea14556a918a1046993130301328",
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}

application = tornado.web.Application([
    (r'/', ec.pages.FrontPage),
    (r'/login', ec.pages.LoginPage),
    (r'/logout', ec.pages.LogoutPage),
    (r'/home', ec.pages.HomePage),
], **settings)

define("debug_templates", default=False)
define("server_port", default=8888)

from tornado import template

class DebugLoader(template.Loader):
    """Debug Template Loader.

    This template loader will always load the template from the file.
    It's slower, but you don't have to restart every time you change
    a template.
    """

    def load(self, name, parent_path=None):
        t = super(DebugLoader, self).load(name, parent_path=parent_path)
        if name in self.templates:
            del self.templates[name]
        return t

def debug_templates():
    template._Loader = template.Loader
    template.Loader = DebugLoader

if __name__ == "__main__":
    if len(sys.argv) < 2:
        conf_file = os.path.join(os.path.dirname(__file__), "conf/dev.conf")
    else:
        conf_file = sys.argv[-1]
    tornado.options.parse_config_file(conf_file)
    if options.debug_templates:
        debug_templates()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
