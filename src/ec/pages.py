import urlparse
from tornado import database, web, auth, httpclient, escape
from tornado.options import define, options

from ec.db import get_conn
import ec.users
from ec import fb


class BasePage(web.RequestHandler):

    def get_current_user(self):
        uid = self.get_secure_cookie("user")
        if uid:
            return ec.users.get_user(int(uid))


class FrontPage(BasePage):

    def get(self):
        if self.current_user:
            return self.redirect('/home')
        self.render("templates/front-page.html")


class HomePage(BasePage):

    @web.authenticated
    def get(self):
        self.render("templates/home-page.html")


class LoginPage(BasePage):

    @web.asynchronous
    def get(self):
        code = self.get_argument('code', None)
        redirect_url = "%s://%s%s" % (self.request.protocol,
                                      self.request.host,
                                      self.request.path)
        if code:
            fb.get_access_token(code,
                                redirect_url,
                                self.async_callback(self._on_access_token_recieved))
        else:
            return self.redirect(fb.get_authorization_url(redirect_url))

    def fail_auth(self, error=None):
        self.write("Facebook Authentication Failed :( %s" % error)
        self.finish()

    def _on_access_token_recieved(self, response):
        if response.error:
            self.fail_auth(response.body)
        else:
            self.access_token = urlparse.parse_qs(response.body)['access_token'][0]
            fb.get_user(self.access_token, self.async_callback(self._on_user_recieved))

    def _on_user_recieved(self, response):
        if response.error:
            self.fail_auth(response.body)
        else:
            json = escape.json_decode(response.body)
            fbid = json['id']
            user = ec.users.get_user_by_fbid(fbid)
            if user:
                uid = user.id
            else:
                uid = ec.users.create_user(fbid, self.access_token)
            self.set_secure_cookie("user", str(uid))
            return self.redirect("/")


class LogoutPage(BasePage):
    def get(self):
        self.clear_all_cookies()
        return self.redirect('/')
