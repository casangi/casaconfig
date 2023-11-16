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

def data_update(path=None, version=None, force=False, logger=None, auto_update_rules=False):
    """
    Check for updates to the installed casarundata and install the update or change to 
    the requested version when appropriate.
    
    A text file (readme.txt at path) records the version string, the date 
    when that version was installed in path, and the files installed into path. That file
    must already exist in path in order to use this function. Use pull_data to install
    casarundata into a new location.

    If path is None then config.measurespath is used.

    If the version is None (the default) then the most recent version returned by 
    data_available is used.

    If version is "release" then the version associated with the release in 
    the dictionary returned by get_data_info is used. If there is no release
    version information known then an error message is printed and nothing is
    updated.

    If the version requested matches the one in the readme.txt file at path then this function does
    nothing unless force is True.

    If a specific version is not requested (the default) and the date in the readme.txt file
    at path is today, then this function does nothing unless force is True even if there is a more
    recent version available from the CASA server.

    When auto_update_rules is True then path must be owned by the user, force must be
    False and the version must be None. This is used during casatools initialization when
    data_auto_update is True. Automatic updating happens during casatools initialization
    so that the updated casarundata and measures are in place before any tool needs to use them.

    If an update is to be installed the previously installed files, as listed in the 
    readme.txt file at path, are removed before the contents of the version 
    being installed are unpacked. This includes the set of measures tables
    that are part of that casarundata version. A data update is typically followed by a
    measures_update to ensure that the most recent measures data are installed.

    A file lock is used to prevent more that one data update (pull_data, measures_update,
    or data_update) from updating any files in path at the same time. When locked, the 
    lock file (data_update.lock in path) contains information about the process that
    has the lock. When data_update gets the lock it checks the readme.txt file in path
    to make sure that an update is still necessary (if force is True then an update 
    always happens). If the lock file is not empty then a previous update of path (pull_data,
    data_update, or measures_update) did not exit as expected and the contents of path are
    suspect. In that case, an error will be reported and nothing will be updated. The lock
    file can be checked to see the details of when that file was locked. The lock file can be
    removed and data_update can be tried again. It may be safest in that case to remove path
    completely or use a different path and use pull_data to install a fresh copy of the
    desired version.

    Some of the tables installed by data_update are only read when casatools starts. Use of 
    data_update should typically be followed by a restart of CASA so that any changes are seen by
    the tools and task that use this data.

    **Note:** data_update requires that the expected readme.txt file already exists at the top-level
    directory at path. If the file does not exist or can not be interpreted as expected then
    data_update will return without updating any data.

    **Note:** if auto_update_rules is True the user must own path (in addition to having read and
    write permissions there). The version must then also be None and the force option must be False.

    **Note:** the most recent casarundata may not include the most recent measures data. A data_update
    is typically followed by a measures_update.

    Parameters
       - path (str=None) - Folder path to update. Must contain a valid readme.txt. If not set then config.measurespath is used.
       - version (str=None) - Version of casarundata to retrieve (usually in the form of casarundata-x.y.z.tar.gz, see data_available()). Default None retrieves the latest.
       - force (bool=False) - If True, always re-download the casarundata. Default False will not download casarundata if already updated today unless the version parameter is specified and different from what was last downloaded.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal.
       - auto_update_rules (bool=False) - If True then the user must be the owner of path, version must be None, and force must be False.
        
    Returns
       None
    
    """

    import os
    from datetime import datetime

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

    if auto_update_rules:
        if version is not None:
            print_log_messages('auto_update_rules requires that version be None', logger, True)
            return
        if force:
            print_log_messages('force must be False when auto_update_rules is True', logger, True)
            return
        if (not os.path.isdir(path)) or (os.stat(path).st_uid != os.getuid()):
            print_log_messages('path must exist as a directory and it must be owned by the user when auto_update_rules is True', logger, True)
            return        

    # readme must exist
    if not os.path.exists(readme_path):
        print_log_messages('No readme.txt file found at path. Nothing updated or checked.', logger, True);
        return

    # path must be writable with execute bit set
    if (not os.access(path, os.W_OK | os.X_OK)) :
        print('No permission to write to path, cannot update : %s' % path, file=sys.stdout)
        if logger is not None: logger.post('No permission to write to path, cannot update : %s' % path, 'ERROR')
        return
    
    # try and digest the readme file

    installed_files = []
    currentVersion = []
    currentDate = []
    dataReadmeInfo = read_readme(readme_path)
    if dataReadmeInfo is not None:
        currentVersion = dataReadmeInfo['version']
        currentDate = dataReadmeInfo['date']
        installed_files = dataReadmeInfo['extra']
    else:
        print_log_messages('The readme.txt file at path could not be read as expected', logger, True)
        print_log_messages('choose a different path or empty this  path and try again using pull_data', logger, True)
        # no lock has been set yet, safe to simply return here
        return

    if (len(installed_files) == 0):
        # this shouldn't happen
        print_log_messages('The readme.txt file at path did not contain the expected list of installed files', logger, True)
        print_log_messages('choose a different path or empty this path and try again using pull_data', logger, True)
        # no lock has been set yet, safe to simply return here
        return

    today_string = datetime.today().strftime('%Y-%m-%d')
    if version is None and force is False and currentDate == today_string:
        # if version is None, currentDate is today and force is False then return without checking for any newer versions
        print_log_messages('data_update current casarundata detected in %s, using version %s' % (path, currentVersion), logger)
        # no lock has been set yet, safe to simply return here
        return

    available_data = data_available()
    requestedVersion = version

    if requestedVersion is None:
        requestedVersion = available_data[-1]

    expectedMeasuresVersion = None
    if requestedVersion == 'release':
        # use the release version from get_data_info
        releaseInfo = get_data_info()['release']
        if releaseInfo is None:
            print_log_messages('No release info found, pull_data can not continue', logger, True)
            return
        requestedVersion = releaseInfo['casarundata']
        expectedMeasuresVersion = releaseInfo['measures']

    if requestedVersion not in available_data:
        print_log_messages('Requested casarundata version %s was not found. See available_data for a list of available casarundata versions.' % requestedVersion)
        # no lock has been set yet, safe to simply return here
        return

    # don't update if force is false and the requested version is already installed
    if force is False and (currentVersion == requestedVersion):
        if expectedMeasuresVersion is not None:
            # the 'release' version has been requested, need to check the measures version
            # assume a force is necessary until the measures version is known to be OK
            force = True
            measures_readme_path = os.path.join(path,'geodetic/readme.txt')
            if os.path.exists(measures_readme_path):
                measuresReadmeInfo = read_readme(measures_readme_path)
                if measuresReadmeInfo is not None:
                    measuresVersion = measuresReadmeInfo['version']
                    if measuresVersion == expectedMeasuresVersion:
                        # it's OK, do not force
                        force = False
                # if measuresReadmeInfo is None then that's a problem and force remains True
            if not force:
                print_log_messages('data_update requested "release" version of casarundata and measures are already installed.', logger)
                # no lock has been set yet, safe to simply return here
                return
        else:
            # normal usage, ok to return now
            print_log_messages('Requested casarundata is installed in %s, using version %s' % (path, currentVersion), logger)
            # no lock has been set yet, safe to simply return here
            return

    # an update appears necessary

    lock_fd = None
    try:
        print_log_messages('data_update using version %s, acquiring the lock ... ' % requestedVersion, logger)

        lock_fd = get_data_lock(path, 'data_update')
        # if lock_fd is None it means the lock file was not empty - because we know that path exists at this point
        if lock_fd is None:
            print_log_messages('The lock file at %s is not empty.' % path, logger, True)
            print_log_messages('A previous attempt to update path may have failed or exited prematurely.', logger, True)
            print_log_messages('Remove the lock file and set force to True with the desired version (default to most recent).', logger, True)
            print_log_messages('It may be best to completely repopulate path using pull_data and measures_update.', logger, True)
            return

        do_update = True
        # it's possible that another process had path locked and updated the readme with new information, re-read it
        dataReadmeInfo = read_readme(readme_path)
        if dataReadmeInfo is not None:
            currentVersion = dataReadmeInfo['version']
            currentDate = dataReadmeInfo['date']
            installedFiles = dataReadmeInfo['extra']
            if ((currentVersion == requestedVersion) and (not force)):
                if expectedMeasuresVersion is not None:
                    # this is a 'release' update request, need to check that the measures version is also now OK
                    measures_readme_path = os.path.update(path,'geodetic/readme.txt')
                    if os.path.exists(measures_readme_path):
                        measuresReadmeInfo = read_readme(measures_readme_path)
                        if measuresReadmeInfo is not None:
                            measuresVersion = measuresReadmeInfo['version']
                            if measuresVersion == expectedMeasuresVersion:
                                do_update = False
                        # if measuresReadmeInfo is None there was a problem which requires a full update so do_update remains True
                    if not do_update:
                        print_log_messages('data update requested "release" version of casarundata and measures are already installed.', logger)
                else:
                    # nothing to do here, already at the expected version and an update is not being forced
                    do_update = False
                    print_log_messages('data_update requested version is already installed.', logger)
                    
            if do_update:
                # update is still on, check the manifest
                if len(installed_files) == 0:
                    # this shouldn't happen, do not do an update
                    do_update = False
                    print_log_messages('The readme.txt file read at path did not contain the expected list of installed files', logger, True)
                    print_log_messages('This should not happen unless multiple sessions are trying to update data at the same time and one experienced problems or was done out of sequence', logger, True)
                    print_log_messages('Check for other updates in process or choose a different path or clear out this path and try again using pull_data or update_all', logger, True)
        else:
            # this shouldn't happen, do not do an update
            do_update = False
            print_log_messages('Unexpected problem reading readme.txt file during data_update, can not safely update to the requested version', logger, True)
            print_log_messages('This should not happen unless multiple sessions are trying to update at the same time and one experienced problems or was done out of sequence', logger, True)
            print_log_messages('Check for other updates in process or choose a different path or clear out this path and try again using pull_data or update_all', logger, True)

    
        if do_update:
            do_pull_data(path, requestedVersion, installed_files, currentVersion, currentDate, logger)

        # truncate the lock file
        lock_fd.truncate(0)

    except Exception as exc:
        print_log_messages('ERROR! : Unexpected exception while populating casarundata version %s to %s' % (requestedVersion, path), logger, True)
        print_log_messages('ERROR! : %s' % exc, logger, True)
        # leave the contents of the lock file as is to aid in debugging
        # import traceback
        # traceback.print_exc()

    # if the lock file is not closed, do that now to release the lock
    if lock_fd is not None and not lock_fd.closed:
        lock_fd.close()
    
    return
