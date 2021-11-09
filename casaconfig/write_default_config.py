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


def write_default_config(name, **kwargs):
    """
    write default configuration file

    Parameters
       - name (str) - output filename to write configuration to
       - **kwargs - modify the configuration option specified by keyword to value specified in variable (i.e. telemetry_enabled = True).
       Keywords that don't exist in the default list are ignored.

    Returns
       None

    """
    import os
    import re
    import pkg_resources

    name = os.path.expanduser(name)

    # create directory if necessary
    if ('/' in name) and (name.rindex('/') > 0) and (not os.path.exists(name[:name.rindex('/')])):
        os.system('mkdir %s' % name[:name.rindex('/')])

    # read default config.py from package installation
    with open(pkg_resources.resource_filename('casaconfig', 'config.py'), 'r') as fid:
        config = fid.read()

    # modify specified keys
    for key, value in kwargs.items():
        config = re.sub('%s\s*\=\s*.+?\n'%key, r'%s = %s\n'%(key,value), config, flags=re.DOTALL)

    # write to specified location
    with open(name, 'w') as fid:
        fid.write(config)