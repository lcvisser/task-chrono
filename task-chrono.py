# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import login_required

from settings import SettingsPage, SaveSettingsHandler
from settings import get_settings
from stats import StatsPage
from task import Task, NewTaskHandler, DeleteTaskHandler
from task import StartTaskHandler, StopTaskHandler
from util import JINJA


# Main page request handler
class MainPage(webapp2.RequestHandler):
    @login_required
    def get(self):
        # Get settings for current user
        user = users.get_current_user()
        settings = get_settings(user)
        
        # Get key for current list
        list_name = settings.active_list
        list_key = ndb.Key('User', user.user_id(), 'TaskList', list_name)
        
        # Get tasks for list, order by priority and creation date
        task_query = Task.query(ancestor=list_key).order(Task.state, Task.created)
        tasks = task_query.fetch()
        
        # Create template context
        context = {
            'page': 'list',
            'tasks': tasks,
            'logout_url': users.create_logout_url('/')}
        
        # Parse and serve template
        template = JINJA.get_template('tasklist.html')
        self.response.write(template.render(context))


# Help page request handler
class HelpPage(webapp2.RequestHandler):
    def get(self):
        # Create template context
        context = {
            'page': 'help',
            'logout_url': users.create_logout_url(self.request.uri)}
        
        # Parse and serve template
        template = JINJA.get_template('help.html')
        self.response.write(template.render(context))


# Main application instance
application = webapp2.WSGIApplication(
    [('/', MainPage),
    ('/stats', StatsPage),
    ('/settings', SettingsPage),
    ('/help', HelpPage),
    ('/new', NewTaskHandler),
    ('/delete', DeleteTaskHandler),
    ('/start', StartTaskHandler),
    ('/stop', StopTaskHandler),
    ('/save', SaveSettingsHandler)
    ], debug=False)
