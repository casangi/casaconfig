# lsit of paths where CASA should search for data subdirectories. Default [measurespath].
datapath = [ ]

# location of required measures data, takes precedence over any measures data also present in datapath.
measurespath = "~/.casa/data"

# locations to check for measures tarballs, this can be a single string value or
# a list of strings, the first element in the list is the default value to use
# Each element should be a URL giving a location containing a set of measures
# tarballs having names following the form WSRT_Measures_YYYYMMDD-HHMMSS.*
# WHere YYYYMMDD is a date and HHMMSS is a time, anything can come after the
# .* but it should indicate a form of tarball, usually compressed, e.g. "ztar"
measures_site = ["https://iers.astron.nl/", "https://go.nrao.edu/iers/"]

# automatically update measures data if not current (measurespath must be owned by the user)
# when data_auto_update is True then measures_auto_update MUST also be True
measures_auto_update = True

# automatically update casarundata and measures data if not current (measurespath must be owned by the user)
data_auto_update = True

# the interval, in days, that an installed casarundata is considered to be recent
# recent casarundata installations are not updated unless the force argument is true
data_update_interval = 1

# the interval, in days, that an installed measures data is considered to be recent
# recent measures data installations are not updated unless the force argument is tru
measures_update_interval = 1

# a measures site is considered out of date if the newest tar file found there is older
# than this many days. This may cause a warning and affect which measures_site is actually use.
# the units are days and it is used as an integer. No attempt is made to account for the time
# zone difference  between the local time and the time of the measures site
measures_site_interval = 2

# location of the optional user's startup.py
startupfile = '~/.casa/startup.py'

# location of the cachedir
cachedir = '~/.casa'

# log file path/name
logfile='casa-%s.log' % _time.strftime("%Y%m%d-%H%M%S", _time.gmtime())

# do not create a log file when True, If True, then any logfile value is ignored and there is no log file
nologfile = False

# print log output to terminal when True (in addition to any logfile and CASA logger)
log2term = False

# do not start the CASA logger GUI when True
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
iplog = False

# the IPython log file path name to be used when iplog is True
iplogfile='ipython-%s.log' % _time.strftime("%Y%m%d-%H%M%S", _time.gmtime())

# include the user's local site-packages in the python path if True. May conflict with CASA modules
user_site = False

# verbosity level for casaconfig
casaconfig_verbose = 1

# skip the network check step when fetching data or available data lists, useful if the sites used there are blocked
skipnetworkcheck = False
