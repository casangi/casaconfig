# Copyright 2025 AUI, Inc. Washington DC, USA
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

import urllib.request
import urllib.error

def have_network():
    """
    check to see if an active network with general internet connectivity
    is available. returns True if we have internet connectivity and
    False if we do not.
    """
    ###
    ### see: https://stackoverflow.com/questions/50558000/test-internet-connection-for-python3
    ###
    ### copied from in casagui/utils/__init__.py
    ###
    try:
        with urllib.request.urlopen('http://clients3.google.com/generate_204') as response:
            return response.status == 204
    except urllib.error.HTTPError:
        ### http error
        return False
    except urllib.error.ContentTooShortError:
        return False
    except urllib.error.URLError:
        return False
    except Exception:
        return False
