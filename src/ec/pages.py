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

    def render(self, *args, **kwargs):
        kwargs.setdefault("OPTIONS", options)
        super(BasePage, self).render(*args, **kwargs)
        if options.debug_templates:
            del web.RequestHandler._templates

    def json_callback(self, func):
        def wrapper(response):
            if response.error:
                self.write(response.body)
                self.finish()
            else:
                func(escape.json_decode(response.body))
        return self.async_callback(wrapper)


class FrontPage(BasePage):

    def get(self):
        if self.current_user:
            return self.redirect('/home')
        self.render("templates/front-page.html")


class HomePage(BasePage):

    @web.authenticated
    @web.asynchronous
    def get(self):
        fb.get_user(self.current_user.fbid,
                    self.current_user,
                    self.async_callback(self._on_get_user))

    def _on_get_user(self, user, error=None):
        if error:
            self.render("templates/error-page.html", error=error)
        else:
            self.render("templates/home-page.html", name=user['name'])


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
            return self.redirect(fb.get_authorization_url(redirect_url,
                                                          scope=['offline_access']))

    def fail_auth(self, error=None):
        self.write("Facebook Authentication Failed :( %s" % error)
        self.finish()

    def _on_access_token_recieved(self, response):
        if response.error:
            self.fail_auth(response.body)
        else:
            self.access_token = urlparse.parse_qs(response.body)['access_token'][0]
            fb.fbget_self(self.access_token, self.async_callback(self._on_user_recieved))

    def _on_user_recieved(self, json, error=None):
        if error:
            self.write(error)
            self.finish()
        else:
            fbid = json['id']
            user = ec.users.get_user_by_fbid(fbid)
            if user:
                uid = user.id
                ec.users.set_fb_access_token(uid, self.access_token)
            else:
                uid = ec.users.create_user(fbid, self.access_token)
            self.set_secure_cookie("user", str(uid))
            return self.redirect("/")


class LogoutPage(BasePage):

    def get(self):
        ec.users.clear_fb_access_token(self.current_user.id)
        self.clear_all_cookies()
        return self.redirect('/')
