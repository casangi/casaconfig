import unittest
import os, shutil, sys, subprocess
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

        if os.path.exists(os.path.join(os.getcwd(), 'measures')):
            shutil.rmtree(os.path.join(os.getcwd(), 'measures'))

        if os.path.isfile(os.path.expanduser("~/.casa/config.py.user")):
            os.replace(os.path.expanduser("~/.casa/config.py.user"), os.path.expanduser("~/.casa/config.py"))


    def test_casaconfig_get_data_dir(self):
        '''Test casaconfig populated data folder exists in casaconfig module'''
        self.assertEqual(os.path.realpath(casaconfig.get_data_dir()),os.path.realpath('{}/casaconfig/__data__/'.format(sitepackages)))

    def test_file_exists(self):
        '''Test Default config.py exists in casaconfig module'''
        self.assertTrue(os.path.isfile('{}/casaconfig/config.py'.format(sitepackages)))

    def test_import_casatools(self):
        '''Test that import casatools will return ImportError with rundata not set'''
        # Test May need to be restructured
        # Due to casatools / casaconfig caching, run the import of casatools in a shell with an empty config and read stdout/stderr for ImportError

        f = open(self.test_configpath,"w")
        f.write("# Test Config File\n")
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

        today = date.today()
        yesterday = today - timedelta(days=1)

        measuresdata_yesterday= "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))

        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'measures'), version=measuresdata_yesterday, force=False, logger=None)
        dir1 = os.path.isdir(os.path.expanduser(os.path.join(os.getcwd(), 'measures', 'ephemerides')))
        dir2 = os.path.isdir(os.path.expanduser(os.path.join(os.getcwd(), 'measures', 'geodetic')))

        self.assertTrue(dir1 and dir2)


    def test_casaconfig_measures_update(self):
        '''Test downgrade to upgrade measures data to location'''

        today = date.today()
        yesterday = today - timedelta(days=1)
        measuresdata_today = "WSRT_Measures_{}-160001.ztar".format(today.strftime("%Y%m%d"))
        measuresdata_yesterday= "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))

        # Downgrade
        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'measures'), version=measuresdata_yesterday, force=False, logger=None)

        # Upgrade
        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'measures'), version=measuresdata_today, force=False, logger=None)

        dir1 = os.path.isdir(os.path.expanduser(os.path.join(os.getcwd(), 'measures', 'ephemerides')))
        dir2 = os.path.isdir(os.path.expanduser(os.path.join(os.getcwd(), 'measures', 'geodetic')))

        self.assertTrue(dir1 and dir2)


    def test_read_rundata_from_user_config(self):
        '''Test casaconfig downloads specific data to location and casatools reads that data location'''
        try:
            del casaconfig
        except:
            pass

        try:
            del casatools
        except:
            pass

        today = date.today()
        yesterday = today - timedelta(days=1)

        measuresdata_yesterday= "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))

        f = open(self.test_configpath,"w")
        f.write("# Test Config File\n")
        f.write('rundata = "{}"\n'.format(os.path.join(os.getcwd(), 'measures')))
        f.close()

        import casaconfig
        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'measures'), version=measuresdata_yesterday, force=False, logger=None)

        import casatools

        self.assertEqual(casatools.utils.utils().rundata(), os.path.join(os.getcwd(), 'measures'))

        if 'casatools' in sys.modules:
            sys.modules.pop("casatools",None)

    def test_update_populate(self):
        '''Test Automatic Updates to datapath'''

        today = date.today()
        yesterday = today - timedelta(days=1)

        measuresdata_yesterday= "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))

        f = open(self.test_configpath,"w")
        f.write("# Test Config File\n")
        f.write('datapath = ["{}"]\n'.format(os.path.join(os.getcwd(), 'measures')))
        f.write('rundata = "{}"\n'.format(os.path.join(os.getcwd(), 'measures')))
        f.write('populate_data = True\n')
        f.write('measures_update = True\n')
        f.close()

        casaconfig.measures_update(path=os.path.join(os.getcwd(), 'measures'), version=measuresdata_yesterday, force=False, logger=None)

        proc = subprocess.Popen('{} -c "import casatools"'.format(sys.executable), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()

        ref = True if "WSRT_Measures_{}-160001.ztar".format(today.strftime("%Y%m%d")) in str(output) else False
        self.assertTrue(ref, "Update Failed")


if __name__ == '__main__':

    unittest.main()
