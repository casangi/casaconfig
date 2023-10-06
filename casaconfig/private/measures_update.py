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

def measures_update(path, auto_update_rules=False, version=None, force=False, logger=None):
    """
    Retrieve IERS data used for measures calculations from ASTRON server
    
    Original data source is here: https://www.iers.org/IERS/EN/DataProducts/data.html

    CASA maintains a separate Observatory table which is used by measures_update instead 
    of the version that accompanies the ASTRON measures tables.

    A text file (readme.txt in the geodetic directory in path) records the version string
    and the date when that version was installed in path.

    If the version requested matches the one in that text file then this function does
    nothing unless force is True.

    If a specific version is not requested (the default) and the date in that text file
    is today, then this function does nothing unless force is True even if there is a more
    recent version available from the ASTRON server.

    Automatic updating (when the measures_auto_update config value is True) uses this
    function as the casatools module is starting so that the updated measures are in
    place before any tool needs to use them. 

    Using measures_update after casatools has started should always be followed by exiting 
    and restarting casa (or the casatools module if modular casa components are being used).

    A file lock is used to prevent more that one measures_update and data_update from updating
    the measures files in path at the same time. When locked, the lock file (data_update.lock 
    in path) will contain information about the process that has the lock. When a measures_update
    gets the lock it will check the readme.txt file in the geodetic directory in path
    to make sure that an update is still necessary (if force is True an update always happens).

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

    **Note:** measures_update requires that the expected readme.txt file already exists in
    the geodetic directory at path. If that file does not exist or can not be interpreted as
    expected then measures_update will return without updating any data.

    **Note:** if auto_update_rules is True the user must own path (in addition to having 
    read and write permissions there). The version must then also be None and the force option 
    must be False.


    Parameters
       - path (str) - Folder path to place updated measures data. Must contain a valid geodetic/readme.txt
       - auto_update_rules (bool=False) - If True then the user must be the owner of path, version must be None, and force must be False.
       - version (str=None) - Version of measures data to retrieve (usually in the form of yyyymmdd-160001.ztar, see measures_available()). Default None retrieves the latest.
       - force (bool=False) - If True, always re-download the measures data. Default False will not download measures data if already updated today unless the version parameter is specified and different from what was last downloaded.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal
        
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
    
    if not os.path.exists(path): os.mkdir(path)
    current = None
    updated = None
    today_string = datetime.today().strftime('%Y-%m-%d')

    # first, does this look like it needs to be updated

    # if measures are already preset, get their version
    readme_path = os.path.join(path,'geodetic/readme.txt')
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r') as fid:
                readme = fid.readlines()
            current = readme[1].split(':')[-1].strip()
            updated = readme[2].split(':')[-1].strip()
        except:
            pass

    # don't re-download the same data
    if not force:
        if ((version is not None) and (version == current)) or ((version is None) and (updated == today_string)):
            print_log_messages('measures_update current measures detected in %s, using version %s' % (path, current), logger)
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
            updated = None
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r') as fid:
                        readme = fid.readlines()
                        current = readme[1].split(':')[-1].strip()
                        updated = readme[2].split(':')[-1].strip()
                except:
                    pass

            if ((version is not None) and (version == current)) or ((version is None) and (updated == today_string)):
                # no update will be done, version is as requested or it's already been updated today
                print_log_messages('measures_update current measures detected in %s, using version %s' % (path, current), logger)
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
            target = files[-1] if version is None else version
            if target not in files:
                print_log_messages('measures_update cant find specified version %s' % target, logger, True)

            else:
                # there are files to extract, remove the readme.txt file in case this dies unexpectedly
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
                        # always exclude *.old names in geodetic and the Observatories table
                        if not((re.search('geodetic',m.name) and re.search('.old',m.name)) or re.search('Observatories',m.name)):
                            x_list.append(m)

                    ztar.extractall(path=path,members=x_list)
                    ztar.close()

                os.system("rm %s" % os.path.join(path, 'measures.ztar'))

                # get the Observatories table from CASA
                print_log_messages('measures_update obtaining the Observatories table from CASA', logger)
                context = ssl.create_default_context(cafile=certifi.where())
                tstream = urllib.request.urlopen('https://casa.nrao.edu/download/geodetic/observatories.tar.gz', context=context, timeout=400)
                tar = tarfile.open(fileobj=tstream, mode="r:gz")
                tar.extractall(path=path)

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
