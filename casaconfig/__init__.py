# __init__.py
"""
casaconfig API functions
"""
import pkg_resources

__name__ = 'casaconfig'

datapath = pkg_resources.resource_filename('casaconfig', '__data__/')

from .get_data_dir import get_data_dir
from .measures_update import measures_update
from .measures_available import measures_available
from .set_casacore_path import set_casacore_path
from .pull_data import pull_data
from .write_default_config import write_default_config