# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import datetime
import jinja2
import os

import task

# Formatter function for date/time
def format_datetime(dt, format='%H:%M:%S %Y-%m-%d'):
    if dt is not None:
        dt_str = dt.strftime(format)
    else:
        dt_str = ''
    
    return dt_str


# Formatter function for durations
def format_duration(duration, state, restarted):
    if state == task.STATE.IN_PROGRESS:
        # Duration is logged duration plus time since last restart
        delta = datetime.datetime.now() - restarted
        m, s = divmod(duration + delta.seconds, 60)
        h, m = divmod(m, 60)
        d_str = '%d:%02d:%02d' % (h, m, s)
    elif state == task.STATE.FINISHED:
        # Duration is logged duration
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)
        d_str = '%d:%02d:%02d' % (h, m, s)
    else:
        # state == task.STATE.NEW or undefined, duration is not defined
        d_str = '--:--:--'
    
    return d_str


# Formatter function for estimates
def format_estimate(value):
    m, s = divmod(value, 60)
    h, m = divmod(m, 60)
    return '%d:%02d:%02d' % (h, m, s)


# Configure Jinja2 environment
JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    trim_blocks=True)

JINJA.filters['datetime'] = format_datetime
JINJA.filters['duration'] = format_duration
JINJA.filters['estimate'] = format_estimate
