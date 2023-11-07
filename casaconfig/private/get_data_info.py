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

    The casarundata and measures type value are each a dictionary of 'version' 
    and 'date' where version is the version string and date is the date when it  
    was installed These values are taken from the readme.txt file for each type.

    The 'release' type is from the release_data_readme.txt file which is copied
    into place when a modular CASA is built. It consists of a dictionary of
    'casarundata' and 'measures' where the values are the version strings for each
    type of data for this release. That allows casaconfig to install that
    casarundata version for testing purposes. The release information does not depend 
    on the path argument since it is found in the casaconfig module.

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

    If no casadata release information is found or the contents are unexpected the returned
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
    from .read_readme import read_readme

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
            result['casarundata'] = {'version':'error', 'date':''}
            readmeContents = read_readme(datareadme_path)
            if readmeContents is not None:
                currentVersion = readmeContents['version']
                currentDate = readmeContents['date']
                # this one is just a check that the manifest at least exists
                if len(readmeContents['extra']) > 0:
                    result['casarundata'] = {'version':currentVersion, 'date':currentDate}
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
            result['measures'] = {'version':'error', 'date':''}
            readmeContents = read_readme(measuresreadme_path)
            if readmeContents is not None:
                currentVersion = readmeContents['version']
                currentDate = readmeContents['date']
                result['measures'] = {'version':currentVersion,'date':currentDate}
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
            casarundataVersion = None
            measuresVersion = None
            ok = True
            reason = None
            readme_lines = importlib.resources.read_text('casaconfig','release_data_readme.txt').split('\n')
            for readmeLine in readme_lines:
                # lines must contain something and not start with #
                if len(readmeLine) > 0 and readmeLine[0] != '#':
                    splitLine = readmeLine.split(':')
                    if len(splitLine) == 2:
                        lineType = splitLine[0].strip()
                        lineVers = splitLine[1].strip()
                        if lineType == 'casarundata':
                            if casarundataVersion is not None:
                                ok = False
                                reason = "duplicate casarundata lines"
                                break
                            casarundataVersion = lineVers
                        elif lineType == 'measures':
                            if measuresVersion is not None:
                                ok = False
                                reason = "duplicate measures lins"
                                break
                            measuresVersion = lineVers
                        else:
                            ok = False
                            reason = "Unexpected type : %s" % lineType
                            break
                    else:
                        ok = False
                        reason = "Missing or too many ':' separators"
            if (casarundataVersion is None or measuresVersion is None) and ok:
                ok = False
                reason = "missing one or more version strings for expected casarundata and measures types"

            if not ok:
                print_log_messages("Incorrectly formatted release_data_readme.txt. %s" % reason, logger, True)
                # leave 'release' as None
            else:
                result['release'] = {'casarundata':casarundataVersion, 'measures':measuresVersion}
        except:
            print("Unexpected error reading release_data_readme.txt")
            # leave 'release' as None
    else:
        # no release information available, probably a modular install only
        # leave 'release' as None
        pass

    return result
