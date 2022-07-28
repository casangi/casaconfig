import unittest
import os, shutil, stat, sys, subprocess
from datetime import date, timedelta
import importlib
import site
sitepackages = site.getsitepackages()[0]

import casaconfig

class casaconfig_test(unittest.TestCase):

    def setUp(self):
        if os.path.isfile(os.path.expanduser("~/.casa/config.py")):
            os.replace(os.path.expanduser("~/.casa/config.py"), os.path.expanduser("~/.casa/config.py.user"))

        self.test_configpath =  os.path.join(os.path.expanduser("~/.casa/"),"config.py")

    def tearDown(self):
        if os.path.isfile(self.test_configpath):
            os.remove(self.test_configpath)

        if os.path.exists(os.path.join(os.getcwd(), 'testmeasures')):
            shutil.rmtree(os.path.join(os.getcwd(), 'testmeasures'))

        if os.path.exists(os.path.join(os.getcwd(), 'emptymeasures')):
            shutil.rmtree(os.path.join(os.getcwd(), 'emptymeasures'))

        if os.path.isfile(os.path.expanduser("~/.casa/config.py.user")):
            os.replace(os.path.expanduser("~/.casa/config.py.user"), os.path.expanduser("~/.casa/config.py"))


    def test_casaconfig_get_data_dir(self):
        '''Test casaconfig populated data folder exists in casaconfig module'''
        self.assertEqual(os.path.realpath(casaconfig.get_data_dir()),os.path.realpath('{}/casaconfig/__data__/'.format(sitepackages)))

    def test_file_exists(self):
        '''Test Default config.py exists in casaconfig module'''
        self.assertTrue(os.path.isfile('{}/casaconfig/config.py'.format(sitepackages)))

    def test_import_casatools(self):
        '''Test that import casatools will return ImportError with measurespath set to an empty directory that cannot be written to'''
        # Due to casatools / casaconfig caching, run the import of casatools and read stdout/stderr for ImportError
        # after first creating an empty measurespath directory with the write permissions turned off
        # and then creating a test config file using the path to that directory as measurespath

        emptyPath = os.path.join(os.getcwd(), 'emptymeasures')
        if (not os.path.exists(emptyPath)) : os.mkdir(emptyPath)
        # the current permissions
        pstat = stat.S_IMODE(os.stat(emptyPath).st_mode)
        # a bitmask that's the opposite of all of the write permission bits
        no_write = ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
        # remove the write permissions
        pstat = pstat & no_write
        os.chmod(emptyPath,pstat)

        f = open(self.test_configpath,"w")
        f.write("# Test Config File\n")
        f.write("measurespath='%s'\n" % emptyPath)
        f.close()
        proc = subprocess.Popen('{} -c "import casatools"'.format(sys.executable), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()

        ref = True if "ImportError" in str(output) else False
        self.assertTrue(ref, "ImportError Not Found")

    def test_casaconfig_measures_available(self):
        '''Test That Today or Yesterday measures data is returned'''

        today = date.today()
        yesterday = today - timedelta(days=1)
        measuresdata_today = "WSRT_Measures_{}-160001.ztar".format(today.strftime("%Y%m%d"))
        measuresdata_yesterday= "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))

        self.assertTrue(any(elem in casaconfig.measures_available() for elem in [measuresdata_today, measuresdata_yesterday]))

    def test_casaconfig_measures_downgrade(self):
        '''Test downgrade measures data to location'''

        # today's WSRT measures tar might not yet exist and yesterdays might already be installed
        # use 2 days ago to make sure that the version is downgraded
        today = date.today()
        pastdate = today - timedelta(days=2)

        measuresdata_past= "WSRT_Measures_{}-160001.ztar".format(pastdate.strftime("%Y%m%d"))

        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'testmeasures'), version=measuresdata_past, force=False, logger=None)
        dir1 = os.path.isdir(os.path.expanduser(os.path.join(os.getcwd(), 'testmeasures', 'ephemerides')))
        dir2 = os.path.isdir(os.path.expanduser(os.path.join(os.getcwd(), 'testmeasures', 'geodetic')))

        self.assertTrue(dir1 and dir2)


    def test_casaconfig_measures_update(self):
        '''Test downgrade to upgrade measures data to location'''

        # today's WSRT measures tar might not yet exist and yesterdays might already be installed
        # use 2 days ago to make sure that the version is downgraded
        # and then update it to yesterday to check that it is updated
        today = date.today()
        yesterday = today - timedelta(days=1)
        pastdate = today - timedelta(days=2)
        measuresdata_past = "WSRT_Measures_{}-160001.ztar".format(pastdate.strftime("%Y%m%d"))
        measuresdata_yesterday= "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))

        # Downgrade
        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'testmeasures'), version=measuresdata_past, force=False, logger=None)

        # Upgrade
        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'testmeasures'), version=measuresdata_yesterday, force=False, logger=None)

        dir1 = os.path.isdir(os.path.expanduser(os.path.join(os.getcwd(), 'testmeasures', 'ephemerides')))
        dir2 = os.path.isdir(os.path.expanduser(os.path.join(os.getcwd(), 'testmeasures', 'geodetic')))

        self.assertTrue(dir1 and dir2)


    def test_read_measurespath_from_user_config(self):
        '''Test casaconfig downloads specific data to location and casatools reads that data location'''

        # today may not yet exist, use yesterday to request a date that should exist
        today = date.today()
        yesterday = today - timedelta(days=1)

        measuresdata_yesterday= "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))

        # start a fresh process with a test config file setting measurespath to a local testmeasures
        # directory; in that process, import casaconfig and update the measures data to yesterday
        # then import casatools and verify that utils measurespath agrees with casaconfig measurespath

        # that can't be done in this process because casaconfig has likely already been imported and set

        testMeasuresPath = os.path.join(os.getcwd(),'testmeasures')

        fc = open(self.test_configpath,"w")
        fc.write("# Test Config File\n")
        fc.write('measurespath = "{}"\n'.format(testMeasuresPath))
        fc.close()


        # the test script to execute via the "-c" option in the process
        # the string is enclosed in double quotes when used, so only single quotes should appear within the string
        test_string = ''
        test_string += "import casaconfig; "
        test_string += "casaconfig.measures_update(path='{}',version='{}',force=False,logger=None); ".format(testMeasuresPath,measuresdata_yesterday)
        test_string += "import casatools; "
        test_string += "assert('{}' == casatools.utils.utils().measurespath())".format(testMeasuresPath)

        proc = subprocess.Popen('{} -c "{}"'.format(sys.executable,test_string), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()

        ref = False if "AssertionError" in str(output) else True
        self.assertTrue(ref, "AssertionError seen in output : expected utils().measurespath() was not seen")

    def test_update_populate(self):
        '''Test Automatic Updates to datapath'''

        # force a download by going back 2 days since the loaded version may still be yesterday (today may not yet be available)
        today = date.today()
        yesterday = today - timedelta(days=1)
        pastdate = today - timedelta(days=2)

        measuresdata_today = "WSRT_Measures_{}-160001.ztar".format(today.strftime("%Y%m%d"))
        measuresdata_yesterday = "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))
        measuresdata_past = "WSRT_Measures_{}-160001.ztar".format(pastdate.strftime("%Y%m%d"))

        testmeasurespath = os.path.join(os.getcwd(),'testmeasures')

        f = open(self.test_configpath,"w")
        f.write("# Test Config File\n")
        f.write('datapath = ["{}"]\n'.format(testmeasurespath))
        f.write('measurespath = "{}"\n'.format(testmeasurespath))
        f.write('populate_data = True\n')
        f.write('measures_update = True\n')
        f.close()

        # this degrades testmeasures to 2 days ago
        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'testmeasures'), version=measuresdata_past, force=False, logger=None)
        # but the geodetic/readme.txt will have today's date in the ndate field, revert that to 2 days ago so that casatools will update it
        # this duplcates the code in measures_update so would need to change if the format of the readme changes
        with open(os.path.join(testmeasurespath,'geodetic/readme.txt'), 'w') as fid:
            fid.write("# measures data populated by casaconfig\nversion : %s\ndate : %s" % (measuresdata_past, pastdate.strftime('%Y-%m-%d')))

        # start a new casatools, which should update the measures to the more recent version
        proc = subprocess.Popen('{} -c "import casatools"'.format(sys.executable), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()

        # output should contain today's or yesterday's measures data file name
        ref = (measuresdata_today in str(output)) or (measuresdata_yesterday in str(output))
        self.assertTrue(ref, "Update Failed")


if __name__ == '__main__':

    unittest.main()
