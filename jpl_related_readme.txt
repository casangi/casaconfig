This branch, jpl_related, contains scripts removed from the main casaconfig
branch that are not appropriate at this point but might be useful in the future.

These scripts are : 
   * JPLephem_reader2.py
   * jplephem_request.py
   * tec_maps.py
   * table_open.py

JPLephem_reader2.py can be found in casatasks/src/private
jplephem_request.py appears to be older casa code not currently used
tec_maps.py can be found in casatasks/src/private
table_open.py uses python-casacore to open tables and return xarray dataset(s).

table_open may be useful for casangi but is not used by any parts of casa. It
is used by the version of tec_maps.py found here
