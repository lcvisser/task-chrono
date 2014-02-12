# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import datetime
import os
import StringIO as sio
import math
import numpy


# Task states in order of priority
STATE_IN_PROGRESS = 0
STATE_NEW = 1
STATE_FINISHED = 2

# Define colors
GREEN = (0.43,0.92,0.80)
RED = (0.92,0.43,0.43)
DARK_BLUE = (0.43, 0.43, 0.92)
LIGHT_BLUE = (0.77, 0.9, 1.0)


# Try to load matplotlib
mpl_available = None
if __name__ == '__main__':
    # Running as script
    os.chdir(os.environ['HOME'])
    import matplotlib.pyplot as plt
    mpl_available = True
else:
    # Running on GAE
    
    # Set-up environment for matplotlib
    os.environ['MATPLOTLIBDATA'] = os.getcwdu()
    os.environ['MPLCONFIGDIR'] = os.getcwdu()
    
    # Try to import matplotlib
    mpl_available = True
    try:
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
def generate_est_png(tasks, number=10, display=False):
    if len(tasks) > 0 and mpl_available:
        # Allocate arrays
        N = len(tasks)
        x = numpy.arange(N)
        lbe = numpy.zeros(N)
        errors = numpy.zeros(N)
        average = numpy.zeros(N)
        sigma_minus = numpy.zeros(N)
        sigma_plus = numpy.zeros(N)
        colors = []
        
        # Plot properties
        M = max([0, N - number])  # index of first task to show
        w = 0.6  # width of the bars
        
        # Compute values
        for i, task in enumerate(tasks):
            lbe[i] = i - w/2
            errors[i] = (task.estimate - task.duration) / 60.0  # in minutes
            average[i] = numpy.average(errors[:i+1]) / (i + 1)
            sigma_minus[i] = average[i] - numpy.std(errors[:i+1])
            sigma_plus[i] = average[i] + numpy.std(errors[:i+1])
            if errors[i] >= 0:
                # Logged duration was less than estimate
                colors.append(GREEN)
            else:
                # Logged duration was more than estimate
                colors.append(RED)
        
        # Create plot
        plt.title('Estimation accuracy')
        plt.hold(True)
        plt.xlim(M-w/2, N-1+w/2)
        plt.xticks([])
        plt.ylim(min([-10, numpy.min(errors)-10]), max([10, numpy.max(errors)+10]))
        plt.ylabel('Estimation error [minutes]')
        
        # Plot data
        plt.plot(x[M:], average[M:], color=DARK_BLUE)
        plt.plot(x[M:], sigma_minus[M:], color=LIGHT_BLUE)
        plt.plot(x[M:], sigma_plus[M:], color=LIGHT_BLUE)
        plt.fill_between(x[M:], y1=sigma_minus[M:], y2=sigma_plus[M:], color=LIGHT_BLUE)
        plt.bar(lbe[M:], errors[M:], w, color=colors[M:], alpha=0.4)
        
        # Create labels
        for x, task in enumerate(tasks[M:]):
            plt.text(x+M, 1, task.name, rotation=90, ha='center', va='bottom')

        
        # Output
        if not display:
            # Output as base64-encoded string
            im = sio.StringIO()
            plt.savefig(im, format='png')
            png = im.getvalue().encode('base64').strip()
            plt.clf()
            return png
        else:
            # Show on screen
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
    for i in reversed(range(15)):
        tasks.append(Task('Task with ID' + str(i),
            random.normalvariate(3600, 20/(i+1)),
            random.normalvariate(3000, 40/(i+1))))
    
    generate_est_png(tasks, display=True)
