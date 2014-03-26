# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import login_required

from settings import get_settings
from task import Task
from util import generate_est_png
from util import JINJA, STATE


# Stats page request handler
class StatsPage(webapp2.RequestHandler):
    @login_required
    def get(self):
        # Get settings for current user
        user = users.get_current_user()
        settings = get_settings(user)
        
        # Get key for current list
        list_name = settings.active_list
        list_key = ndb.Key('User', user.user_id(), 'TaskList', list_name)
        
        # Get tasks for list, order by priority and creation date
        task_query = Task.query(
                Task.state == STATE.FINISHED,
                ancestor=list_key).order(Task.finished)
        tasks = task_query.fetch(100)
        
        # Generate PNG
        est_png = generate_est_png(tasks, 25)
        
        # Create template context
        context = {
            'page': 'stats',
            'estimation_png': est_png,
            'logout_url': users.create_logout_url(self.request.uri)}
        
        # Parse and serve template
        template = JINJA.get_template('stats.html')
        self.response.write(template.render(context))
