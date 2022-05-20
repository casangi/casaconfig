########################################################################
#
# Copyright (C) 2022
# Associated Universities, Inc. Washington DC, USA.
#
# This script is free software; you can redistribute it and/or modify it
# under the terms of the GNU Library General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
# License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
#
# Correspondence concerning AIPS++ should be adressed as follows:
#        Internet email: aips2-request@nrao.edu.
#        Postal address: AIPS++ Project Office
#                        National Radio Astronomy Observatory
#                        520 Edgemont Road
#                        Charlottesville, VA 22903-2475 USA
#
########################################################################
'''
Default values for the configuration variables for all CASA python packages.
New configuration variables should be added here.
'''
import os as _os
import time as _time
import pkgutil as _pkgutil

def _globals( ):
    return globals()

# list of paths where CASA should search for data subdirectories
_casaconfig_loader = _pkgutil.get_loader('casaconfig')
if _casaconfig_loader:
    _f = _os.path.join(_os.path.dirname(_casaconfig_loader.path),'__data__')
    if _os.path.exists(_os.path.join(_f,'geodetic')):
        datapath = [ _f ]
        measurespath = _f
    else:
        datapath = [ ]
        measurespath = _os.path.expanduser("~/.casa/measures")
else:
    datapath = [ ]
    measurespath = _os.path.expanduser("~/.casa/measures")

cachedir = '~/.casa'

# automatically populate the measurespath[0] location if not already done
populate_data = True

# automatically update measures data if not current (measurespath must be user-writable)
measures_update = True

# log file path/name
logfile='casa-%s.log' % _time.strftime("%Y%m%d-%H%M%S", _time.gmtime())

# do not create a log file when True, If True, then any logfile value is ignored and there is no log file
nologfile = False

# print log output to terminal when True (in addition to any logfile and CASA logger)
log2term = False

# do not start the CASA logger when True
nologger = False

# avoid starting GUI tools when True. If True then the CASA logger is not started even if nologger is False
nogui = False

# the IPython prompt color scheme. Must be one of "Neutral", "NoColor", "Linux" or "LightBG", default "Neutral"
colors = "Neutral"

# startup without a graphical backend if True
agg = False

# attempt to load the pipeline modules and set other options appropriate for pipeline use if True
pipeline = False

# create and use an IPython log in the current directory if True
iplog = False

# allow anonymous usage reporting
telemetry_enabled = True

# location to place telemetry data prior to reporting
telemetry_log_directory = _os.path.expanduser("~/.casa/telemetry")

# maximum size of telemetry recording
telemetry_log_limit = 20480

# telemetry recording size that triggers a report
telemetry_log_size_interval = 60

# telemetry recording report frequency
telemetry_submit_interval = 604800

# allow anonymous crash reporting
crashreporter_enabled = True

# include the user's local site-packages in the python path if True. May conflict with CASA modules
user_site = False
