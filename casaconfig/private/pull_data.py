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

def pull_data(path=None, version=None, force=False, logger=None):
    """
    Pull the casarundata contents from the CASA host and install it in path.

    The path must either contain a previously installed version of casarundata 
    or it must not exist or be empty.

    If path is None then config.measurespath will be used.

    If version is None (the default) then the most recent version is pulled.

    If version is "release" then the version associated with the release in 
    the dictionary returned by get_data_info is used. If there is no release
    version information known then an error message is printed and nothing is
    updated.

    A text file (readme.txt at path) records the version string, the date
    when that version was installed in path, and the files installed into path.
    This file is used to determine if the contents are a previously installed 
    version.

    If the version to be pulled matches the version in the readme.txt file then this 
    function does nothing unless force is true. No error messages will result when the
    version already matches what was previously installed (no installation is then
    necessary unless force is True).

    The measures tables included in casarundata will typically 
    not be the most recent version. To get the most recent measures data, measures_update
    should be used after pull_data.

    If path contains a previously installed version then all of the files listed in 
    the manifest part of the readme.txt file are first removed from path.

    A file lock is used to prevent more than one data update (pull_data, measures_update,
    or data_update) from updating any files in path at the same time. When locked, the
    lock file (data_update.lock in path) contains information about the process that
    has the lock. When pull_data gets the lock it checks the readme.txt file in path
    to make sure that a copy of the data should be pulled (the version doesn't match what
    was requested). If force is True an update always happens. If the lock file is not
    empty then a previous update of path (pull_data, data_update, or measures_update)
    did not exit as expected and the contents of path are suspect. In that case, pull_data
    will report that as an error and nothing will be updated. The lock file can be checked
    to see the details of when that file was locked. The lock file can be removed and
    pull_data can then be used to install the desired version. It may be safest in that case
    to remove path completely or use a different path and run pull_data to install 
    a fresh copy of the desired version.

    Some of the tables installed by pull_data are only read when casatools starts. Use of 
    pull_data should typically be followed of CASA by a restart so that 
    any changes are seen by the tools and tasks that use this data.

    Parameters
       - path (str) - Folder path to place casarundata contents. It must be empty or not exist or contain a valid, previously installed version. If not set then config.measurespath is used.
       - version (str=None) - casadata version to retrieve. Default None gets the most recent version.
       - force (bool=False) - If True, re-download the data even when the requested version matches what is already installed. Default False will not download data if the installed version matches the requested version.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Messages are always written to the terminal. Default None does not write any messages to a logger.

    Returns
       None

    """

    import os

    from .data_available import data_available
    from .print_log_messages import print_log_messages
    from .get_data_lock import get_data_lock
    from .do_pull_data import do_pull_data
    from .get_data_info import get_data_info
    from .read_readme import read_readme

    if path is None:
        from .. import config as _config
        path = _config.measurespath

    if path is None:
        # it's not being set in a config file, probably casasiteconfig.py is being use but has not been edited
        print_log_messages('path is None and has not been set in config.measurespath (probably casasiteconfig.py). Provide a valid path and retry.', logger, True)
        return

    path = os.path.expanduser(path)
    readme_path = os.path.join(path, 'readme.txt')

    installed_files = []
    available_data = None
    currentVersion = None
    currentDate = None
    
    # attempt a pull if path does not exist or is empty:
    do_pull = (not os.path.exists(path)) or (len(os.listdir(path))==0)
    if not do_pull:
        # if the readme_path exists, find the current version, install date, and installed files
        if os.path.exists(readme_path):
            readmeInfo = read_readme(readme_path)
            if readmeInfo is not None:
                currentVersion = readmeInfo['version']
                currentDate = readmeInfo['date']
                installed_files = readmeInfo['extra']
            else:
                print_log_messages('destination path is not empty and the readme.txt file found there could not be read as expected', logger, True)
                print_log_messages('choose a different path or empty this path and try again', logger, True)
                # no lock has been set yet, safe to simply return here
                return

            if (len(installed_files) == 0):
                # this shouldn't happen
                print_log_messages('destination path is not empty and the readme.txt file found there did not contain the expected list of installed files', logger, True)
                print_log_messages('choose a different path or empty this path and try again', logger, True)
                # no lock as been set yet, safe to simply return here
                return
            
            # the readme file looks as expected, pull if the version is different or force is true
            if version is None:
                # use most recent available
                available_data = data_available()
                version = available_data[-1]
            do_pull = (version!=currentVersion) or force

            if not do_pull:
                # it's already at the expected version and force is False, nothing to do
                # safe to return here, no lock has been set
                return
        else:
            # path exists and is not empty
            print_log_messages('destination path exists, is not empty, and does not contain the expected readme.txt file', logger, True)
            print_log_messages('choose a different path or empty this path and try again', logger, True)
            # no lock has been set yet, safe to simply return here
            return

    # a pull will happen, unless the version string is not available

    if available_data is None:
        available_data = data_available()

    if version is None:
        # need a version, use most recent available
        version = available_data[-1]

    expectedMeasuresVersion = None
    if version is 'release':
        # use the release version from get_data_info
        releaseInfo = get_data_info()['release']
        if releaseInfo is None:
            print_log_messages('No release info found, pull_data can not continue', logger, True)
            return
        version = releaseInfo['casarundata']
        expectedMeasuresVersion = releaseInfo['measures']

    if version not in available_data:
        print_log_messages('version %s not found on CASA server, use casaconfig.data_available for a list of casarundata versions' % version, logger, True)
        return

    if not os.path.exists(path):
        # make dirs all the way down path if possible
        os.makedirs(path)

    # lock the data_update.lock file
    lock_fd = None
    try:
        print_log_messages('pull_data using version %s, acquiring the lock ... ' % version, logger)

        lock_fd = get_data_lock(path, 'pull_data')
        # if lock_fd is None it means the lock file was not empty - because we know that path exists at this point
        if lock_fd is None:
            print_log_messages('The lock file at %s is not empty.' % path, logger, True)
            print_log_messages('A previous attempt to update path may have failed or exited prematurely.', logger, True)
            print_log_messages('It may be best to do a fresh pull_data on that location.', logger, True)
            print_log_messages('Remove the lock file and set force to True with the desired version (default to the most recent).', logger, True)
            return
        
        do_pull = True
        if not force and os.path.exists(readme_path):
            # the readme file needs to be reread here
            # it's possible that another process had path locked and updated the readme file with new information
            readmeInfo = read_readme(readme_path)
            if readmeInfo is not None:
                currentVersion = readmeInfo['version']
                currentDate = readmeInfo['date']
                if ((currentVersion == version) and (not force)):
                    if expectedMeasuresVersion is not None:
                        # this is a release pull and the measures version must also match
                        # start off assuming a pull is necessary
                        do_pull = True
                        measures_readme_path = os.path.join(path,'geodetic/readme.txt')
                        if os.path.exists(measures_readme_path):
                            measuresReadmeInfo = read_readme(measures_readme_path)
                            if measuresReadmeInfo is not None:
                                measuresVersion = measuresReadmeInfo['version']
                                if measuresVersion == expectedMeasuresVersion:
                                    # no pull is necessary
                                    do_pull = False
                                    print_log_messages('pull_data requested "release" versions of casarundata and measures are already installed.', logger)
                            # otherwise the measures readme info is suspect and the pull should happen
                    else:
                        # nothing to do here, already at the expected version and a pull is not being forced
                        do_pull = False
                        print_log_messages('pull_data requested version is already installed.', logger)

                if do_pull:
                    # make sure the copy of installed_files is the correct one
                    installed_files = readmeInfo['extra']
                    if len(installed_files) == 0:
                        # this shoudn't happen, do not do a pull
                        do_pull = False
                        print_log_messages('destination path is not empty and the readme.txt file found there did not contain the expected list of installed files', logger, True)
                        print_log_messages('This should not happen unless multiple sessions are trying to pull_data at the same time and one experienced problems or was done out of sequence', logger, True)
                        print_log_messages('Check for other updates in process or choose a different path or clear out this path and try again', logger, True)                    
            else:
                # this shouldn't happen, do not do a pull
                do_pull = False
                print_log_messages('Unexpected error reading readme.txt file during pull_data, can not safely pull the requested version', logger, True)
                print_log_messages('This should not happen unless multiple sessions are trying to pull_data at the same time and one experienced problems or was done out of sequence', logger, True)
                
        if do_pull:
            do_pull_data(path, version, installed_files, currentVersion, currentDate, logger)
                        
        # truncate the lock file
        lock_fd.truncate(0)
        
    except Exception as exc:
        print_log_messages('ERROR! : Unexpected exception while populating casarundata version %s to %s' % (version, path), logger, True)
        print_log_messages('ERROR! : %s' % exc, logger, True)
        # leave the contents of the lock file as is to aid in debugging
        # import traceback
        # traceback.print_exc()

    # if the lock file is not closed, do that now to release the lock
    if lock_fd is not None and not lock_fd.closed:
        lock_fd.close()
        
    return
