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
    
    Parameters
       - path (str=None) - Folder path to place updated measures data. Default None places it in package installation directory
       - version (str=None) - Version of measures data to retrieve (in the form of yyyymmdd-160001, see measures_available()). Default None retrieves the latest
       - force (bool=False) - If True, always re-download the measures data even if matching set found in path. Default False will not download duplicate measures
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal
        
    Returns
       None
    
    """
    from ftplib import FTP
    import os
    from datetime import datetime
    import pkg_resources
    
    if path is None: path = pkg_resources.resource_filename('casaconfig', '__data__/')
    path = os.path.expanduser(path)
    if not os.path.exists(path): os.mkdir(path)
    current = None
    updated = None

    # if measures are already preset, get their version
    if os.path.exists(os.path.join(path, 'geodetic/readme.txt')):
        try:
            with open(os.path.join(path,'geodetic/readme.txt'), 'r') as fid:
                readme = fid.readlines()
            current = readme[1].split(':')[-1].strip()
            updated = readme[2].split(':')[-1].strip()
        except:
            pass

    # don't re-download the same data
    if not force:
        if ((version is not None) and (version == current)) or ((version is None) and (updated == datetime.today().strftime('%Y-%m-%d'))):
            print('casaconfig current measures detected, using version %s' % current)
            if logger is not None: logger.post('casaconfig current measures detected, using version %s' % current, 'INFO')
            return

    print('casaconfig connecting to ftp.astron.nl ...')
    if logger is not None: logger.post('casconfig connecting to ftp.astron.nl ...', 'INFO')

    ftp = FTP('ftp.astron.nl')
    rc = ftp.login()
    rc = ftp.cwd('outgoing/Measures')
    files = sorted([ff for ff in ftp.nlst() if (len(ff) > 0) and (not ff.endswith('.dat'))])

    # target filename to download
    target = files[-1] if version is None else version
    if target not in files:
        if logger is not None: logger.post('casaconfig cant find specified version %s' % target, 'ERROR')
        else: print('##### ERROR: cant find specified version %s #####' % target)
        return
    
    with open(os.path.join(path,'measures.ztar'), 'wb') as fid:
        print('casaconfig downloading data from ASTRON server ...')
        if logger is not None: logger.post('casaconfig downloading %s from ASTRON server ...' % target, 'INFO')
        ftp.retrbinary('RETR ' + target, fid.write)
    
    os.system("tar -zxf %s -C %s" % (os.path.join(path,'measures.ztar'), path))
    os.system("rm %s" % os.path.join(path, 'measures.ztar'))
    os.system("rm -fr %s/*.old" % os.path.join(path, 'geodetic'))
    with open(os.path.join(path,'geodetic/readme.txt'), 'w') as fid:
       fid.write("# measures data populated by casaconfig\nversion : %s\ndate : %s" % (target, datetime.today().strftime('%Y-%m-%d')))

    return
