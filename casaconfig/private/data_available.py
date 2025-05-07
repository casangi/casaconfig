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

def data_available():
    """
    List available casarundata versions on CASA server at https://go.nrao.edu/casarundata

    This returns a list of the casarundata versions available on the CASA
    server. The version parameter of data_update must be one
    of the values in that list if set (otherwise the most recent version
    in this list is used).

    A casarundata version is the filename of the tarball and look 
    like "casarundata.x.y.z.tar.*" (different compressions may be used by CASA without
    changing casaconfig functions that use those tarballs). The full filename is
    the casarundata version expected in casaconfig functions.

    Parameters
       None
    
    Returns
       list - version names returned as list of strings

    Raises
       - casaconfig.NoNetwork - Raised where there is no network seen, can not continue
       - casaconfig.RemoteError - Raised when there is an error fetching some remote content for some reason other than no network
       - Exception - Unexpected exception while getting list of available casarundata versions

    """

    from .get_available_tarfiles import get_available_tarfiles

    try:
        return get_available_tarfiles('https://go.nrao.edu/casarundata', 'casarundata')
    except urllib.error.URLError as urlerr:
        raise RemoteError("Unable to retrieve list of available casarundata versions : " + str(urlerr)) from None
        
    except Exception as exc:
        msg = "Unexpected exception while getting list of available casarundata versions : " + str(exc)
        raise Exception(msg)

    # nothing to return if it got here, must have been an exception
    return []

    
