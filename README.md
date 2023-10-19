# casaconfig
Runtime data necessary for CASA operation.

- Latest documentation [![Documentation Status](https://readthedocs.org/projects/casaconfig/badge/?version=latest)](https://casaconfig.readthedocs.io/en/latest/?badge=latest)
- Stable documentation [![Documentation Status](https://readthedocs.org/projects/casaconfig/badge/?version=stable)](https://casaconfig.readthedocs.io/en/stable/?badge=stable)
      

## Release Instructions
1. Create a release branch with a version name (ie v1.6.2)
2. Ensure the version number in setup.py on the branch is set correctly
3. Create a tag of the release branch (ie v1.6.2-1)
4. Github Action runs automatically to publish a pip package to pypi

## Installation

```
$: pip install casaconfig
```

## Usage

CASA (modular and monolithic) does not come with any data. It must be populated
by calling ```pull_data()``` to download the tables. The default location is
```~/.casa/data```. The ```path``` argument can be used to populate a different location.

```python
from casaconfig import pull_data
pull_data()
```

Within this folder is a stale version of the IERS measures tables needed for accurate measurement. 
Generally users will want to update to the latest measures data and keep current each day. 

```python
from casaconfig import measures_update
measures_update()
```

The update_all function updates or installs the data and the latest measures tables.

```python
from casaconfig import update_all
update_all()
```

A default config.py necessary for CASA operation is included in this package. Users
provide their own config.py (default at ~/.casa/config.py) if they want to change
any of the default values (only the values they want to change need be provided in
that file). 

The default config values are shown here (path's are expanded using expanduser and abspath).

```
$: cat ~/.casa/config.py

import os, time, pkg_resources

# location of geodetic and ephemera data, default path for casaconfig data functions
measurespath = "~/.casa/data"

# search path for measurement sets and images to load, when empty then [measurespath] is used
datapath = [ ]

# automatically update measures data if not current (measurespath must be owned by the user)
# when data_auto_update is True then measures_auto_update MUST also be True
measures_auto_update = True

# automatically update casarundata and measures data if not current (measurespath must be owned by the user)
data_auto_update = True

# location of the optional user's startup.py
startupfile = '~/.casa/startup.py'

# location of the cachedir
cachedir = '~/.casa'

# log file path/name
logfile='casa-%s.log' % time.strftime("%Y-%m-%d", time.gmtime())

# do not create a log file when True, If True, then any logfile value is ignored and there is no log file
nologfile = False

# print log output to terminal when True (in addition to any logfile and CASA logger)
log2term = False

# do not start the CASA logger when True
nologger = False

# avoid starting GUI tools when True. If True then the CASA logger is not started even if nologger is False
nogui = False

# the IPython prompt color scheme. Must be one of "Neutral", "NoColor", "Linux" or "LightBG", default "Neutral"
# if an invalid color is given a warning message is printed and logged but CASA continues using the default color
colors = "Neutral"

# startup without a graphical backend if True
agg = False

# attempt to load the pipeline modules and set other options appropriate for pipeline use if True
# when pipeline is True then agg will be assumed to be true even if agg is set to False here or on the command line
pipeline = False

# create and use an IPython log using the iplogfile path 
iplog = True

# IPython log path/name used when iplog is True
iplogfile = 'ipython-%s.log' % time.strftime("%Y-%m-%d", time.gmtime())

# include the users local site-packages in the python path if True. 
# normally these are excluded to avoid any conflicts with CASA modules
user_site = False
```
