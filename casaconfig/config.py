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
_config_defaults.py (found in the same directory as this file).
'''
from . import _config_defaults
import argparse as __argparse
import sys as __sys
import os as __os

## list of config variables
__defaults = [ x for x in dir(_config_defaults) if not x.startswith('_') ]

## look for arguments that affect casaconfig
__parser = __argparse.ArgumentParser( )
__parser.add_argument( "--noconfig", dest='noconfig', action='store_const', const=True, default=False,
                       help='do not load user config.py' )
__parser.add_argument( "--configpath",dest='configpath', default='~/.casa',
                            help='location for startup files, internal working files')
__flags,__args = __parser.parse_known_args(__sys.argv)
__user_config = [ ] if __flags.noconfig else [ __os.path.join(__flags.configpath,'config.py') ]

## files to be evaluated/loaded
__config_files = [ 'casaconfigsite', *__user_config ]
__loaded_config_files = [ __file__ ]

import pkgutil as __pkgutil

## evaluate config files
for __f in [ __os.path.expanduser(f) for f in __config_files ]:
    if __f.find('/') >= 0 and __os.path.exists(__f):
        ## config file is a fully qualified path
        exec(open(__f).read( ),_config_defaults._globals( ))
        __loaded_config_files.append( __f )
    else:
        ## config file is a package name
        __pkg = __pkgutil.get_loader(__f)
        if __pkg is not None:
            exec(open(__pkg.get_filename( )).read( ),_config_defaults._globals( ))
            __loaded_config_files.append( __pkg.get_filename( ) )


for __v in __defaults:
    globals()[__v] = getattr(_config_defaults,__v,None)

def load_history( ):
    return __loaded_config_files
