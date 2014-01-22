# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import datetime
import jinja2
import os
import re
import urllib
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb


# Formatter function for date/time
DATETIME_FORMAT = '%H:%M:%S %Y-%m-%d'
def format_datetime(dt, format='medium'):
    if dt is not None:
        r = dt.strftime(DATETIME_FORMAT)
    else:
        r = ''
    
    return r
    
# Formatter function for durations
def format_duration(value, format='medium'):
    return str(datetime.timedelta(seconds=value))


# Configure Jinja2 environment
JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    trim_blocks=True)

JINJA.filters['datetime'] = format_datetime
JINJA.filters['duration'] = format_duration


# Default task list name
DEFAULT_LIST_NAME = 'Tasks'


# Task states in order of priority
STATE_IN_PROGRESS = 0
STATE_NEW = 1
STATE_FINISHED = 2


# Regular expressions for parsing duration strings
RE_DAY = re.compile('(\d*\.?\d+)\s*d')
RE_HOUR = re.compile('(\d*\.?\d+)\s*h')
RE_MIN = re.compile('(\d*\.?\d+)\s*m')


# Task class
class Task(ndb.Model):
    # Owner of the task, i.e. the user creating it
    owner = ndb.StringProperty(indexed=True)
    
    # Descriptive name of the task
    name = ndb.StringProperty(indexed=False, default='')
    
    # Estimated duration, in seconds
    estimate = ndb.IntegerProperty(indexed=False, default=0)
    
    # Actual logged duration, in seconds
    duration = ndb.IntegerProperty(indexed=False, default=0)
    
    # Timestamps
    created = ndb.DateTimeProperty(auto_now_add=True)
    started = ndb.DateTimeProperty(auto_now_add=False)
    restarted = ndb.DateTimeProperty(auto_now_add=False)
    finished = ndb.DateTimeProperty(auto_now_add=False)
    
    # Current state
    state = ndb.IntegerProperty(default=STATE_NEW)


# Main page request handler
class MainPage(webapp2.RequestHandler):
    def get(self):        
        user = users.get_current_user()
        if not user:
            # Login is required, redirect to login page
            self.redirect(users.create_login_url(self.request.uri))
        else:
            # Get key for requested list
            list_name = self.request.get('list_name', DEFAULT_LIST_NAME)
            list_key = ndb.Key('User', user.user_id(), 'TaskList', list_name)
            
            # Get tasks for list, order by priority and creation date
            task_query = Task.query(ancestor=list_key).order(Task.state, -Task.created)
            tasks = task_query.fetch()
            
            # Create template context
            context = {
                'list_name': DEFAULT_LIST_NAME,
                'page': 'list',
                'tasks': tasks,
                'logout_url': users.create_logout_url(self.request.uri)}
            
            # Parse and serve template
            template = JINJA.get_template('index.html')
            self.response.write(template.render(context))


# Handler for creating a new task
class NewTaskHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if not user:
            # Login is required, redirect to login page
            self.redirect(users.create_login_url(self.request.uri))
        else:
            # Get key for requested list
            list_name = self.request.get('list_name', DEFAULT_LIST_NAME)
            list_key = ndb.Key('User', user.user_id(), 'TaskList', list_name)
            query_params = {'list_name': list_name}
            
            # Validate task name
            input_name = self.request.get('task_name', '')
            if input_name == '' or input_name.isspace():
                # Invalid task name
                self.redirect('/?' + urllib.urlencode(query_params))
                return
            
            # Validate task estimate
            input_estimate = self.request.get('estimate', '')
            if input_estimate == '' or input_estimate[0].isdigit() == False:
                # Invalid estimate
                self.redirect('/?' + urllib.urlencode(query_params))
                return
            
            # Helper function for parsing parts of estimate string
            def parse(string, regex):
                r = regex.findall(string)
                if r:
                    try:
                        value = float(r[0])
                    except ValueError:
                        value = 0
                else:
                    value = 0
                
                return value
            
            # Get estimate in days, hours and minutes
            d = parse(input_estimate, RE_DAY)
            h = parse(input_estimate, RE_HOUR)
            m = parse(input_estimate, RE_MIN)
            estimate = datetime.timedelta(days=d, hours=h, minutes=m)
            
            # Create and add new task
            task = Task(parent=list_key)
            task.name = input_name
            task.estimate = int(estimate.total_seconds())
            task.put()
            
            # Redirect to main page
            self.redirect('/?' + urllib.urlencode(query_params))


# Handler for deleting a task
class DeleteTaskHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            # Login is required, redirect to login page
            self.redirect(users.create_login_url('/'))
        else:
            # DElete task
            task_key = ndb.Key(urlsafe=self.request.get('task_key'))
            task_key.delete()
            
            # Redirect to main page
            self.redirect('/')


# Handler for (re-)starting a task
class StartTaskHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            # Login is required, redirect to login page
            self.redirect(users.create_login_url('/'))
        else:
            # Get requested task
            task_key = ndb.Key(urlsafe=self.request.get('task_key'))
            task = task_key.get()
            
            # Set timestamps
            if task.state in (STATE_NEW, STATE_FINISHED):
                now = datetime.datetime.utcnow()
                if task.started is None:
                    # Task was not started before
                    task.started = now
                
                # Set task state to "in progress"
                task.restarted = now
                task.state = STATE_IN_PROGRESS
                task.put()
            
            # Redirect to main page
            self.redirect('/')


# Handler for stopping a task
class StopTaskHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            # Login is required, redirect to login page
            self.redirect(users.create_login_url('/'))
        else:
            # Get requested task
            task_key = ndb.Key(urlsafe=self.request.get('task_key'))
            task = task_key.get()
            
            # Set timestamp
            if task.state == STATE_IN_PROGRESS:
                now = datetime.datetime.utcnow()
                task.finished = now
                
                # Calculate duration (rounded to seconds)
                duration_increment = now - task.restarted
                duration_increment -= datetime.timedelta(
                    microseconds=duration_increment.microseconds)
                duration = task.duration + int(duration_increment.total_seconds())
                task.duration = duration
                
                # Set task state to "finished"
                task.state = STATE_FINISHED
                task.put()
            
            # Redirect to main page
            self.redirect('/')


# Application instance
application = webapp2.WSGIApplication(
    [('/', MainPage),
     ('/new', NewTaskHandler),
     ('/delete', DeleteTaskHandler),
     ('/start', StartTaskHandler),
     ('/stop', StopTaskHandler)
    ], debug=False)
