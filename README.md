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

The Python package installs with an empty ```__data__``` subdirectory. The
contents must be populated by calling ```pull_data()``` to download the tables
from the Github repo ```data``` folder.

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

A default config.py necessary for CASA operation is included in this package. Users may make their
own local copy with any desired modifications.

```python
from casaconfig import write_default_config
write_default_config('~/.casa/config.py')
```

```
$: cat ~/.casa/config.py

import os, time, pkg_resources

# list of paths where CASA should search for data subdirectories
datapath = [pkg_resources.resource_filename('casaconfig', '__data__/')]

# location of required runtime measures data, takes precedence over location(s) in datapath list
measurespath = os.path.expanduser("~/.casa/measures")

# automatically update measures data if not current (measurespath must be user-writable)
measures_update = True

# log file path/name
logfile='casalog-%s.log' % time.strftime("%Y-%m-%d", time.localtime())

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
colors = "LightBG"

# startup without a graphical backend if True
agg = False

# attempt to load the pipeline modules and set other options appropriate for pipeline use if True
# when pipeline is True then agg will be assumed to be true even if agg is set to False here or on the command line
pipeline = False

# create and use an IPython log using the iplogfile path 
iplog = True

# IPython log path/name used when iplog is True
iplogfile = 'ipython-%s.log' % time.strftime("%Y-%m-%d", time.localtime())

# allow anonymous usage reporting
telemetry_enabled = True

# location to place telemetry data prior to reporting
telemetry_log_directory = os.path.expanduser("~/.casa/telemetry")

# maximum size of telemetry recording
telemetry_log_limit = 1650

# telemetry recording size that triggers a report
telemetry_log_size_interval = 30

# telemetry recording report frequency
telemetry_submit_interval = 20

# allow anonymous crash reporting
crashreporter_enabled = True

# include the users local site-packages in the python path if True. 
# normally these are excluded to avoid any conflicts with CASA modules
user_site = False
```
