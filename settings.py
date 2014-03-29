# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import login_required

import render
import task


# Default task list name
DEFAULT_LIST_NAME = 'Tasks'


# Possible hours_per_day options
POSSIBLE_HOURS_PER_DAY = (7, 8, 9, 10, 24)


# Settings class
class Settings(ndb.Model):    
    # Setting: number of working hours per day
    hours_per_day = ndb.IntegerProperty(indexed=False, default=8)
    
    # Setting: name of active task list
    active_list = ndb.StringProperty(indexed=False, default=DEFAULT_LIST_NAME)
    
    # List of task list names
    list_names = ndb.StringProperty(indexed=False, repeated=True)


# Helper function to get settings for user
def get_settings(user):
    # Get key for settings
    settings_key = ndb.Key('User', user.user_id())
    
    # Get current settings
    settings_query = Settings.query(ancestor=settings_key)
    settings = settings_query.get()

    # Create new settings object if none exists
    if not settings:
        settings = Settings(parent=settings_key)
        settings.list_names = [DEFAULT_LIST_NAME]
        settings.put()
    
    return settings


# Settings page request handler
class SettingsPage(webapp2.RequestHandler):
    @login_required
    def get(self):
        # Get settings
        settings = get_settings(users.get_current_user())
        
        # Create template context
        context = {
            'page': 'settings',
            'saved': self.request.get('saved', ''),
            'settings': settings,
            'possible_hours_per_day': POSSIBLE_HOURS_PER_DAY,
            'logout_url': users.create_logout_url('/')}
        
        # Parse and serve template
        template = render.JINJA.get_template('settings.html')
        self.response.write(template.render(context))


class SaveSettingsHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if not user:
            # Login is required, redirect to login page
            self.redirect(users.create_login_url(self.request.uri))
        else:
            # Get settings
            settings = get_settings(user)
            
            # Set hours per day
            try:
                hours_per_day = int(self.request.get('hours_per_day', '0'))
            except ValueError:
                hours_per_day = None
            
            if hours_per_day in POSSIBLE_HOURS_PER_DAY:
                settings.hours_per_day = hours_per_day
            
            # Set active list name
            current_active_list = settings.active_list
            new_active_list = self.request.get('active_list', '')
            if new_active_list in settings.list_names:
                settings.active_list = new_active_list
            
            # Add list (if necessary)
            new_list_name = self.request.get('new_list', '')
            if new_list_name == '' or new_list_name.isspace() or (new_list_name in settings.list_names):
                # Invalid name
                pass
            else:
                settings.list_names.append(new_list_name)
                settings.active_list = new_list_name    
            
            # Delete list (if necessary)
            if self.request.get('delete_list', 'off').lower() == 'on':
                list_key = ndb.Key('User', user.user_id(), 'TaskList', current_active_list)
        
                # Get tasks for list
                task_query = task.Task.query(ancestor=list_key)
                tasks = task_query.fetch()
                
                # Delete tasks
                for t in tasks:
                    t.key.delete()
                    
                # Delete the list name
                if current_active_list in settings.list_names:
                    settings.list_names.remove(current_active_list)
                
                # Handle list deletion
                if not settings.list_names:
                    # No more lists left
                    settings.active_list = DEFAULT_LIST_NAME
                    settings.list_names = [DEFAULT_LIST_NAME]
                elif settings.active_list == current_active_list:
                    # Current active list was deleted; set most recently added
                    settings.active_list = settings.list_names[-1]
                else:
                    pass
            
            # Save settings
            settings.put()
            
            # Redirect to main page
            self.redirect('/settings?saved=yes')
