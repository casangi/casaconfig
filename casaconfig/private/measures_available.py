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


def measures_available():
    """
    List available measures versions on ASTRON FTP server

    Parameters
       None
    
    Returns
       list - version names returned as list of strings

    """
    from ftplib import FTP
    
    ftp = FTP('ftp.astron.nl')
    rc = ftp.login()
    rc = ftp.cwd('outgoing/Measures')
    files = ftp.nlst()
    ftp.quit()
    #files = [ff.replace('WSRT_Measures','').replace('.ztar','').replace('_','') for ff in files]
    files = [ff for ff in files if (len(ff) > 0) and (not ff.endswith('.dat'))]
    return files
