# -*- coding: utf-8 -*-

# Copyright (c) 2014 Ludo Visser
#
# task-chrono is distributed under the terms and conditions of the MIT license.
# The full license can be found in the LICENSE file.

import datetime
import os
import StringIO as sio
import subprocess
import numpy


# Set-up environment for matplotlib
os.environ['MATPLOTLIBDATA'] = os.getcwdu()
os.environ['MPLCONFIGDIR'] = os.getcwdu()

# Disable subprocess for matplotlib; not available on GAE
def no_popen(*args, **kwargs):
    raise OSError('popen not available')
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


# PNG generator for estimation statistics
def generate_est_png():
    if mpl_available:
        plt.title("Dynamic PNG")
        for i in range(5): plt.plot(sorted(numpy.random.randn(25)))
        rv = sio.StringIO()
        plt.savefig(rv, format="png")
        plt.clf()
        return rv.getvalue().encode('base64').strip()
    else:
        return ''


if __name__ == "__main__":
    pass