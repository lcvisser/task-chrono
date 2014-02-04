# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import datetime
import os
import StringIO as sio
import subprocess
import math
import numpy


# Task states in order of priority
STATE_IN_PROGRESS = 0
STATE_NEW = 1
STATE_FINISHED = 2


# Set-up environment for matplotlib
os.environ['MATPLOTLIBDATA'] = os.getcwdu()
os.environ['MPLCONFIGDIR'] = os.getcwdu()

# Disable subprocess for matplotlib; not available on GAE
def no_popen(*args, **kwargs):
    raise OSError('popen disabled')
subprocess.Popen = no_popen
subprocess.PIPE = None
subprocess.STDOUT = None

mpl_available = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
except ImportError:
    # Running on GAE Development server
    mpl_available = False


# Formatter function for date/time
def format_datetime(dt, format='%H:%M:%S %Y-%m-%d'):
    if dt is not None:
        dt_str = dt.strftime(format)
    else:
        dt_str = ''
    
    return dt_str


# Formatter function for durations
def format_duration(duration, state, restarted):
    if state == STATE_IN_PROGRESS:
        # Duration is logged duration plus time since last restart
        delta = datetime.datetime.now() - restarted
        m, s = divmod(duration + delta.seconds, 60)
        h, m = divmod(m, 60)
        d_str = '%d:%02d:%02d' % (h, m, s)
    elif state == STATE_FINISHED:
        # Duration is logged duration
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)
        d_str = '%d:%02d:%02d' % (h, m, s)
    else:
        # state == STATE_NEW or undefined, duration is not defined
        d_str = '--:--:--'
    
    return d_str


# Formatter function for estimates
def format_estimate(value):
    m, s = divmod(value, 60)
    h, m = divmod(m, 60)
    return '%d:%02d:%02d' % (h, m, s)


# PNG generator for estimation statistics
def generate_est_png(tasks, display=False):
    if mpl_available:
        w = 0.4
        lbe = numpy.zeros(len(tasks))
        estimates = numpy.zeros(len(tasks))
        lbd = numpy.zeros(len(tasks))
        durations = numpy.zeros(len(tasks))
        
        for i, task in enumerate(tasks):
            lbe[i] = i - w
            estimates[i] = task.estimate
            lbd[i] = i
            durations[i] = task.duration
            
        plt.title('Estimation accuracy')
        plt.bar(lbe, estimates, w, color=(0.43,0.92,0.8), hold=True)
        plt.bar(lbd, durations, w, color=(0.77,0.9,1.0), hold=True)
        
        if not display:
            im = sio.StringIO()
            plt.savefig(im, format='png')
            png = im.getvalue().encode('base64').strip()
            plt.clf()
            return png
        else:
            matplotlib.rcParams['backend'] = 'Qt4Agg'
            plt.show()
            return None
    else:
        return None



if __name__ == '__main__':
    import random
    
    class Task:
        def __init__(self, n, e, d):
            self.name = n
            self.estimate = e
            self.duration = d
    
    tasks = []
    for i in range(10):
        tasks.append(Task('task' + str(i),
            random.normalvariate(i, 0.2),
            random.normalvariate(i, 0.4)))
    
    generate_est_png(tasks, display=True)
