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
parser.add_argument( "--summary", dest='summary', action='store_const', const=True, default=False,
                     help="print out a summary of casaconfig data handling and the exit")
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
else:
    config.measurespath = flags.measurespath

# watch for measurespath of None, that likely means that casasiteconfig.py is in use and this has not been set. It can't be used then.
try:
    if flags.measurespath is None:
        print("measurespath has been set to None in the user or site config file.")
        print("Either provide a measurespath on the casaconfig command line or edit the user or site config file to set measurespath to a location.")
        sys.exit(1)

    # do any expanduser and abspath - this is what should be used
    measurespath = os.path.abspath(os.path.expanduser(flags.measurespath))

    if flags.currentdata:
        if not os.path.exists(measurespath) or not os.path.isdir(measurespath):
            print("No data installed at %s. The measurespath does not exist or is not a directory." % measurespath)
        else:
            print("current data installed at %s" % measurespath)
            dataInfo = casaconfig.get_data_info(measurespath)
        
            # casarundata
            casarunInfo = dataInfo['casarundata']
            if casarunInfo is None or casarunInfo['version'] == "invalid":
                print("No casarundata found (missing readme.txt and not obviously legacy casa data).")
            if casarunInfo['version'] == "error":
                print("Unexpected casarundata readme.txt content; casarundata should be reinstalled.")
            elif casarunInfo['version'] == "unknown":
                print("casarundata version is unknown (probably legacy casa data not maintained by casaconfig).")
            else:
                currentVersion = casarunInfo['version']
                currentDate = casarunInfo['date']
                print('casarundata version %s installed on %s' % (currentVersion, currentDate))
            
            # measures
            measuresInfo = dataInfo['measures']
            if measuresInfo is None or measuresInfo['version'] == "invalid":
                print("No measures data found (missing readme.txt and not obviously legacy measures data).")
            if measuresInfo['version'] == "error":
                print("Unexpected measures readme.txt content; measures should be reinstalled.")
            elif measuresInfo['version'] == "unknown":
                print("measures version is unknown (probably legacy measures data not maintained by casaconfig).")
            else:
                currentVersion = measuresInfo['version']
                currentDate = measuresInfo['date']
                print('measures version %s installed on %s' % (currentVersion, currentDate))
 
        # ignore any other arguments
    elif flags.summary:
        from casaconfig.private.summary import summary
        summary(config)
        # ignore any other arguments
    else:
        if flags.referencetesting:
            print("reference testing using pull_data and 'release' version into %s" % measurespath)
            casaconfig.pull_data(measurespath,'release')
            # ignore all other options
        else:
            # watch for nothing actually set
            if not flags.updateall and not flags.pulldata and not flags.dataupdate and not flags.measuresupdate:
                parser.print_help()
                sys.exit(1)
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

except casaconfig.UnsetMeasurespath as exc:
    # UnsetMeasurespath should not happen because measurespath is checked to not be None above, but just in case
    print(str(exc))
    print("This exception should not happen, check the previous messages for additional information and try a different path")
    sys.exit(1)

except casaconfig.BadReadme as exc:
    print(str(exc))
    sys.exit(1)

except casaconfig.RemoteError as exc:
    print(str(exc))
    print("This is likely due to no network connection or bad connectivity to a remote site, wait and try again")
    sys.exit(1)

except casaconfig.BadLock as exc:
    # the output produced by the update functions is sufficient, just re-echo the exception text itself
    print(str(exc))
    sys.exit(1)

except casaconfig.NotWritable as exc:
    print(str(exc))
    sys.exit(1)

sys.exit(0)
