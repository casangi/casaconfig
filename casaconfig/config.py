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
Configuration state for all CASA python packages.
DO NOT ADD new configuration variables here. Instead, add them in
private/config_defaults_static.py.
'''
from .private import config_defaults as _config_defaults
import traceback as __traceback
import sys as __sys
import os as __os
import pkgutil as __pkgutil
from .private import io_redirect as _io
from .private.get_argparser import get_argparser as __get_argparser

## list of config variables
__defaults = [ x for x in dir(_config_defaults) if not x.startswith('_') ]

## get the ArgumentParser with the arguments needed by casaconfig, help is turned off
__parser = __get_argparser()
__flags,__args = __parser.parse_known_args(__sys.argv)
__user_config = [ ] if __flags.noconfig else [ __flags.configfile ]

## files to be evaluated/loaded
__config_files = [ 'casaconfigsite', *__user_config ]
__loaded_config_files = [ __file__ ]
__errors_encountered = { }

## evaluate config files
## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
## If the the execution mode of python is module execution (e.g. "python3 -m casatools") then
## the output from the configuration files is thrown away. Otherwise, all output from the
## configuration files is passed through. This allows for output from module execution to
## be used by scripts.
##
_module_execution = len(__sys.argv) > 0 and __sys.argv[0] == '-m'
with _io.all_redirected(to=__os.devnull) if _module_execution else _io.no_redirect( ):
    for __f in [ __os.path.expanduser(f) for f in __config_files ]:
        if __f.find('/') >= 0:
            if __os.path.exists(__f):
                 ## config file is a fully qualified path
                 try:
                     __orig = { k: _config_defaults._globals( )[k] for k in __defaults }
                     exec( open(__f).read( ), __orig )
                 except Exception as e:
                     __errors_encountered[__f] = __traceback.format_exc( )
                 else:
                     for __v in __defaults:
                         _config_defaults._globals( )[__v] = __orig[__v]
                     __loaded_config_files.append( __f )
        else:
            ## config file is a package name
            __pkg = __pkgutil.get_loader(__f)
            if __pkg is not None:
                try:
                    __orig = { k: _config_defaults._globals( )[k] for k in __defaults }
                    exec(open(__pkg.get_filename( )).read( ),__orig)
                except Exception as e:
                    __errors_encountered[__pkg.get_filename( )] = __traceback.format_exc( )
                else:
                    for __v in __defaults:
                        _config_defaults._globals( )[__v] = __orig[__v]
                    __loaded_config_files.append( __pkg.get_filename( ) )

# the names of config values that are path that need to be expanded here
__path_names = ["cachedir","datapath","measurespath","logfile","startupfile","telemetry_log_directory"]

for __v in __defaults:
    globals()[__v] = getattr(_config_defaults,__v,None)
    if (__v in __path_names) :
        # expand ~ or ~user constructs and make sure they are absolute paths
        if (type(globals()[__v]) is list) :
            vlist = list(map(__os.path.expanduser, globals()[__v]))
            vlist = list(map(__os.path.abspath,vlist))
            globals()[__v] = vlist
        else:
            globals()[__v] = __os.path.abspath(__os.path.expanduser(globals()[__v]))
                                             
def load_success( ):
    return __loaded_config_files
def load_failure( ):
    return __errors_encountered
