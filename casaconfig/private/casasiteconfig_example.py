# An example site config file.
# Place this in a location checked by casaconfig :
#   /opt/casa/casasiteconfig.py
#   /home/casa/casasiteconfig.py
#   the environment value CASASITECONFIG - use the fully qualified path
#   anywhere in the python path, e.g. the site-packages directory in the CASA being used.
#

# This file should be edited to set measurespath as appropriate

# Set this to point to the location where the site maintained casarundata can be found
# by default datapath will include measurespath

measurespath = "/path/to/installed/casarundata"

# turn off all auto updates of data

measures_auto_update = False
data_auto_update = False
