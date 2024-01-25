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

def measures_update(path=None, version=None, force=False, logger=None, auto_update_rules=False):
    """
    Retrieve IERS data used for measures calculations from the ASTRON server
    
    Original data source used by ASTRON is here: https://www.iers.org/IERS/EN/DataProducts/data.html

    CASA maintains a separate Observatories table which is available in the casarundata
    collection through pull_data and data_update. The Observatories table found at ASTRON
    is not installed by measures_update and any Observatories file at path will not be changed
    by using this function.

    A text file (readme.txt in the geodetic directory in path) records the measures version string
    and the date when that version was installed in path.

    If path is None then config.measurespath is used.

    If the version requested matches the one in that text file then this function does
    nothing unless force is True.

    If a specific version is not requested (the default) and the modification time of that text
    file is less than 24 hrs before now then this function does nothing unless force is True. This
    limits the number of attempts to update the measures data (including checking for more recent
    data) to once per day.

    When auto_update_rules is True then path must exist and contain the expected readme.txt file.
    Path must be owned by the user, force must be False, and the version must be None. This 
    option is used during casatools initialization when measures_auto_update is True. Automatic 
    updating happens during casatools initialization so that the updated measures are in place 
    before any tool needs to use them.

    Using measures_update after casatools has started should always be followed by exiting 
    and restarting casa (or the casatools module if modular casa components are being used).

    A file lock is used to prevent more that one data update (pull_data, measures_update,
    or data_update) from updating any files in path at the same time. When locked, the 
    lock file (data_update.lock in path) contains information about the process that
    has the lock. When measures_update gets the lock it checks the readme.txt file in path
    to make sure that an update is still necessary (if force is True then an update 
    always happens). If the lock file is not empty then a previous update of path (pull_data,
    data_update, or measures_update) did not exit as expected and the contents of path are
    suspect. In that case, an error will be reported and nothing will be updated. The lock
    file can be checked to see the details of when that file was locked. The lock file can be
    removed and measures_update can be tried again. It may be safest in that case to remove path
    completely or use a different path and use pull_data to install a fresh copy of the
    desired version.

    Care should be used when using measures_update outside of the normal automatic
    update that other casa sessions are not using the same measures at the same time,
    especially if they may also be starting at that time. If a specific version is
    requested or force is True there is a risk that the measures may be updated while
    one of those other sessions are trying to load the same measures data, leading to
    unpredictable results. The lock file will prevent simulateous updates from
    happening but if each simultanous update eventually updates the same measures
    location (because force is True or the updates are requesting different versions)
    then the measures that any of those simultanous casatools modules sees is 
    unpredictable. Avoid multiple, simultanous updates outside of the automatic
    update process.

    **Note:** during auto updates, measures_update requires that the expected 
    readme.txt file already exists in the geodetic directory at path. If that file does 
    not exist or can not be interpreted as expected then measures_update will 
    return without updating any data.

    **Note:** if auto_update_rules is True the user must own path (in addition to having 
    read and write permissions there). The version must then also be None and the force option 
    must be False.

    **Note::** During use outside of auto updates, if path does not exist it will be created
    by this function.

    **Notes::** During use outside of auto updates, if the readme.txt file exists but can not
    be read as expected **OR** that file does not exist but the contents of path appear to
    contain measures data (table names in the expected locations) then this function will
    print messages describing that and exit without changing anything at path. Using
    a force value of True will disable this check and install measures at path even if path
    is not empty or the readme.txt file can not be read. This use of force should be used
    with caution.


    Parameters
       - path (str=None) - Folder path to place updated measures data. Must contain a valid geodetic/readme.txt. If not set then config.measurespath is used.
       - version (str=None) - Version of measures data to retrieve (usually in the form of yyyymmdd-160001.ztar, see measures_available()). Default None retrieves the latest.
       - force (bool=False) - If True, always re-download the measures data. Default False will not download measures data if updated within the past day unless the version parameter is specified and different from what was last downloaded.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal
       - auto_update_rules (bool=False) - If True then the user must be the owner of path, version must be None, and force must be False.
        
    Returns
       None
    
    """
    import os
    import pkg_resources
    from datetime import datetime
    import sys

    from ftplib import FTP
    import tarfile
    import re
    import ssl
    import urllib.request
    import certifi
    import fcntl

    from .print_log_messages import print_log_messages
    from .get_data_lock import get_data_lock
    from .get_data_info import get_data_info
    
    if path is None:
        from .. import config as _config
        path = _config.measurespath

    if path is None:
        # it's not being set in a config file, probably casasiteconfig.py is being use but has not been edited
        print_log_messages('path is None and has not been set in config.measurespath (probably casasiteconfig.py). Provide a valid path and retry.', logger, True)
        return

    path = os.path.expanduser(path)

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
    
    if not os.path.exists(path):
        # make dirs all the way down, if possible
        os.makedirs(path)
        
    current = None
    ageRecent = False

    # first, does this look like it needs to be updated

    # get any existing measures readme information
    readmeInfo = get_data_info(path, logger, type='measures')
    if readmeInfo is not None:
        current = readmeInfo['version']
        if readmeInfo['age'] is not None:
            ageRecent = readmeInfo['age'] < 1.0

    if not force:
        # don't re-download the same data
        if (version is not None) and (version == current):
            print_log_messages('measures_update requested version already installed in %s' % path, logger)
            return
        
        # don't check for new version if the age is less than 1 day
        if version is None and ageRecent:
            print_log_messages('measures_update latest version checked recently in %s, using version %s' % (path, current), logger)
            return
        
        # don't overwrite something that looks bad unless forced to do so
        if current == 'invalid':
            print_log_messages('the measures readme.txt file could not be read as expected, an update can not proceed unless force is True', logger, True)
            return

        # don't overwrite something that looks like valid measures data unless forced to do so
        if current == 'unknown':
            print_log_messages('The measures data at %s is not maintained by casaconfig and so it can not be updated unless force is True' % path, logger, True)
            return

    # path must be writable with execute bit set
    if (not os.access(path, os.W_OK | os.X_OK)) :
        print_log_messages('No permission to write to the measures path, cannot update : %s' % path, logger, True)
        return

    # an update needs to happen

    # lock the measures_update.lock file
    lock_fd = None
    try:
        print_log_messages('measures_update measures need to be updated, acquiring the lock ... ', logger)

        lock_fd = get_data_lock(path, 'measures_update')
        # if lock_fd is None it means the lock file was not empty - because we know that path exists at this point
        if lock_fd is None:
            print_log_messages('The lock file at %s is not empty.' % path, logger, True)
            print_log_messages('A previous attempt to update path may have failed or exited prematurely.', logger, True)
            print_log_messages('Remove the lock file and set force to True with the desired version (default to most recent).', logger, True)
            print_log_messages('It may be best to completely repopulate path using pull_data and measures_update.', logger, True)
            return

        do_update = force

        if not do_update:
            # recheck the readme file, another update may have already happened before the lock was obtained
            current = None
            ageRecent = False
            
            readmeInfo = get_data_info(path, logger, type='measures')
            if readmeInfo is not None:
                current = readmeInfo['version']
                if readmeInfo['age'] is not None:
                    ageRecent = readmeInfo['age'] < 1.0

            if (version is not None) and (version == current):
                # no update will be done, version is as requested
                print_log_messages('measures_update requested measures version detected in %s, using version %s' % (path, current), logger)
            elif (version is None) and ageRecent:
                # no update will be done, it's already been checked or updated recently
                print_log_messages('measures_update latest measures version checked recently in %s, using version %s' % (path, current), logger)
            else:
                # final check for problems before updating
                if not force and readmeInfo is not None and (version=='invalid' or version=='unknown'):
                    # at this point, this indicates something is unexpectedly wrong, do not continue
                    print_log_messages('Something unexpected has changed in the measures path location, and measures_update can not continue', logger, True)
                    print_log_messages('a previous measures_update may have exited unexpectedly', logger, True)
                    print_log_messages('It may be necessary to reinstall the casarundata as well as the measures data if %s is the correct path' % path, logger, True)
                    # update is already turned off, the lock file will be cleaned up on exit
                else:
                    # an update is needed
                    do_update = True

        if do_update:
            if force:
                print_log_messages('meaures_update a measures update has been requested by the force argument', logger)

            print_log_messages('measures_update connecting to ftp.astron.nl ...', logger)

            ftp = FTP('ftp.astron.nl')
            rc = ftp.login()
            rc = ftp.cwd('outgoing/Measures')
            files = sorted([ff for ff in ftp.nlst() if (len(ff) > 0) and (not ff.endswith('.dat')) and (ftp.size(ff) > 0)])

            # target filename to download
            # for the non-force unspecified version case this can only get here if the age is > 1 day so there should be a newer version
            # but that isn't checked - this could install a version that's already installed
            target = files[-1] if version is None else version
            if target not in files:
                print_log_messages('measures_update cant find specified version %s' % target, logger, True)

            else:
                # there are files to extract, remove the readme.txt file in case this dies unexpectedly
                readme_path = os.path.join(path,'geodetic/readme.txt')
                if os.path.exists(readme_path):
                    os.remove(readme_path)
    
                with open(os.path.join(path,'measures.ztar'), 'wb') as fid:
                    print_log_messages('measures_update downloading %s from ASTRON server to %s ...' % (target, path), logger)
                    ftp.retrbinary('RETR ' + target, fid.write)

                ftp.close()
    
                # extract from the fetched tarfile
                with tarfile.open(os.path.join(path,'measures.ztar'),mode='r:gz') as ztar:
                    # the list of members to extract
                    x_list = []
                    for m in ztar.getmembers() :
                        # always exclude the Observatories table and  *.old names in geodetic
                        if not((re.search('geodetic',m.name) and re.search('.old',m.name)) or re.search('Observatories',m.name)):
                            x_list.append(m)

                    # use the 'data' filter if available, revert to previous 'fully_trusted' behavior of not available
                    ztar.extraction_filter = getattr(tarfile, 'data_filter', (lambda member, path: member))
                    ztar.extractall(path=path,members=x_list)
                    ztar.close()

                os.system("rm %s" % os.path.join(path, 'measures.ztar'))

                # update the readme.txt file
                with open(readme_path,'w') as fid:
                    fid.write("# measures data populated by casaconfig\nversion : %s\ndate : %s" % (target, datetime.today().strftime('%Y-%m-%d')))

                print_log_messages('measures_update updated measures data at %s' % path, logger)
            
            # closing out the do_update

        # closing out the try block
        # truncate the lock file
        lock_fd.truncate(0)
        
    except Exception as exc:
        print_log_messages("ERROR! : Unexpected exception while updating measures at %s" % path, logger, True)
        print_log_messages("ERROR! : %s" % exc, logger, True)
        # leave the contents of the lock file as is to aid in debugging
        
    # if the lock file is not closed, do that now to release the lock
    if lock_fd is not None and not lock_fd.closed:
        lock_fd.close()

    return
