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
DO NOT ADD new configuration variables here. Instead, add them in
config_defaults_static.py (found in the same directory as this file).
'''
import os as _os
import sys as _sys
import time as _time
import pkgutil as _pkgutil

from .get_argparser import get_argparser as __get_argparser

## get the ArgumentParser with the arguments needed by casaconfig, help is turned off
## this is used to supply command line configuration variales to the static defaults
## specification.
__parser = __get_argparser()
__flags,__args = __parser.parse_known_args(_sys.argv)

def _globals( ):
    return globals()

exec( open(_os.path.join(_os.path.dirname(__file__),'config_defaults_static.py')).read( ), globals( ) )

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

