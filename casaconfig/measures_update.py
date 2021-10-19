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

def measures_update(path=None, version=None):
    """
    Retrieve IERS data used for measures calculations from ASTRON FTP server
    
    Original data source is here: https://www.iers.org/IERS/EN/DataProducts/data.html
    
    Parameters
    ----------
    path : str
        Folder path to place updated measures data. Default None places it in package installation directory
    version : str
        Version of measures data to retrieve (in the form of yyyymmdd-160001, see measures_available()). Default None retrieves the latest
        
    Returns
    -------
    None
    
    """
    from ftplib import FTP
    import os
    import pkg_resources
    
    if path is None: path = pkg_resources.resource_filename('casaconfig', '__data__/')
    path = os.path.expanduser(path)
    if not os.path.exists(path): os.mkdir(path)
    
    # target filename to download
    version = '' if version is None else '_' + version
    target = 'WSRT_Measures' + version + '.ztar'

    print('connecting to ftp.astron.nl ...')
    ftp = FTP('ftp.astron.nl')
    rc = ftp.login()
    rc = ftp.cwd('outgoing/Measures')
    files = ftp.nlst()
    if target not in files:
        print('##### ERROR: cant find specified version #####')
        return
    
    with open(os.path.join(path,'measures.ztar'), 'wb') as fid:
        print('downloading data from ASTRON server ...')
        ftp.retrbinary('RETR ' + target, fid.write)
    
    os.system("tar -zxf %s -C %s" % (os.path.join(path,'measures.ztar'), path))
    os.system("rm %s" % os.path.join(path, 'measures.ztar'))
    os.system("rm -fr %s/*.old" % os.path.join(path, 'geodetic'))
    
    
    return
