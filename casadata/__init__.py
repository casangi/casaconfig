# __init__.py
__name__ = 'casadata'
__all__ = [ 'datapath' ]

import os as _os

datapath=(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'__data__'))

from .get_data_dir import get_data_dir
from .measures_update import measures_update
from .measures_available import measures_available
from .set_casacore_path import set_casacore_path
from .table_open import table_open
from .pull_data import pull_data