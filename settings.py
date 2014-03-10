# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import login_required

from util import JINJA, STATE


# Default task list name
DEFAULT_LIST_NAME = 'Tasks'


# Settings class
class Settings(ndb.Model):
    # Owner of the settings, i.e. the user
    owner = ndb.StringProperty(indexed=True)
    
    # Setting: number of working hours per day
    hours_per_day = ndb.IntegerProperty(indexed=False, default=8)
    
    # Setting: name of active task list
    active_list_name = ndb.StringProperty(indexed=False, default=DEFAULT_LIST_NAME)
    
    # List of task list names
    list_names = ndb.StringProperty(indexed=False, repeated=True)
