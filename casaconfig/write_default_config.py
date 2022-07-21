# Copyright 2021 AUI, Inc. Washington DC, USA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
this module will be included in the api
"""
import argparse
import os
import re
import time   # needed by argparse
import pkg_resources
from . import _config_defaults
from . import config


def write_default_config(name, **kwargs):
    """
    write default configuration file

    Parameters
       - name (str) - output filename to write configuration to
       - \*\*kwargs - modify the configuration option specified by keyword to value specified in variable (i.e. telemetry_enabled = True).
         Keywords that don't exist in the default list are ignored.

    Returns
       None

    """
    name = os.path.expanduser(name)

    # create directory if necessary
    if ('/' in name) and (name.rindex('/') > 0) and (not os.path.exists(name[:name.rindex('/')])):
        os.system('mkdir %s' % name[:name.rindex('/')])

    # find config variable names
    __default_names = [ x for x in dir(_config_defaults) if not x.startswith('_') ]

    # generate default values
    __defaults = { k: getattr(config,k) for k in __default_names }

    # replace config values with **kwargs
    for k,v in kwargs.items( ):
        if k in __defaults:
            __defaults[k] = v

    # read static default contents
    with open(pkg_resources.resource_filename('casaconfig', '_config_defaults_static.py'), 'r') as fid:
        config_contents = fid.read()

    # modify specified keys
    for key, value in __defaults.items():
        config_contents = re.sub('%s\s*\=\s*.+?\n'%key, r'%s = %s\n'%(key,repr(value)), config_contents, flags=re.DOTALL)

    # write to specified location
    with open(name, 'w') as fid:
        print('writing %s' % name)
        fid.write(config_contents)



######################################
## command line application
######################################
def main():
    parser = argparse.ArgumentParser(prog='write_default_config', description='write out a default casa configuration file')
    parser.add_argument('outfile', help='output filename to write the configuration to')

    # open the default values inside this package and parse it to extract the default parameters/values
    with open(pkg_resources.resource_filename('casaconfig', '_config_defaults.py'), 'r') as fid:
        config = fid.read()
        options = re.findall('\n\#(.+?)\n\s*(\S+?)\s*\=\s*(.+?)\n', config, flags=re.DOTALL)

    for option in options:
        parser.add_argument('--%s' % option[1], help=option[0].strip())

    args = vars(parser.parse_args())
    set_args = []
    for arg in args:
        if (arg != 'outfile') and (args[arg] is not None):
            try:
                set_args += [(arg, eval(args[arg]))]
            except:
                set_args += [(arg, args[arg])]
    set_args = dict(set_args)
    write_default_config(args['outfile'], **set_args)
