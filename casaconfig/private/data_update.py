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

def data_update(path=None, version=None, force=False, logger=None, auto_update_rules=False, verbose=None):
    """
    Check for updates to the installed casarundata and install the update or change to 
    the requested version when appropriate.

    The verbose argument controls the level of information provided when this function when the data
    are unchanged for expected reasons. A level of 0 prints and logs nothing. A
    value of 1 logs the information and a value of 2 logs and prints the information.

    The path must contain a previously installed version of casarundata.
    Use pull_data to install casarundata into a new path (empty or does not exist).
    
    If path is None then config.measurespath is used.

    If the version is None (the default) then the most recent version returned by 
    data_available is used.

    If version is "release" then the version associated with the release in 
    the dictionary returned by get_data_info is used. If there is no release
    version information available to casaconfig then an error message is printed 
    and nothing is updated. Release version information is only available in
    monolithic CASA installations.

    If a specific version is not requested (the default) and a check for the 
    versions available for installation at path has been done within the past
    24 hours then this function does nothing even if there is a more
    recent version available from the CASA server unless force is True.

    If force is True then the requested version (or the latest version available
    now) is installed even if that version is already installed or a check for the
    latest version has been done within the past 24 hours.

    A text file (readme.txt at path) records the version string, the date 
    when that version was installed in path, and the files installed into path. That file
    must already exist in path in order to use this function. Use pull_data to install
    casarundata into a new location.

    When auto_update_rules is True then path must be owned by the user, force must be
    False and the version must be None. This is used during casatools initialization when
    data_auto_update is True. Automatic updating happens during casatools initialization
    so that the updated casarundata and measures are in place before any tool needs to use them.

    If an update is to be installed the previously installed files, as listed in the 
    readme.txt file at path, are removed before the contents of the version 
    being installed are unpacked. If the measures contents of path have been updated since
    the previously installed version of casarundata then those updates will also be removed
    by this data update while preparing to install the requested version of casarundata (which
    includes a copy of the measures data that is likely older than today). A data update is 
    typically followed by a measures_update to ensure that the most recent measures data 
    are installed.

    A file lock is used to prevent more that one data update (pull_data, measures_update,
    or data_update) from updating any files in path at the same time. When locked, the 
    lock file (data_update.lock in path) contains information about the process that
    has the lock. When data_update gets the lock it checks the readme.txt file in path
    to make sure that an update is still necessary (if force is True then an update 
    always happens). If the lock file is not empty then a previous update of path (pull_data,
    data_update, or measures_update) did not exit as expected or is still in process (via a
    separate instance of CASA) and the contents of path may be suspect. In that case, 
    an error will be reported and nothing will be updated. The lock file can be checked to 
    see the details of when that file was locked. The lock file can be removed and data_update 
    can be tried again. It may be safest in that case to remove path completely or use a
    different path and use pull_data to install a fresh copy of the desired version.

    Some of the tables installed by data_update are only read when casatools starts. Use of 
    data_update except during CASA startup by the auto update proess  should typically be 
    followed by a restart of CASA so that any changes are seen by the tools and tasks that 
    use this data.

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
       - force (bool=False) - If True, always re-download the casarundata. Default False will not download casarundata if updated within the past day unless the version parameter is specified and different from what was last downloaded.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal.
       - auto_update_rules (bool=False) - If True then the user must be the owner of path, version must be None, and force must be False.
       - verbose (int) - Level of output, 0 is none, 1 is to logger, 2 is to logger and terminal, defaults to casaconfig_verbose in the config dictionary.
        
    Returns
       None
    
    Raises
       - casaconfig.AutoUpdatesNotAllowed - raised when path does not exist as a directory or is not owned by the user
       - casaconfig.BadLock - raised when the lock file was not empty when an attempt was made to obtain the lock
       - casaconfig.BadReadme - raised when the readme.txt file at path did not contain the expected list of installed files or was incorrectly formatted
       - casaconfig.NoReadme - raised when the readme.txt file is not found at path (path also may not exist)
       - casaconfig.NotWritable - raised when the user does not have permission to write to path
       - casaconfig.RemoteError - raised by data_available when the list of available data versions could not be fetched
       - casaconfig.UnsetMeasurespath - raised when path is None and measurespath has not been set in config.
       - Exception - raised when there was an unexpected exception while populating path

    """

    import os

    from casaconfig import data_available
    from casaconfig import pull_data
    from casaconfig import get_data_info
    from casaconfig import AutoUpdatesNotAllowed, BadReadme, BadLock, NoReadme, RemoteError, UnsetMeasurespath, NotWritable
    from .print_log_messages import print_log_messages
    from .get_data_lock import get_data_lock
    from .do_pull_data import do_pull_data

    if path is None:
        from .. import config as _config
        path = _config.measurespath

    if path is None:
        raise UnsetMeasurespath('data_update: path is None and has not been set in config.measurespath. Provide a valid path and retry.')
        return

    if verbose is None:
        from .. import config as _config
        verbose = _config.casaconfig_verbose

    # when a specific version is requested then the measures readme.txt that is part of that version
    # will get a timestamp of now so that default measures updates won't happen for a day unless the
    # force argument is used for measures_update
    namedVersion = version is not None

    path = os.path.expanduser(path)
    readme_path = os.path.join(path, 'readme.txt')

    if auto_update_rules:
        if version is not None:
            print_log_messages('data_update: auto_update_rules requires that version be None', logger, True)
            return
        if force:
            print_log_messages('data_update: force must be False when auto_update_rules is True', logger, True)
            return
        if (not os.path.isdir(path)) or (os.stat(path).st_uid != os.getuid()):
            raise AutoUpdatesNotAllowed("data_update: path must exist as a directory and it must be owned by the user, path = %s" % path)

    if not os.path.exists(readme_path):
        # path must exist and it must be empty in order to continue
        if not os.path.exists(path) or (len(os.listdir(path)) > 0):
            raise NoReadme('data_update: no casarundata readme.txt file found at %s. Nothing updated or checked.' % path);
        # ok to install a fresh copy, use pull_data directly
        return pull_data(path,version,force,logger,verbose)

    # path must be writable with execute bit set
    if (not os.access(path, os.W_OK | os.X_OK)) :
        raise NotWritable('data_update: No permission to write to %s, cannot update.' % path)
    
    # try and digest the readme file

    installed_files = []
    currentVersion = []
    currentDate = []
    ageRecent = False

    # already checked that path is OK, type is OK here, no need to trap for exceptions here
    dataReadmeInfo = get_data_info(path, logger, type='casarundata')
    
    if dataReadmeInfo is None or dataReadmeInfo['version'] == 'invalid':
        msgs = []
        msgs.append('The readme.txt file at path could not be read as expected')
        msgs.append('choose a different path or empty this  path and try again using pull_data')
        print_log_messages(msgs, logger, True)
        # no lock has been set yet, safe to simply return here
        return

    currentVersion = dataReadmeInfo['version']
    currentDate = dataReadmeInfo['date']
    installed_files = dataReadmeInfo['manifest']
    if dataReadmeInfo['age'] is not None:
        ageRecent = dataReadmeInfo['age'] < 1.0

    if currentVersion == 'unknown':
        msgs = []
        msgs.append('The data update path appears to be casarundata but no readme.txt file was found')
        msgs.append('A data update is not possible but CASA use of this data may be OK.')
        msgs.append('casaconfig must first install the casarundata in path for data_update to run as expected on that path')
        print_log_messages(msgs, logger, True)

    if (len(installed_files) == 0):
        # this shouldn't happen
        # no lock has been set yet, safe to raise this exception without worrying about the lock
        raise BadReadme('data_update: the readme.txt file at path did not contain the expected list of installed files')

    if version is None and force is False and ageRecent:
        # if version is None, the readme is less than 1 day old  and force is False then return without checking for any newer versions
        if verbose > 0:
            print_log_messages('data_update: version installed or checked less than 1 day ago, nothing updated or checked', logger, verbose=verbose)
        # no lock has been set yet, safe to simply return here
        return

    # this may raise a RemoteError, no need to catch that here but it may need to be caught upstream
    available_data = data_available()
    requestedVersion = version
    latestVersion = False

    if requestedVersion is None:
        latestVersion = True
        requestedVersion = available_data[-1]

    expectedMeasuresVersion = None
    if requestedVersion == 'release':
        # use the release version from get_data_info
        releaseInfo = get_data_info()['release']
        if releaseInfo is None:
            print_log_messages('No release info found, data_update can not continue', logger, True)
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
            measuresReadmeInfo = get_data_info(path, logger, type='measures')
            if measuresReadmeInfo is not None:
                measuresVersion = measuresReadmeInfo['version']
                if measuresVersion == expectedMeasuresVersion:
                    # it's OK, do not force
                    force = False
                # if measuresReadmeInfo is None then that's a problem and force remains True, this also catches 'invalid' and 'unknown' measures versions, which should not happen here
            if not force:
                if verbose > 0:
                    print_log_messages('data_update: requested "release" version of casarundata and measures are already installed.', logger, verbose=verbose)
                # no lock has been set yet, safe to simply return here
                return
        else:
            # normal usage, ok to return now
            if latestVersion:
                if verbose > 0:
                    print_log_messages('The latest version is already installed in %s' % path, logger, verbose=verbose)
                # touch the dates of the readme to prevent a future check on available data for the next 24 hours
                os.utime(readme_path)
            else:
                if verbose > 0:
                    print_log_messages('Requested casarundata version is already installed in %s, %s' % (path, currentVersion), logger, verbose=verbose)
                
            # no lock has been set yet, safe to simply return here
            return

    # an update appears necessary

    lock_fd = None
    clean_lock = True   # set to False if the contents are actively being update and the lock file should not be cleaned on exception
    try:
        print_log_messages('data_update using version %s, acquiring the lock ... ' % requestedVersion, logger)

        lock_fd = get_data_lock(path, 'data_update')
        # the BadLock exception that may happen here is caught below

        do_update = True
        # it's possible that another process had path locked and updated the readme with new information, re-read it
        dataReadmeInfo = get_data_info(path, logger, type='casarundata')
        if dataReadmeInfo is not None:
            currentVersion = dataReadmeInfo['version']
            currentDate = dataReadmeInfo['date']
            installedFiles = dataReadmeInfo['manifest']
            ageRecent = dataReadmeInfo['age'] < 1.0
            if ((currentVersion == requestedVersion) and (not force)):
                if expectedMeasuresVersion is not None:
                    # this is a 'release' update request, need to check that the measures version is also now OK
                    measuresReadmeInfo = get_data_info(path, logger, type='measures')
                    if measuresReadmeInfo is not None:
                        measuresVersion = measuresReadmeInfo['version']
                        if measuresVersion == expectedMeasuresVersion:
                            do_update = False
                    # if measuresReadmeInfo is None there was a problem which requires a full update so do_update remains True
                    if not do_update:
                        # always verbose here because the lock file is in use
                        print_log_messages('data update requested "release" version of casarundata and measures are already installed.', logger)
                else:
                    # nothing to do here, already at the expected version and an update is not being forced
                    if latestVersion:
                        # always verbose here because the lock file is in use
                        print_log_messages('The latest version is already installed, using version %s' % currentVersion, logger)
                        # touch the dates of the readme to prevent a future check on available data for the next 24 hours
                        os.utime(readme_path)
                    else:
                        # always verbose here because the lock file is in use
                        print_log_messages('requested version is already installed.', logger)
                    do_update = False
                    
            if do_update:
                # update is still on, check the manifest
                if len(installed_files) == 0:
                    # this shouldn't happen, do not do an update, raise the BadReadme exception, caught below and the lock cleaned up then
                    raise BadReadme('data_update: the readme.txt file at path did not contain the expected list of installed files')
        else:
            # this shouldn't happen
            raise BadReadme('data_update: unexpected problem reading readme.txt file during data update, can not safely update to the requested version')

        if do_update:
            # do not clean the lock file contents at this point unless do_pull_data returns normally
            clean_lock = False
            do_pull_data(path, requestedVersion, installed_files, currentVersion, currentDate, logger)
            clean_lock = True
            if namedVersion:
                # a specific version has been requested, set the times on the measures readme.txt to now to avoid
                # a default update of the measures data without using the force argument
                measuresReadmePath = os.path.join(path,'geodetic/readme.txt')
                os.utime(measuresReadmePath)

    except BadLock as exc:
        # the path is known to exist so this means that the lock file was not empty and it's not locked
        msgs = str(exc)
        msgs.append('data_update: the lock file at %s is not empty.' % path)
        msgs.append('A previous attempt to update path may have failed or exited prematurely.')
        msgs.append('Remove the lock file and set force to True with the desired version (default to most recent).')
        msgs.append('It may be best to completely re-populate path using pull_data and measures_update.')
        print_log_messages(msgs, logger, True)
        # reraise this
        raise

    except BadReadme as exc:
        # something is wrong in the readme after an update was triggered, this shouldn't happen, print more context reraise this
        msgs = str(exc)
        msgs.append('This should not happen unless multiple sessions are trying to update data at the same time and one experienced problems or was done out of sequence')
        msgs.append('Check for other updates in progress or choose a different path or clear out this path and try again using pull_data or update_all')
        print_log_messages(msgs, logger, True)
        raise

    except Exception as exc:
        msgs = []
        msgs.append('ERROR! : Unexpected exception while populating casarundata version %s to %s' % (requestedVersion, path))
        msgs.append('ERROR! : %s' % exc)
        print_log_messages(msgs, logger, True)
        raise

    finally:
        # make sure the lock file is closed and also clean the lock file if safe to do so, this is always executed
        if lock_fd is not None and not lock_fd.closed:
            if clean_lock:
                lock_fd.truncate(0)
            lock_fd.close()
    
    return
