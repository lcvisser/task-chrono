# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import login_required

from settings import DEFAULT_LIST_NAME
from stats import StatsPage
from task import Task, NewTaskHandler, DeleteTaskHandler
from task import StartTaskHandler, StopTaskHandler
from util import JINJA


# Main page request handler
class MainPage(webapp2.RequestHandler):
    @login_required
    def get(self):
        # Get key for requested list
        user = users.get_current_user()
        list_name = self.request.get('list_name', DEFAULT_LIST_NAME)
        list_key = ndb.Key('User', user.user_id(), 'TaskList', list_name)
        
        # Get tasks for list, order by priority and creation date
        task_query = Task.query(ancestor=list_key).order(Task.state, Task.created)
        tasks = task_query.fetch()
        
        # Create template context
        context = {
            'list_name': DEFAULT_LIST_NAME,
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
            'list_name': DEFAULT_LIST_NAME,
            'page': 'help',
            'logout_url': users.create_logout_url(self.request.uri)}
        
        # Parse and serve template
        template = JINJA.get_template('help.html')
        self.response.write(template.render(context))


# Main application instance
application = webapp2.WSGIApplication(
    [('/', MainPage),
    ('/stats', StatsPage),
    # placeholder for settings
    ('/help', HelpPage),
    ('/new', NewTaskHandler),
    ('/delete', DeleteTaskHandler),
    ('/start', StartTaskHandler),
    ('/stop', StopTaskHandler)
    ], debug=False)
