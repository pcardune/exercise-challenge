from tornado.web import UIModule

class Box(UIModule):
    def render(self, legend=None, content=''):
        return self.render_string(
            "templates/ui/box.html", legend=legend, content=content)

class LeftRight(UIModule):
    def render(self, left='', right=''):
        return self.render_string(
            "templates/ui/left-right.html", left=left, right=right)


class UserBox(Box):

    def render(self, user, content=''):
        return self.render_string(
            "templates/ui/user-box.html",
            user=user,
            content=content)

class EntriesBox(Box):
    def render(self, date, entries, can_delete=False):
        return super(EntriesBox, self).render(
            legend=date.strftime("%B %d"),
            content=self.render_string(
                "templates/ui/entries-list.html",
                entries=entries,
                can_delete=can_delete))

class ProfilePic(UIModule):
    def render(self, user):
        return ('<div class="profile-pic">'
                '<img src="http://graph.facebook.com/%s/picture" />'
                '</div>' % user['id'])
