
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

def get_config( default=False ):
    """
    Get configuration values as a list of strings which can be logged, stored, or evaluated.

    The default values (returned when default is True) are the configuration values after all config files have been evaluated but before the path values have been expanded using os.path.expanduser and os.path.abspath. Modules that use the command line to change config values may also not update the default values. User actions in a CASA session will also typically not change the default values.

    Parameters
       - default (bool=False) - If True, return the default values.

    Returns
       - list[str] - list of configuration strings
    """

    from .. import config as _config
    if not default :
        valsObj = _config
    else:
        valsObj = _config._config_defaults

    return list( map( lambda name: f'{name} = {repr(getattr(valsObj,name))}', _config.__defaults ) )
