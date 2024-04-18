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

def pull_data(path=None, version=None, force=False, logger=None, verbose=None):
    """
    Pull the casarundata contents from the CASA host and install it in path.

    The verbose argument controls the level of information provided when this function when the data
    are unchanged for expected reasons. A level of 0 prints and logs nothing. A
    value of 1 logs the information and a value of 2 logs and prints the information.
  
    The path must either contain a previously installed version of casarundata 
    or it must not exist or be empty.

    If path is None then config.measurespath will be used.

    If version is None (the default) then the most recent version is pulled.

    If version is "release" then the version associated with the release in 
    the dictionary returned by get_data_info is used. If there is no release
    version information known then an error message is printed and nothing is
    checked or installed.

    If force is True then the requested version is installed even if that
    version is already installed.

    Results and errors are always printed. They are also logged to the logger
    if available.

    A text file (readme.txt at path) records the version string, the date
    when that version was installed in path, and the files installed into path.
    This file is used to determine if the contents are a previously installed 
    version. If path is not empty then this file must exist with the expected
    contents in order for pull_data to proceed.

    If the version to be pulled matches the version in the readme.txt file then 
    pull_data does nothing unless force is True. No error messages will result when the
    version already matches what was previously installed (no installation is then
    necessary unless force is True).

    The measures tables included in casarundata will typically not be the most 
    recent version. To get the most recent measures data, measures_update
    should be used after pull_data.

    If path contains a previously installed version then all of the files listed in 
    the manifest part of the readme.txt file are first removed from path. This ensures
    that files not present in the version being installed are removed in moving to the
    other version.

    A file lock is used to prevent more than one data update (pull_data, measures_update,
    or data_update) from updating any files in path at the same time. When locked, the
    lock file (data_update.lock in path) contains information about the process that
    has the lock. When pull_data gets the lock it checks the readme.txt file in path
    to make sure that a copy of the data should still be pulled (the version doesn't 
    match what was requested, or force is True). If the lock file is not
    empty then a previous update of path (pull_data, data_update, or measures_update)
    did not exit as expected and the contents of path are suspect. In that case, pull_data
    will report that as an error and nothing will be updated. The lock file can be checked
    to see the details of when that file was locked. The lock file can be removed and
    pull_data can then be used to install the desired version. It may be safest in that case
    to remove path completely or use a different path and run pull_data to install 
    a fresh copy of the desired version.

    Some of the tables installed by pull_data are only read when casatools starts. Use of 
    pull_data should typically be followed by a restart of CASA so that 
    any changes are seen by the tools and tasks that use this data.

    **Note:** When version is None (the default), data_available is always used to find out
    what versions are available. There is no check on when the data were last updated before
    calling data_available (as there is in the two update functions). 

    Parameters
       - path (str) - Folder path to place casarundata contents. It must be empty or not exist or contain a valid, previously installed version. If not set then config.measurespath is used.
       - version (str=None) - casadata version to retrieve. Default None gets the most recent version.
       - force (bool=False) - If True, re-download and install the data even when the requested version matches what is already installed. Default False will not download data if the installed version matches the requested version.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Messages are always written to the terminal. Default None does not write any messages to a logger.
       - verbose (int) - Level of output, 0 is none, 1 is to logger, 2 is to logger and terminal, defaults to casaconfig_verbose in the config dictionary.

    Returns
       None

    Raises
       - casaconfig.BadLock - raised when the lock file is not empty when a lock is requested
       - casaconfig.BadReadme - raised when the readme.txt file found at path does not contain the expected list of installed files or there was an unexpected change while the data lock is on
       - casaconfig.NotWritable - raised when the user does not have write permission to path
       - casaconfig.RemoteError - raised by data_available when the list of available data versions could not be fetched
       - casaconfig.UnsetMeasurespath - raised when path is None and and measurespath has not been set in config.

    """

    import os

    from casaconfig import data_available
    from casaconfig import get_data_info
    from casaconfig import UnsetMeasurespath, BadLock, BadReadme, NotWritable

    from .print_log_messages import print_log_messages
    from .get_data_lock import get_data_lock
    from .do_pull_data import do_pull_data

    if path is None:
        from .. import config as _config
        path = _config.measurespath

    if path is None:
        raise UnsetMeasurespath('path is None and has not been set in config.measurespath. Provide a valid path and retry.')

    # when a specific version is requested then the measures readme.txt that is part of that version
    # will get a timestamp of now so that default measures updates won't happen for a day unless the
    # force argument is used for measures_update
    namedVersion = version is not None

    path = os.path.expanduser(path)
    readme_path = os.path.join(path, 'readme.txt')

    installed_files = []
    available_data = None
    currentVersion = None
    currentDate = None
    
    # attempt a pull if path does not exist or is empty (except for any lock file, handled later)
    readmeInfo = get_data_info(path, logger, type='casarundata')
    do_pull = readmeInfo is None
    if not do_pull:
        # find the current version, install date, and installed files
        currentVersion = readmeInfo['version']
        currentDate = readmeInfo['date']
        installed_files = readmeInfo['manifest']

        if currentVersion == 'invalid':
            msgs = []
            msgs.append('destination path is not empty and this does not appear to be casarundata OR the readme.txt file found there could not be read as expected')
            msgs.append('choose a different path or empty this path and try again')
            print_log_messages(msgs, logger, True)
            # no lock has been set yet, safe to simply return here
            return

        if currentVersion == 'unknown':
            msgs = []
            msgs.append('destination path appears to be casarundata but no readme.txt file was found')
            msgs.append('no data will be installed but CASA use of this data may be OK. Choose a different path or delete this path to install new casarundata.')
            if force:
                msgs.append('force is True but there is no readme.txt found and the location is not empty, no data will be installed')
                msgs.append('Choose a different path or empty this path to install new casarundata')
            print_log_messages(msgs, logger, True)
            # no lock as been set yet, safe to simply return here
            return

        if (installed_files is None or len(installed_files) == 0):
            # this shouldn't happen
            # no lock has been set yet, safe to raise this exception without worrying about the lock
            raise BadReadme('pull_data: the readme.txt file at path did not contain the expected list of installed files')
            
        # the readme file looks as expected, pull if the version is different or force is true
        if version is None:
            # use most recent available
            # this may raise a RemoteError, no need to catch that here but it may need to be caught upstream
            available_data = data_available()
            version = available_data[-1]

        do_pull = (version!=currentVersion) or force

        if not do_pull:
            # it's already at the expected version and force is False, nothing to do
            # safe to return here, no lock has been set
            print_log_messages('pull_data: version is already at the expected version and force is False. Nothing was changed', logger, verbose=verbose)
            return
        
    # a pull will happen, unless the version string is not available

    if version is None:
        # need a version, use most recent available
        
        if available_data is None:
            # this may raise a RemoteError, no need to catch that here but it may need to be caught upstream
            available_data = data_available()
            
        version = available_data[-1]

    expectedMeasuresVersion = None
    if version == 'release':
        # use the release version from get_data_info
        releaseInfo = get_data_info()['release']
        if releaseInfo is None:
            print_log_messages('No release info found, pull_data can not continue', logger, True)
            return
        version = releaseInfo['casarundata']
        expectedMeasuresVersion = releaseInfo['measures']
    else:
        # requested version must be available
        if available_data is None:
            # this may raise a RemoteError, no need to catch that here but it may need to be caught upstream
            available_data = data_available()
            
        if version not in available_data:
            print_log_messages('version %s not found on CASA server, use casaconfig.data_available() for a list of casarundata versions' % version, logger, True)
            return

    if not os.path.exists(path):
        # make dirs all the way down path if possible
        os.makedirs(path)

    # path must be writable with execute bit set
    if (not os.access(path, os.W_OK | os.X_OK)) :
        raise NotWritable('pull_data: No permission to write to path, cannot update : %s' % path)

    # lock the data_update.lock file
    lock_fd = None
    clean_lock = True  # set to False if the contents are actively being update and the lock file should not be cleaned on exception
    try:
        print_log_messages('pull_data using version %s, acquiring the lock ... ' % version, logger)

        lock_fd = get_data_lock(path, 'pull_data')
        # the BadLock exception that may happen here is caught below
        
        do_pull = True
        if not force:
            # need to recheck any readme file that may be present here
            # it's possible that another process had path locked and updated the readme file with new information
            readmeInfo = get_data_info(path, logger, type='casarundata')
            if readmeInfo is not None:
                currentVersion = readmeInfo['version']
                currentDate = readmeInfo['date']
                if ((currentVersion == version) and (not force)):
                    if expectedMeasuresVersion is not None:
                        # this is a release pull and the measures version must also match
                        # start off assuming a pull is necessary
                        do_pull = True
                        measuresReadmeInfo = get_data_info(path, logger, type='measures')
                        if measuresReadmeInfo is not None:
                            measuresVersion = measuresReadmeInfo['version']
                            if measuresVersion == expectedMeasuresVersion:
                                # no pull is necessary
                                do_pull = False
                                print_log_messages('pull_data requested "release" versions of casarundata and measures are already installed.', logger)
                            # otherwise this is a release pull and even if the measuresVersion is 'unknown' or 'invalid' we should proceed with a pull at this point
                            # problems with casarundata path will have been caught before
                    else:
                        # nothing to do here, already at the expected casarundata version and a pull is not being forced and this is not a release pull
                        do_pull = False
                        print_log_messages('pull_data requested version is already installed.', logger)

                # a version of 'invalid', 'error', or 'unknown' is a surprise here, likely caused by something else doing something
                # incompatible with this attempt
                if version in ['invalid','error','unknown']:
                    # raise BadReadme (caught below) and do not clean up the lock file
                    clean_lock = False
                    raise BadReadme('data_update : something unexpected has changed in the path location, can not continue')

                if do_pull:
                    # make sure the copy of installed_files is the correct one
                    installed_files = readmeInfo['manifest']
                    if len(installed_files) == 0:
                        # this shoudn't happen, raise BadReadme (caught below) and do not clean up the lock file
                        clean_lock = False
                        raise BadReadme('pull_data : the readme.txt file at path did not contain the expected list of installed files after the lock was obtained, this should never happen.')

        if do_pull:
            # do not clean the lock file contents at this point unless do_pull_data returns normally
            clean_lock = False
            do_pull_data(path, version, installed_files, currentVersion, currentDate, logger)
            clean_lock = True
            if namedVersion:
                # a specific version has been requested, set the times on the measures readme.txt to now to avoid
                # a default update of the measures data without using the force argument
                measuresReadmePath = os.path.join(path,'geodetic/readme.txt')
                os.utime(measuresReadmePath)


    except BadLock as exc:
        # the path is known to exist so this means that the lock file was not empty and it's not locked
        msgs = str(exc)
        msgs.append('The lock file at %s is not empty.' % path)
        msgs.append('A previous attempt to update path may have failed or exited prematurely.')
        msgs.append('It may be best to completely repopulated path using pull_data and measures_update.')
        print_log_messages(msgs, logger, True)
        # reraise this
        raise
    except BadReadme as exc:
        # something is wrong in the readme after an update was triggered and locked, this shouldn't happen, print more context and reraise this
        msgs = str(exc)
        msgs.append('This should not happen unless multiple sessions are trying to update data at the same time and one experienced problems or was done out of sequence')
        msgs.append('Check for other updates in progress or choose a different path or clear out this path and try again')
        print_log_messages(msgs, logger, True)
        raise
    
    except Exception as exc:
        msgs = []
        msgs.append('ERROR! : Unexpected exception while populating casarundata version %s to %s' % (version, path))
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
