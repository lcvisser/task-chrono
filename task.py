# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import datetime
import re
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import login_required

import settings
import util


# Task states in order of priority
STATE = util.Enum('IN_PROGRESS', 'NEW', 'FINISHED')


# Regular expressions for parsing duration strings
RE_DAY = re.compile('(\d*\.?\d+)\s*d')
RE_HOUR = re.compile('(\d*\.?\d+)\s*h')
RE_MIN = re.compile('(\d*\.?\d+)\s*m')


# Task class
class Task(ndb.Model):    
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
    state = ndb.IntegerProperty(default=STATE.NEW)


# Handler for creating a new task
class NewTaskHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if not user:
            # Login is required, redirect to login page
            self.redirect(users.create_login_url(self.request.uri))
        else:
            # Get settings for current user
            user_settings = settings.get_settings(user)
            
            # Get key for current list
            list_name = user_settings.active_list
            list_key = ndb.Key('User', user.user_id(), 'TaskList', list_name)
            
            # Validate task name
            input_name = self.request.get('task_name', '')
            if input_name == '' or input_name.isspace():
                # Invalid task name
                self.redirect('/')
                return
            
            # Validate task estimate
            input_estimate = self.request.get('estimate', '')
            if input_estimate == '' or input_estimate[0].isdigit() == False:
                # Invalid estimate
                self.redirect('/')
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
            hpd = int(user_settings.hours_per_day)
            estimate = datetime.timedelta(hours=d*hpd + h, minutes=m)
            
            # Create and add new task
            task = Task(parent=list_key)
            task.name = input_name
            task.estimate = int(estimate.total_seconds())
            task.put()
            
            # Redirect to main page
            self.redirect('/')


# Handler for deleting a task
class DeleteTaskHandler(webapp2.RequestHandler):
    @login_required
    def get(self):
        # Delete task
        task_key = ndb.Key(urlsafe=self.request.get('task_key'))
        task_key.delete()
        
        # Redirect to main page
        self.redirect('/')


# Handler for (re-)starting a task
class StartTaskHandler(webapp2.RequestHandler):
    @login_required
    def get(self):
        # Get requested task
        task_key = ndb.Key(urlsafe=self.request.get('task_key'))
        task = task_key.get()
        
        # Set timestamps
        if task.state in (STATE.NEW, STATE.FINISHED):
            now = datetime.datetime.utcnow()
            if task.started is None:
                # Task was not started before
                task.started = now
            
            # Set task state to "in progress"
            task.restarted = now
            task.state = STATE.IN_PROGRESS
            task.put()
        
        # Redirect to main page
        self.redirect('/')


# Handler for stopping a task
class StopTaskHandler(webapp2.RequestHandler):
    @login_required
    def get(self):
        # Get requested task
        task_key = ndb.Key(urlsafe=self.request.get('task_key'))
        task = task_key.get()
        
        # Set timestamp
        if task.state == STATE.IN_PROGRESS:
            now = datetime.datetime.utcnow()
            task.finished = now
            
            # Calculate duration (rounded to seconds)
            duration_increment = now - task.restarted
            duration_increment -= datetime.timedelta(
                microseconds=duration_increment.microseconds)
            duration = task.duration + int(duration_increment.total_seconds())
            task.duration = duration
            
            # Set task state to "finished"
            task.state = STATE.FINISHED
            task.put()
        
        # Redirect to main page
        self.redirect('/')
