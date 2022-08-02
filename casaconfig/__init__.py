"""
Interface specification for all user facing external functions in the casaconfig package.
"""
# __init__.py
from .get_data_dir import get_data_dir
from .measures_update import measures_update
from .measures_available import measures_available
from .set_casacore_path import set_casacore_path
from .pull_data import pull_data

def getconfig( ):
    '''Get configuration values as strings which can be logged, stored or evaluated.

    Returns
    -------
    list[str]            list of configuration strings
    '''
    from . import _config_defaults as cdf
    return list( map( lambda name: f'{name} = {repr(getattr(cdf,name))}', filter( lambda x: not x.startswith('_'), dir(cdf) ) ) )
