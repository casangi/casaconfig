# Copyright 2020 AUI, Inc. Washington DC, USA
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


def set_casacore_path(path=None):
    """
    Set the path in .casarc to the desired data directory

    Parameters
       - path (string=None) - path to the desired data directory. Default None uses the included data directory from this package

    Returns
       None

    """
    import pkg_resources
    import os
    import re
    import sys
    
    if path is None: path = pkg_resources.resource_filename('casaconfig', 'data/')
    path = os.path.abspath(os.path.expanduser(path))

    rctext = 'measures.directory: %s\n' % path

    casarc = os.path.expanduser('~/.casarc')
    
    # get the current .casarc contents if it exists
    # set/replace the path to the geodetic folder
    if os.path.exists(casarc):
        with open(casarc, 'r') as fid:
            print('found existing .casarc...', file = sys.stderr )
            oldtxt = fid.read()
        if 'measures.directory' in oldtxt:
            rctext = re.sub('measures.directory: .+?\n', '%s'%rctext, oldtxt, flags=re.DOTALL)
        else:
            rctext = oldtxt.strip() + '\n' + rctext
    # write out new .casarc file
    with open(casarc, 'w') as fid:
        print('writing %s...' % casarc)
        fid.write(rctext)
        
    return
