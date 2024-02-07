import sys
import os
from casaconfig.private.get_argparser import get_argparser

parser = get_argparser(add_help=True)

# get_argparser supplies configfile, noconfig, nositeconfig
# add measurespath, pull-data, data-update, measures-update, update-all, reference-testing, current-data

parser.prog = "casaconfig"

# measurespath will default to the value in config if not set here
parser.add_argument( "--measurespath", dest='measurespath', default=None,
                     help="location of casarundata")

parser.add_argument( "--pull-data", dest='pulldata', action='store_const', const=True, default=False,
                     help="invoke pull_data() to populate measurespath with latest casarundata")
parser.add_argument( "--data-update", dest='dataupdate', action='store_const', const=True, default=False,
                     help="invoke data_update() to update measurespath to the latest casarundata")
parser.add_argument( "--measures-update", dest='measuresupdate', action='store_const', const=True, default=False,
                     help="invoke measures_update() to update measurespath to the latest measures data")
parser.add_argument( "--update-all", dest='updateall', action='store_const', const=True, default=False,
                     help="invoke update_all() to populate (update) measurespath with the latest casarundata and measures data")
parser.add_argument( "--reference-testing", action='store_const', const=True, dest='referencetesting', default=False,
                     help="set measurespath to the casarundata when this version was produced, used for testing purposes")
parser.add_argument( "--current-data", dest='currentdata', action='store_const', const=True, default=False,
                     help="print out a summary of the current casarundata and measures data installed in measurespath and then exit")
parser.add_argument("--force", dest='force', action='store_const', const=True, default=False,
                    help="force an update using the force=True option to update_all, data_update, and measures_update")

# initialize the configuration to be used
flags,args = parser.parse_known_args(sys.argv)
from casaconfig import config

# import the casaconfig module
import casaconfig

# make sure measurespath reflects any command line value
if flags.measurespath is None:
    flags.measurespath = config.measurespath

# watch for measurespath of None, that likely means that casasiteconfig.py is in use and this has not been set. It can't be used then.
if flags.measurespath is None:
    print("measurespath has been set to None, likely in casasiteconfig.py.")
    print("Either provide a measurespath on the casaconfig command line or edit casasiteconfig.py or other a user config.py to set measurespath to a location.")
    sys.exit(1)

# do any expanduser and abspath - this is what should be used
measurespath = os.path.abspath(os.path.expanduser(flags.measurespath))

if flags.currentdata:
    if not os.path.exists(measurespath) or not os.path.isdir(measurespath):
        print("No data installed at %s. The measurespath does not exist or is not a directory." % measurespath)
    else:
        from casaconfig import get_data_info
        print("current data installed at %s" % measurespath)
        dataInfo = get_data_info(measurespath)
        
        # casarundata
        casarunInfo = dataInfo['casarundata']
        if casarunInfo is None or casarunInfo['version'] == "invalid":
            print("No casarundata found (missing or unexpected readme.txt contents, not obviously legacy casa data).")
        elif casarunInfo['version'] == "unknown":
            print("casarundata version is unknown (probably legacy casa data not maintained by casaconfig).")
        else:
            currentVersion = casarunInfo['version']
            currentDate = casarunInfo['date']
            print('casarundata version %s installed on %s' % (currentVersion, currentDate))
            
        # measures
        measuresInfo = dataInfo['measures']
        if measuresInfo is None or measuresInfo['version'] == "invalid":
            print("No measures data found (missing or unexpected readme.txt, not obviously legacy measures data).")
        elif measuresInfo['version'] == "unknown":
            print("measures version is unknown (probably legacy measures data not maintained by casaconfig).")
        else:
            currentVersion = measuresInfo['version']
            currentDate = measuresInfo['date']
            print('measures version %s installed on %s' % (currentVersion, currentDate))
 
    # ignore any other arguments

else:
    if flags.referencetesting:
        print("reference testing using pull_data and 'release' version into %s" % measurespath)
        casaconfig.pull_data(measurespath,'release')
        # ignore all other options
    else:
        # the update options, update all does everything, no need to invoke anything else
        print("Checking for updates into %s" % measurespath)
        if flags.updateall:
            casaconfig.update_all(measurespath,force=flags.force)
        else:
            # do any pull_update first
            if flags.pulldata:
                casaconfig.pull_data(measurespath)
            # then data_update, not necessary if pull_data just happened
            if flags.dataupdate and not flags.pulldata:
                casaconfig.data_update(measurespath, force=flags.force)
            # then measures_update
            if flags.measuresupdate:
                casaconfig.measures_update(measurespath, force=flags.force)

sys.exit(0)
