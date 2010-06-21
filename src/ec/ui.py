import datetime
from tornado.web import UIModule

from ec import et
import ec.users

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
        if entries:
            user = ec.users.get_user(entries[0].user_id)
        else:
            user = None
        for entry in entries:
            if 'exercise_type' not in entry:
                entry['exercise_type'] = et.get_exercise_type(entry.exercise_type_id)
            if 'data_points' not in entry:
                entry['data_points'] = ec.entries.get_data_points_for_entry(entry.id)
            for data_point in entry['data_points']:
                if 'measure' not in data_point:
                    data_point['measure'] = et.get_measure(data_point.measure_id)
        return super(EntriesBox, self).render(
            legend=date.strftime("%B %d"),
            content=self.render_string(
                "templates/ui/entries-list.html",
                entries=entries,
                user=user,
                can_delete=can_delete))

class ProfilePic(UIModule):
    def render(self, user):
        return ('<div class="profile-pic">'
                '<img src="http://graph.facebook.com/%s/picture" />'
                '</div>' % user['id'])

class Select(UIModule):

    def render(self, name, options, prompt=None):
        current_value = self.handler.get_argument(name, None)
        def render_option(value, display):
            if unicode(value) == current_value:
                return (u'<option value="{value}" selected="selected">'
                        u'{display}'
                        u'</option>').format(**locals())
            else:
                return u'<option value="{value}">{display}</option>'.format(**locals())

        options = u''.join(render_option(value, display)
                           for value, display in options)
        if prompt:
            options = u'<option>{0}</option>{1}'.format(prompt, options)
        return u'<select name="{name}">{options}</select>'.format(**locals())


class StatusForm(UIModule):
    def render(self):
        today = datetime.date.today()
        dates = [(today,"today"),
                 (today-datetime.timedelta(days=1),"yesterday")]
        for days in [2,3]:
            dates.append((today-datetime.timedelta(days=days), "%s days ago" % days))

        selected_exercise = self.handler.get_argument("et", None)
        measures = None
        if selected_exercise:
            selected_exercise = int(selected_exercise)
            measures = et.get_measures_for_exercise_type(selected_exercise)

        return self.render_string("templates/ui/status-form.html",
                                  dates=dates,
                                  selected_exercise=self.handler.get_argument("et",None),
                                  exercise_types=et.get_all_exercise_types(),
                                  measures=measures)

    def embedded_javascript(self):
        return '''
  $("#status_form select[name='et']").change(
    function() {
      var val = $(this).val();
      var date = $("select[name='date']").val();
      window.location = window.location.pathname+"?"+$("#status_form").serialize();
    });
'''
