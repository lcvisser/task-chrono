# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import numpy
import os
import StringIO as sio


# Useful enumeration class
class Enum:
    def __init__(self, *sequential, **named):
        enumerated = dict(zip(sequential, range(len(sequential))), **named)
        for name, value in enumerated.iteritems():
            setattr(self, name, value)


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
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    mpl_available = True
else:
    # Running on GAE
    
    # Set-up environment for matplotlib
    os.environ['MATPLOTLIBDATA'] = os.getcwdu()
    os.environ['MPLCONFIGDIR'] = os.getcwdu()
    
    # Try to import matplotlib
    mpl_available = True
    try:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    except ImportError:
        # Running on GAE Development server
        mpl_available = False


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
        w = 0.4  # width of the bars
        
        # Compute values
        for i, task in enumerate(tasks):
            lbe[i] = i - w/2
            errors[i] = (task.duration - task.estimate) / 60.0  # in minutes
            average[i] = numpy.average(errors[:i+1]) / (i + 1)
            sigma_minus[i] = average[i] - numpy.std(errors[:i+1])
            sigma_plus[i] = average[i] + numpy.std(errors[:i+1])
            if errors[i] <= 0:
                # Logged duration was less than estimate
                colors.append(GREEN)
            else:
                # Logged duration was more than estimate
                colors.append(RED)
        
        # Create plot
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(1, 1, 1)
        ax.hold(True)
        ax.set_xlim(M-w/2, N-1+w/2)
        ax.set_xticks([])
        ax.set_xticklabels([])
        ax.set_ylim(min([-10, numpy.min(errors)-10]), max([180, numpy.max(errors)+10]))
        ax.set_ylabel('Estimation error [minutes]')
        ax.grid(axis='y')
        
        # Plot data
        ax.plot(x[M:], average[M:], color=DARK_BLUE)
        ax.plot(x[M:], sigma_minus[M:], color=LIGHT_BLUE)
        ax.plot(x[M:], sigma_plus[M:], color=LIGHT_BLUE)
        ax.fill_between(x[M:], y1=sigma_minus[M:], y2=sigma_plus[M:], color=LIGHT_BLUE)
        ax.bar(lbe[M:], errors[M:], w, color=colors[M:], alpha=0.4)
        
        # Create labels
        for x, task in enumerate(tasks[M:]):
            ax.text(x+M, 1, task.name, rotation=90, ha='center', va='bottom')
        
        # Output
        if not display:
            # Output as base64-encoded string
            im = sio.StringIO()
            fig.savefig(im, format='png')
            png = im.getvalue().encode('base64').strip()
            return png
        else:
            # Show on screen
            canvas.show()
            return None
    else:
        return None


# Unit test
if __name__ == '__main__':
    import random
    
    class Task:
        def __init__(self, n, e, d):
            self.name = n
            self.estimate = e
            self.duration = d
    
    tasks = []
    for i in range(25):
        tasks.append(Task('Task with ID' + str(i),
            random.normalvariate(3600, 20),
            random.normalvariate(3600, 20)))
    
    generate_est_png(tasks, display=True)
