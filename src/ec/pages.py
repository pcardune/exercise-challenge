import urlparse
import datetime
from tornado import database, web, auth, httpclient, escape
from tornado.options import define, options

from ec.db import get_conn
import ec.users
import ec.entries
from ec import fb
from ec import et


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

    def render_status_form(self):
        selected_exercise = self.get_argument("et", None)
        measures = None
        if selected_exercise:
            selected_exercise = int(selected_exercise)
            measures = et.get_measures_for_exercise_type(selected_exercise)
        return self.render_string(
            "templates/status-form.html",
            exercise_types=et.get_all_exercise_types(),
            selected_exercise=selected_exercise,
            measures=measures)

    def _on_get_user(self, user, error=None):
        if error:
            self.render("templates/error-page.html", error=error)
        else:
            self.user = user
            fb.get_user_friends_on_here(self.current_user.fbid,
                                        self.current_user,
                                        self.async_callback(self._on_get_friends))

    def _on_get_friends(self, friends, error=None):
        if error:
            self.render("templates/error-page.html", error=error)
        else:
            self.render("templates/home-page.html",
                        user=self.user,
                        entries_by_date=ec.entries.get_entries_by_date(self.current_user.id),
                        friends=friends,
                        )


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


class CreateExerciseTypePage(BasePage):

    def post(self):
        name = self.get_argument('name')
        description = self.get_argument('description', '')
        et.create_exercise_type(name, description)
        self.redirect('/exercises')


class ExerciseTypesPage(BasePage):
    def get(self):
        exercise_types = et.get_all_exercise_types()
        self.render("templates/exercise-types-page.html",
                    form=self.render_string("templates/create-exercise-type-form.html"),
                    exercise_types=exercise_types)


class CreateEntryPage(BasePage):
    def post(self):
        exercise_type = et.get_exercise_type(
            int(self.get_argument("et")))

        date = datetime.datetime.strptime(
            self.get_argument('date'),
            "%Y-%m-%d")

        entry_id = ec.entries.create_entry(
            self.current_user.id,
            date,
            exercise_type.id)

        measures = et.get_measures_for_exercise_type(exercise_type.id)
        for measure in measures:
            value = self.get_argument("measure-%s-value" % measure.id, None)
            if value:
                ec.entries.create_data_point(
                    entry_id, measure.id, value)

        self.redirect('/home')


class BaseUserPage(BasePage):
    @web.asynchronous
    def get(self, fbid):
        self.user = ec.users.get_user_by_fbid(fbid)
        fb.get_user(fbid,
                    self.current_user,
                    self.async_callback(self._on_get_user))

    def _on_get_user(self, fbuser, error=None):
        if error:
            self.render("templates/error-page.html", error=error)
        else:
            self.on_get_user(fbuser)


class UserPage(BaseUserPage):

    def on_get_user(self, fbuser):
        self.render("templates/user-page.html",
                    user=self.user,
                    fbuser=fbuser,
                    entries_by_date=ec.entries.get_entries_by_date(self.user.id),
                    can_delete=False)


class UserStatsPage(BaseUserPage):

#    def get_charts(self):
#        by_date = ec.entries.get_entries_by_date(uid)
#        for date, entries in ec.entries.

    def on_get_user(self, fbuser):
        self.render("templates/user-stats-page.html",
                    user=self.user,
                    fbuser=fbuser,
                    chars=self.get_charts())


class DeleteEntryPage(BasePage):
    def post(self, entry_id):
        entry = ec.entries.get_entry(entry_id)
        if entry.user_id == self.current_user.id:
            ec.entries.delete_entry(entry_id)
        self.redirect('/home')
