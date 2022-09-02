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

def measures_update(path=None, version=None, force=False, logger=None):
    """
    Retrieve IERS data used for measures calculations from ASTRON FTP server
    
    Original data source is here: https://www.iers.org/IERS/EN/DataProducts/data.html

    CASA maintains a separate Observatory table which is used my measures_update instead of the version that accompanies the ASTRON measures tables. 
    
    Parameters
       - path (str=None) - Folder path to place updated measures data. Default None places it in package installation directory
       - version (str=None) - Version of measures data to retrieve (usually in the form of yyyymmdd-160001.ztar, see measures_available()). Default None retrieves the latest
       - force (bool=False) - If True, always re-download the measures data. Default False will not download measures data if already updated today unless version parameter is specified and different from what was last downloaded.
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

    if path is None: path = pkg_resources.resource_filename('casaconfig', '__data__/')
    path = os.path.expanduser(path)
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
            print('casaconfig current measures detected in %s, using version %s' % (path, current), file=sys.stdout)
            if logger is not None: logger.post('casaconfig current measures detected in %s, using version %s' % (path, current), 'INFO')
            return

    # path must be writable with execute bit set
    if (not os.access(path, os.W_OK | os.X_OK)) :
        print('No permission to write to the measures path, cannot update : %s' % path, file=sys.stdout)
        if logger is not None: logger.post('No permission to write to the measures path, cannot update : %s' % path, 'ERROR')
        return

    # an update needs to happen

    # lock the measures_update.lock file
    lock_fd = None
    try:
        print('casaconfig measures need to be updated, acquiring the lock ... ',file=sys.stdout)
        lock_path = os.path.join(path,'measures_update.lock')

        # open and lock the lock file - don't truncate it here if it already exists, wait until it's locked
        mode = 'r+' if os.path.exists(lock_path) else 'w'
        lock_fd = open(lock_path, mode)
        fcntl.lockf(lock_fd,fcntl.LOCK_EX)
        
        # truncate and update the lock information
        # this should already be empty, but just in case
        lock_fd.seek(0)
        lock_fd.truncate(0)
        lock_fd.write("locked using measures_update by %s on %s : pid = %s at %s" % (os.getlogin(),os.uname().nodename, os.getpid(), datetime.today().strftime('%Y-%m-%d:%H:%M:%S')))
        lock_fd.flush()

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
                print('casaconfig current measures detected in %s, using version %s' % (path, current), file=sys.stdout)
                if logger is not None: logger.post('casaconfig current measures detected in %s, using version %s' % (path, current), 'INFO')
            else:
                # an update is needed
                do_update = True

        if do_update:
            if force:
                print('casaconfig a measures update has been requested by the force argument', file=sys.stdout)
                if logger is not None: logger.post('casaconfig a measures update has been requested by the force argument', 'INFO')

            print('casaconfig connecting to ftp.astron.nl ...', file=sys.stdout)
            if logger is not None: logger.post('casconfig connecting to ftp.astron.nl ...', 'INFO')

            ftp = FTP('ftp.astron.nl')
            rc = ftp.login()
            rc = ftp.cwd('outgoing/Measures')
            files = sorted([ff for ff in ftp.nlst() if (len(ff) > 0) and (not ff.endswith('.dat')) and (ftp.size(ff) > 0)])

            # target filename to download
            target = files[-1] if version is None else version
            if target not in files:
                if logger is not None: 
                    logger.post('casaconfig cant find specified version %s' % target, 'ERROR')
                else: 
                    print('##### ERROR: cant find specified version %s #####' % target, file=sys.stdout)

            else:
                # there are files to extract, remove the readme.txt file in case this dies unexpectedly
                if os.path.exists(readme_path):
                    os.remove(readme_path)
    
                with open(os.path.join(path,'measures.ztar'), 'wb') as fid:
                    print('casaconfig downloading %s from ASTRON server to %s ...' % (target, path), file=sys.stdout)
                    if logger is not None: logger.post('casaconfig downloading %s from ASTRON server to %s ...' % (target, path), 'INFO')
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
                print('casaconfig obtaining the Observatories table from CASA', file=sys.stdout)
                if logger is not None: logger.post('casconfig obtaining the Observatories table from CASA ...', 'INFO')
                context = ssl.create_default_context(cafile=certifi.where())
                tstream = urllib.request.urlopen('https://casa.nrao.edu/download/geodetic/observatories.tar.gz', context=context, timeout=400)
                tar = tarfile.open(fileobj=tstream, mode="r:gz")
                tar.extractall(path=path)

                # update the readme.txt file
                with open(readme_path,'w') as fid:
                    fid.write("# measures data populated by casaconfig\nversion : %s\ndate : %s" % (target, datetime.today().strftime('%Y-%m-%d')))

                print('casaconfig updated measures data at %s' % path, file=sys.stdout)
                if logger is not None: logger.post('casaconfig updated measures data at %s' % path, 'INFO')
            
            # closing out the do_update

        # closing out the try block
        # truncate the lock file
        lock_fd.truncate(0)

        # close the lock file to release the lock
        lock_fd.close()
        
    except Exception as exc:
        print("ERROR! : Unexpected exception while updating measures at %s" % path, file=sys.stdout)
        print("ERROR! : %s" % exc, file=sys.stdout)
        # close the lock file if not closed to release the lock
        # leave the contents as is to aid in debugging
        if lock_fd is not None and not(lock_fd.closed):
            lock_fd.close()

    return
