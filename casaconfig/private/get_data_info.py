# Copyright 2023 AUI, Inc. Washington DC, USA
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

def get_data_info(path=None, logger=None):
    """
    Get the summary information on the 3 types of data managed by casaconfig.

    The return value is a dictionary by type of of data : 'casarundata', 'measures',
    and 'release'.

    The path is the location to use to search for the installed release information.
    The path argument defaults to config.measurespath when not set.

    For each type the value is a dictionary of 'version' and 'date' where
    version is the version string and date is the date when it was installed.
    These values are taken from the readme.txt file for each type.

    The 'release' type is from the release_data_readme.txt file which is copied
    into place when a modular CASA is built. It is the release.txt for the
    data appropriate for that module CASA release and it used by the "--reference-testing"
    command line option for casaconfig. That allows casaconfig to install that
    casarundata version for testing purposes. The release information does not depend 
    on the path argument.

    If path is empty or does not exist then the return value for the 'casarundata' and
    'measures' types is None.

    If no readme.txt file can be found at path but the contents of path have the directories
    expected for casarundata then the version returned for 'casarundata' is 'unknown' and
    the date is an empty string. The path location may contain casarundata from a legacy
    installation of CASA data. CASA may be able to use the files at this location but they
    can not be maintained by casaconfig.

    If no readme.txt file can be found for the measures at path/geodetic but both the geodetic
    and ephemeris directories are present in path then the version returned for 'measures' is
    'unknown' and the date is an empty string. The path location may contain measures data from
    a legacy installation of CASA data. CASA may be able to use any measures tables at this
    location by they can not be maintained by casaconfig.

    If no casadata release information is found the returned
    value for 'release' is None and the "--reference-testing" option will not do anything
    for this installation of casaconfig. This will be the case for a modular installation.

    If path has not been set (has a value of None) then the returned value will be None. This
    likely means that a casasiteconfig.py exists but has not yet been edited to set measurespath.

    Parameters
       - path (str) - Folder path to find the casarundata and measures data information. If not set then config.measurespath is used.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the the terminal.
    
    Returns
       dict - a dictionary by type, 'casarundata', 'measures', 'release' where each type is a dictionary containing 'version' and 'date'. A return value of None indicates path is unset. A value of None for that type means no information could be found about that type.
    """

    # when None is returned, path wasn't set
    result = None

    import os
    import importlib.resources
    from .print_log_messages import print_log_messages

    if path is None:
        from .. import config as _config
        path = _config.measurespath

    if path is None:
        # it's not being set in a config file, probably casasiteconfig.py is being used but has not been edited
        print_log_messages('path is None and has not been set in config.meausrespath (probably casasiteconfig.py). Provide a valid path and retry.', logger, True)

        return None
    
    path = os.path.abspath(os.path.expanduser(path))

    result = {'casarundata':None, 'measures':None, 'release':None}

    # casarundata and measures 

    if os.path.isdir(path) and (len(os.listdir(path))>0):
        # there's something at path, look for the casarundata readme
        datareadme_path = os.path.join(path,'readme.txt')
        if os.path.exists(datareadme_path):
            # the readme exists, get the info
            try:
                with open(datareadme_path, 'r') as fid:
                    readme = fid.readlines()
                    currentVersion = readme[1].split(':')[1].strip()
                    currentDate = readme[2].split(':')[1].strip()
                    # this one is just a check that there's the manifest is probably also OK
                    line4 = readme[4]
                    result['casarundata'] = {'version':currentVersion, 'date':currentDate}
            except:
                result['casarundata'] = {'version':'error', 'date':''}
        else:
            # does it look like it's probably casarundata?
            expected_dirs = ['alma','catalogs','demo','ephemerides','geodetic','gui','nrao']
            ok = True
            for d in expected_dirs:
                if not os.path.isdir(os.path.join(path,d)): ok = False
            if ok:
                # probably casarundata
                result['casarundata'] = {'version':'unknown', 'date':''}
            else:
                # probably not casarundata
                result['casarundata'] = {'version':'not casarundata', 'date':''}

        # look for the measures readme
        measuresreadme_path = os.path.join(path,'geodetic/readme.txt')
        if os.path.exists(measuresreadme_path):
            # the readme exists, get the info
            try:
                with open(measuresreadme_path, 'r') as fid:
                    readme = fid.readlines()
                    currentVersion = readme[1].split(':')[1].strip()
                    currentDate = readme[2].split(':')[1].strip()
                    result['measures'] = {'version':currentVersion, 'date':currentDate}
            except:
                result['measures'] = {'version':'error', 'date':''}
        else:
            # does it look like it's probably measuresdata?
            # path should have ephemerides and geodetic directories
            if os.path.isdir(os.path.join(path,'ephemerides')) and os.path.isdir(os.path.join(path,'geodetic')):
                result['measures'] = {'version':'unknown', 'date':''}
            else:
                # probably not measuresdata
                result['measures'] = {'version':'not measures', 'date':''}

    # release data versions
    if importlib.resources.is_resource('casaconfig','release_data_readme.txt'):
        try:
            readme_lines = importlib.resources.read_text('casaconfig','release_data_readme.txt').split('\n')
            currentVersion = readme_lines[1].split(':')[1].strip()
            currentDate = readme_lines[2].split(':')[1].strip()
            result['release'] = {'version':currentVersion, 'date':currentDate}
        except:
            result['release'] = {'version':'error', 'date':''}
    else:
        # no release information available, probably a modular install only
        # leave 'release' as None
        pass

    return result
