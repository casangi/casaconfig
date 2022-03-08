# Updated version to support the current JPL-Horizons query results as of 2013 June.
# (when S-T-O is requested the current query result returns phi, PAB-LON, PAB-LAT along
# with S-T-O value).
#
# casapy functions for converting ASCII ephemerides from JPL-Horizons into
# CASA tables and installing them where casapy can find them.
#
# jplfiles_to_repository() puts it all together, so it is most likely the
# function you want.
#
# There are various utilities like convert_radec, datestr*, get_num_from_str,
# mean_radius*, and construct_tablepath defined in here as well.


from __future__ import absolute_import
from __future__ import print_function
from glob import glob
import os
import re
import sys
import scipy.special
import time                  # We can always use more time.
import numpy

# get is_python3 and is_CASA6
from casatasks.private.casa_transition import *
if is_CASA6:
    from casatools import quanta, measures
    from casatools import table as tbtool
    from casatasks import casalog

    _qa = quanta( )
    _me = measures( )
else:
    from taskinit import gentools, tbtool, qa, casalog

    _me = gentools(['me'])[0]
    # not really a local tool
    _qa = qa

# Possible columns, as announced by their column titles.
# The data is scooped up by 'pat'.  Either use ONE group named by the column
# key, or mark it as unwanted.  '-' is not valid in group names.
# Leading and trailing whitespace will be taken care of later.
# Sample lines:
#  Date__(UT)__HR:MN     R.A.___(ICRF/J2000.0)___DEC Ob-lon Ob-lat Sl-lon Sl-lat   NP.ang   NP.dist               r        rdot            delta      deldot    S-T-O   L_s
#  2010-May-01 00:00     09 01 43.1966 +19 04 28.673 286.52  18.22 246.99  25.34 358.6230      3.44  1.661167637023  -0.5303431 1.28664311447968  15.7195833  37.3033   84.50
# 
# some mod to label names and comments so that they corresponds to
# JPL-Horizons naming comvension
cols = {
    'MJD': {'header': r'Date__\(UT\)__HR:MN(:)?(\w+)?(\.)?(\w+)?',
            'comment': 'date',
            'pat':     r'(?P<MJD>\d+-\w+-\d+ \d+:\d+)'},
    'RA': {'header': r'R.A._+\([^)]+',
           'comment': 'Right Ascension',
           'pat':    r'(?P<RA>(\d+ \d+ )?\d+\.\d+)'}, # require a . for safety
    'DEC': {'header': r'\)_+DEC.',
            'comment': 'Declination',
            'pat':    r'(?P<DEC>([-+]?\d+ \d+ )?[-+]?\d+\.\d+)'},
    'NP_ang': {'header': r'NP\.ang',
               'comment': 'North-Pole pos. angle',
               'pat': r'(?P<NP_ang>[0-9.]+|n\.a\.)',
               'unit': 'deg'},
    'NP_dist': {'header': r'NP\.dist',
                'comment': 'North-Pole ang. distance',
               'pat': r'(?P<NP_dist>[-+0-9.]+|n\.a\.)',
                'unit': 'arcsec'},
    'illu': {'header': r'Illu%',
             #'comment': 'Illumination',
             'comment': 'Illuminated fraction',
             'pat':    r'(?P<illu>[0-9.]+)',
             'unit': r'%'},
    # put back to original heading...
    # TT: query result header name change (sometime in 2018) 
    # Ob_lon -> Obsrv_lon, Ob_lat->Obsrv_lat,  
    # Sl_lon -> Solar-lon, Sl_lat ->Solar-lat 
    #'DiskLong': {'header': r'Ob-lon',
    'DiskLong': {'header': r'Obsrv-lon',
               'comment': 'Sub-observer longitude',
    #           'pat':    r'(?P<Obs_Long>[0-9.]+|n\.a\.)',
               'pat':    r'(?P<DiskLong>[0-9.]+|n\.a\.)',
               'unit': 'deg'},
    #'DiskLat': {'header': r'Ob-lat',
    'DiskLat': {'header': r'Obsrv-lat',
               'comment': 'Sub-observer latitude',
    #           'pat':    r'(?P<Obs_Lat>[-+0-9.]+|n\.a\.)',
               'pat':    r'(?P<DiskLat>[-+0-9.]+|n\.a\.)',
               'unit': 'deg'},
    #'Sl_lon': {'header': r'Sl-lon',
    'Sl_lon': {'header': r'Solar-lon',
               'comment': 'Sub-Solar longitude',
               'pat':    r'(?P<Sl_lon>[0-9.]+|n\.a\.)',
               'unit': 'deg'},
    #'Sl_lat': {'header': r'Sl-lat',
    'Sl_lat': {'header': r'Solar-lat',
               'comment': 'Sub-Solar longitude',
               'pat':    r'(?P<Sl_lat>[-+0-9.]+|n\.a\.)',
               'unit': 'deg'},

    # These are J2000 whether or not ra and dec are apparent directions.
    'NP_RA': {'header': r'N\.Pole-RA',
              'comment': 'North Pole right ascension',
              'pat':    r'(?P<NP_RA>(\d+ \d+ )?\d+\.\d+)'}, # require a . for safety
    'NP_DEC': {'header': r'N\.Pole-DC',
               'comment': 'North Pole declination',
               'pat':    r'(?P<NP_DEC>([-+]?\d+ \d+ )?[-+]?\d+\.\d+)'},
    
    'r': {'header': 'r',
          'comment': 'heliocentric distance',
          'unit':    'AU',
          'pat':     r'(?P<r>[0-9.]+)'},
    'rdot': {'header': 'rdot',
             #'comment': 'heliocentric velocity',
             'comment': 'heliocentric distance rate',
             'unit': 'km/s',
             'pat': r'(?P<rdot>[-+0-9.]+)'},
    #         'unwanted': True},
    'Rho': {'header': 'delta',
            'comment': 'geocentric distance',
            'unit':    'AU',
            'pat':     r'(?P<Rho>[0-9.]+)'},
    'RadVel': {'header': 'deldot',
               #'comment': 'Radial velocity relative to the observer',
               'comment': 'geocentric distance rate',
               'pat': r'(?P<RadVel>[-+0-9.]+)',
               'unit': 'km/s'},
    'phang': {'header':  'S-T-O',
              'comment': 'phase angle',
              'unit':    'deg',
              'pat':     r'(?P<phang>[0-9.]+)'},
    # added columns to match current(as of June 2013) query result 
    'phi': {'header':  'phi',
	    'comment': 'phase angle',
	    'unit':    'deg',
            'pat':     r'(?P<phi>[0-9.]+)',
            'unwanted': True},
    'PAB_LON': {'header':  'PAB-LON',
	    'comment': 'ecliptic longitude',
	    'unit':    'deg',
            'pat':     r'(?P<PAB_LON>[0-9.]+)',
            'unwanted': True},
    'PAB_LAT': {'header':  'PAB-LAT',
	    'comment': 'ecliptic latitude',
	    'unit':    'deg',
            'pat':     r'(?P<PAB_LAT>[-+0-9.]+)',
            'unwanted': True},
    # -----------------------------------------------------------
    'ang_sep': {'header': 'ang-sep/v',
                'comment': 'Angular separation from primary',
                'pat': r'(?P<ang_sep>[0-9.]+/.)'},  # arcsec, "visibility code".
                                                    # t: transiting primary
                                                    # O: occulted by primary
                                                    # p: partial umbral eclipse
                                                    # P: occulted partial umbral eclipse
                                                    # u: total umbral eclipse
                                                    # U: occulted total umbral eclipse
                                                    # *: none of the above
                                                    # -: target is primary
    'L_s': {'header': 'L_s',  # 08/2010: JPL does not supply this and
            'unit': 'deg',    # says they cannot.  Ask Bryan Butler.
            'comment': 'Season angle',
            'pat': r'(?P<L_s>[-+0-9.]+)'}

    }

def readJPLephem(fmfile,version=''):
    """
    Reads a JPL Horizons text file (see
    http://ssd.jpl.nasa.gov/horizons.cgi#top ) for a solar system object and
    returns various quantities in a dictionary.  The dict will be blank ({}) if
    there is a failure.
    """
    retdict = {}
    casalog.origin('readJPLephem')

    # Try opening fmfile now, because otherwise there's no point continuing.
    try:
        ephem = open(fmfile, 'rb')
        print("opened the file=%s" % fmfile)
        lines=ephem.readlines()
        # skip this, handle by rstrip later
        #crCount=0
        #newlines=''
        #newln=''
        #for ln in lines:
        #  n = ln.count('\r')
        #  if n > 0:
        #    newln=ln.replace('\r','\n')
        #    crCount+=n
        #    newlines += newln
        #if crCount > 0:
        #  print "The input file appears to contains the carriage return code, \'^M\', will replace it with \'\\n\'..."
        #  raw_input('pause0')
        #  ephem.close()
        #  ephem = open('temp_ephem_data.txt','w+')
        #  ephem.write(newlines)
        ephem.seek(0)
    except IOError:
        casalog.post("Could not open ephemeris file " + fmfile,
                     priority="SEVERE")
        return {}

    # reset to default search pattern for MJD
    cols['MJD']['pat']=r'(?P<MJD>\d+-\w+-\d+ \d+:\d+)'
    # Setup the regexps.

    # Headers (one time only things)
    
    # Dictionary of quantity label: regexp pattern pairs that will be searched
    # for once.  The matching quantity will go in retdict[label].  Only a
    # single quantity (group) will be retrieved per line.
    headers = {
        'NAME': {'pat': r'^[>\s]*Target body name:\s+\d*\s*(\w+)'},   # object name, w.o. number
        'ephtype': {'pat': r'\?s_type=1#top>\]\s*:\s+\*(\w+)'}, # e.g. OBSERVER
        'obsloc': {'pat': r'^[>\s]*Center-site name:\s+(\w+)'},        # e.g. GEOCENTRIC
        # Catch either an explicit mean radius or a solitary target radius.
        'meanrad': {'pat': r'(?:Mean radius \(km\)\s*=|^Target radii\s*:)\s*([0-9.]+)(?:\s*km)?\s*$',
                    'unit': 'km'},
        # Triaxial target radii
        #'radii': {'pat': r'Target radii\s*:\s*([0-9.]+\s*x\s*[0-9.]+\s*x\s*[0-9.]+)\s*km.*Equator, meridian, pole',
        'radii': {'pat': r'Target radii\s*:\s*([0-9.]+\s*x\s*[0-9.]+\s*x\s*[0-9.]+)\s*km.*Equator, meridian, pole|Target radii\s*:\s*([0-9.]+)\s*km\s*',
                  'unit': 'km'},
        'T_mean': {'pat': r'Mean Temperature \(K\)\s*=\s*([0-9.]+)',
                   'unit': 'K'},

         # Figure out the units later.
        'rot_per': {'pat': r'(?i)(?<!Inferred )\b(rot(ation(al)?|\.)?\s*per.*=\s*([-0-9.]+\s*[dhr]*|Synchronous))'},
        'orb_per': {'pat': r'Orbital period((, days)?\s*=\s*[-0-9.]+\s*[dhr](\s*\(?R\)?)?)'},

        # MeasComet does not read units for these! E-lon(deg),  Lat(deg),     Alt(km)
        'GeoLong': {'pat': r'^[>\s]*Center geodetic\s*: ([-+0-9.]+,\s*[-+0-9.]+,\s*[-+0-9.]+)'},
        'dMJD':    {'pat': r'^[>\s]*Step-size\s*:\s*(.+)'},

        #                     request method v  wday mth   mday  hh  mm  ss   yyyy
        'VS_CREATE': {'pat': r'^[>\s]*Ephemeris / \w+ \w+ (\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)'}
        }
    for hk in headers:
        headers[hk]['pat'] = re.compile(headers[hk]['pat'])

    # Data ("the rows of the table")
    
    # need date, r (heliocentric distance), delta (geocentric distance), and phang (phase angle).
    # (Could use the "dot" time derivatives for Doppler shifting, but it's
    # likely unnecessary.)
    #datapat = r'^[>\s]*'
    datapat = r'^\s*'

    stoppat = r'[>\s]*\$\$EOE$'  # Signifies the end of data.

    # Read fmfile into retdict.
    num_cols = 0
    in_data = False
    comp_mismatches = []
    print_datapat = False
    # define interpretation of invalid values ('n.a.')
    invalid=-999.
    for origline in ephem:
        if is_python3:
            #line = origline.decode("utf-8").rstrip('\r\n')
            line = origline.decode(sys.getdefaultencoding( ),"strict").rstrip('\r\n')
        else:
            line = origline.rstrip('\r\n')
        if in_data:
            if re.match(stoppat, line):
                break
            matchobj = re.search(datapat, line)
            if matchobj:
                #print "matchobj!"
                gdict = matchobj.groupdict()
                #print "gdict=",gdict
                for col in gdict:
                    if gdict[col]=='n.a.':
                        gdict[col]=invalid
                #    print "cols.key=",cols.keys()
 
                    if not cols[col].get('unwanted'):
                        retdict['data'][col]['data'].append(gdict[col])
                if len(gdict) < num_cols:
                    print("Partially mismatching line:")
                    print(line)
                    print("Found:")
                    print(gdict)
                    print_datapat = True
                    raw_input("pause0")
            else:
                print_datapat = True
                # Chomp trailing whitespace.
                comp_mismatches.append(re.sub(r'\s*$', '', line))
        elif re.match(r'^[>\s]*' + cols['MJD']['header'] + r'\s+'
                      + cols['RA']['header'], line):
            # need to modify regex to search for the header name for MJD containing second digits
            if re.match(r'^[>\s]*Date__\(UT\)__HR:MN:SC.fff', line):
                cols['MJD']['pat'] = r'(?P<MJD>\d+-\w+-\d+ \d+:\d+:\d+.\d+)'
            # See what columns are present, and finish setting up datapat and
            # retdict.
            havecols = []
            # extract coordinate ref info

            m=re.match(r'(^[>\s]*)(\S+)(\s+)('+cols['RA']['header']+')', line)
            coordref=m.group(4).split('(')[-1]
            cols['RA']['comment']+='('+coordref+')'
            cols['DEC']['comment']+='('+coordref+')'
            #print "cols['RA']['comment']=",  cols['RA']['comment']
            # Chomp trailing whitespace.
            myline = re.sub(r'\s*$', '', line)
            titleline = myline
            remaining_cols = list(cols.keys())
            found_col = True
            # This loop will terminate one way or another.
            while myline and remaining_cols and found_col:
                found_col = False
                #print "myline = '%s'" % myline
                #print "remaining_cols =", ', '.join(remaining_cols)
                for col in remaining_cols:
                    if re.match(r'^[>\s]*' + cols[col]['header'], myline):
                        #print "Found", col
                        havecols.append(col)
                        remaining_cols.remove(col)
                        myline = re.sub(r'^[>\s]*' + cols[col]['header'],
                                        '', myline)
                        found_col = True
                        break
            datapat += r'\s+'.join([cols[col]['pat'] for col in havecols])
            sdatapat = datapat
            casalog.post("Found columns: " + ', '.join(havecols))
            datapat = re.compile(datapat)
            retdict['data'] = {}
            for col in havecols:
                if not cols[col].get('unwanted'):
                    retdict['data'][col] = {'comment': cols[col]['comment'],
                                            'data':    []}
            num_cols = len(retdict['data'])
        #elif re.match(r'^\$\$SOE\s*$', line):  # Start of ephemeris
        elif re.match(r'^[>\s]*\$\$SOE\s*$', line):  # Start of ephemeris
            casalog.post("Starting to read data.", priority='INFO2')
            in_data = True
        else:
            #print "line =", line
            #print "looking for", 
            for hk in headers:
                 #print "hk=",hk

                 if not hk in retdict:
                    matchobj = re.search(headers[hk]['pat'], line)
                    if matchobj:
                        if hk=='radii':
                            mobjs=matchobj.groups()
                            for gp in mobjs:
                                if gp!=None:
                                    retdict[hk] = gp
                                    break
                            break
                        else:
                            retdict[hk] = matchobj.group(1) # 0 is the whole line
                            break
    ephem.close()
    # clean up the temp file if exists
    #if os.path.exists('temp_ephem_data.txt'):
    #  os.remove('temp_ephem_data.txt')

    # If there were errors, provide debugging info.
    if comp_mismatches:
        print("Completely mismatching lines:")
        #print "\n".join(comp_mismatches)
    if print_datapat:
        print("The apparent title line is:")
        print(titleline)
        print("datapat = r'%s'" % sdatapat)

    # Convert numerical strings into actual numbers.
    try:
        retdict['earliest'] = datestr_to_epoch(retdict['data']['MJD']['data'][0])
        retdict['latest'] = datestr_to_epoch(retdict['data']['MJD']['data'][-1])
    except Exception:
        print("Error!")
        if 'data' in retdict:
            if 'MJD' in retdict['data']:
                if 'data' in retdict['data']['MJD']:
                    #print "retdict['data']['MJD']['data'] =", retdict['data']['MJD']['data']
                    print("retdict['data'] = %s" % retdict['data'])
                else:
                    print("retdict['data']['MJD'] has no 'data' key.")
                    print("retdict['data']['MJD'].keys() = %s" % retdict['data']['MJD'].keys())
            else:
                print("retdict['data'] has no 'MJD' key.")
                print("retdict['data'].keys() = %s" % retdict['data'].keys())
        else:
            print("retdict has no 'data' key.")
        raise

    for hk in headers:
        if hk in retdict:
            if 'unit' in headers[hk]:
                if hk == 'radii':
                    radii = retdict[hk].split('x')
                    if len(radii)==1:
                        a = float(radii[0])
                        retdict[hk] = {'unit': headers[hk]['unit'], 'value': (a,a,a)}
                        retdict['meanrad'] = {'unit': headers[hk]['unit'],
                                          'value': a}
                    else:
                        a, b, c = [float(r) for r in radii]
                        retdict[hk] = {'unit': headers[hk]['unit'],
                                   'value': (a, b, c)}
                        retdict['meanrad'] = {'unit': headers[hk]['unit'],
                                          'value': mean_radius(a, b, c)}
                else:
                    try:
                        # meanrad might already have been converted.
                        if type(retdict[hk]) != dict:
                            retdict[hk] = {'unit': headers[hk]['unit'],
                                           'value': float(retdict[hk])}
                    except Exception:
                        print("Error converting header %s to a Quantity." % hk)
                        print("retdict[hk] = %s" % retdict[hk])
                        raise
            elif hk == 'GeoLong':
                long_lat_alt = retdict[hk].split(',')
                retdict['GeoLong'] = float(long_lat_alt[0])
                retdict['GeoLat']  = float(long_lat_alt[1])
                retdict['GeoDist'] = float(long_lat_alt[2])
            elif hk == 'dMJD':
                retdict[hk] = _qa.convert(_qa.totime(retdict[hk].replace('minutes', 'min')),
                                         'd')['value']
            elif hk == 'orb_per':
                unit = 'h'
                retrograde = False
                if 'd' in retdict[hk].lower():
                    unit = 'd'                 # Actually this is most common.
                if 'r' in retdict[hk].lower():
                    retrograde = True
                value = get_num_from_str(retdict[hk], 'orbital period')
                if value != False:
                    if retrograde and value > 0.0:
                        value = -value
                    retdict[hk] = {'unit': unit, 'value': value}
                else:
                    del retdict[hk]
                    
    # The rotation period might depend on the orbital period ("Synchronous"),
    # so handle it after all the other headers have been done.
    if 'rot_per' in retdict:
        rpstr = retdict['rot_per']
        if 'ROTPER' in rpstr:                            # Asteroid
            retdict['rot_per'] = {'unit': 'h',         # Always seems to be for asteroids.
                                  'value': get_num_from_str(rpstr, 'rotation period')}
        elif 'Synchronous' in rpstr:
            retdict['rot_per'] = retdict['orb_per']
        else:  # Most likely a planet.
            match = re.search(r'(\d+)h\s*(\d+)m\s*([0-9.]+)s', rpstr)
            if match:
                hms = [float(match.group(i)) for i in range(1, 4)]
                retdict['rot_per'] = {'unit': 'h',
                                      'value': hms[0] + (hms[1] + hms[2] / 60.0) / 60.0}
            else:
                # DON'T include the optional r in hr!  qa.totime can't handle it.
                try:
                    match = re.search(r'([-0-9.]+)(?:\s*\+-[0-9.]+)?\s*([dh])', rpstr)
                    if match:
                        retdict['rot_per'] = {'unit': match.group(2),
                                              'value': float(match.group(1))}
                except:
                    print("Error parsing the rotation period from")
                    print(rpstr)
    
    if 'ang_sep' in retdict['data']:
        retdict['data']['obs_code'] = {'comment': 'Obscuration code'}
    for dk in retdict['data']:
        if dk == 'obs_code':
            continue
        if 'unit' in cols[dk]:
            retdict['data'][dk]['data'] = {'unit': cols[dk]['unit'],
                      'value': scipy.array([float(s) for s in retdict['data'][dk]['data']])}
            if dk == 'RadVel':
                # Convert from km/s to AU/d.  Blame MeasComet, not me.
                retdict['data'][dk]['data']['unit'] = 'AU/d'
                kmps_to_AUpd = _qa.convert('1km/s', 'AU/d')['value']
                retdict['data'][dk]['data']['value'] *= kmps_to_AUpd

        if re.match(r'.*(RA|DEC)$', dk):
            retdict['data'][dk] = convert_radec(retdict['data'][dk])
        elif dk == 'MJD':
            retdict['data']['MJD'] = datestrs_to_MJDs(retdict['data']['MJD'])
        elif dk == 'ang_sep':
            angseps = []
            obscodes = []
            for asoc in retdict['data'][dk]['data']:
                angsep, obscode = asoc.split('/')
                angseps.append(float(angsep))
                obscodes.append(obscode)
            retdict['data'][dk]['data'] = {'unit': 'arcseconds',
                                           'value': angseps}
            retdict['data']['obs_code']['data'] = obscodes

    if len(retdict.get('radii', {'value': []})['value']) == 3 \
           and 'NP_RA' in retdict['data'] and 'NP_DEC' in retdict['data']:
        # Do a better mean radius estimate using the actual theta.
        retdict['meanrad']['value'] = mean_radius_with_known_theta(retdict)

    # To be eventually usable as a MeasComet table, a few more keywords are needed.
    retdict['VS_TYPE'] = 'Table of comet/planetary positions'
    if version=='':
        version='0003.0001'
    #retdict['VS_VERSION'] = '0003.0001'
    retdict['VS_VERSION'] = version 
    if 'VS_CREATE' in retdict:
        dt = time.strptime(retdict['VS_CREATE'], "%b %d %H:%M:%S %Y")
    else:
        casalog.post("The ephemeris creation date was not found.  Using the current time.",
                     priority="WARN")
        dt = time.gmtime()
    retdict['VS_CREATE'] = time.strftime('%Y/%m/%d/%H:%M', dt)

    # VS_DATE is required by MeasComet, but it doesn't seem to be actually used.
    retdict['VS_DATE'] = time.strftime('%Y/%m/%d/%H:%M', time.gmtime())

    if 'MJD' in retdict['data']:
        #casalog.post("retdict.keys=%s" % retdict.keys())
        retdict['MJD0'] = retdict['data']['MJD']['value'][0] - retdict['dMJD']
    else:
        print("The table will not be usable with me.framecomet because it lacks MJD.")

    # adding posrefsys keyword
    if cols['RA']['comment'].count('J2000'):
        retdict['posrefsys']='ICRF/J2000.0'
    if cols['RA']['comment'].count('B1950'):
        retdict['posrefsys']='FK4/B1950.0'
   
    return retdict

def convert_radec(radec_col):
    """
    Returns a column of RAs or declinations as strings, radec_col, as a
    quantity column.  (Unfortunately MeasComet assumes the columns are
    Quantities instead of Measures, and uses GeoDist == 0.0 to toggle between
    APP and TOPO.)
    """
    angstrlist = radec_col['data']
    angq = {}
    nrows = len(angstrlist)

    if len(angstrlist[0].split()) > 1:
        # Prep angstrlist for qa.toangle()
        if radec_col['comment'][:len("declination")].lower() == 'declination':
            for i in range(nrows):
                dms = angstrlist[i].replace(' ', 'd', 1)
                angstrlist[i] = dms.replace(' ', 'm') + 's'
        else:                                                  # R.A.
            for i in range(nrows):
                angstrlist[i] = angstrlist[i].replace(' ', ':')

        # Do first conversion to get unit.
        try:
            firstang = _qa.toangle(angstrlist[0])
        except Exception:
            print("Error: Could not convert %s to an angle." % angstrlist[0])
            raise
        angq['unit'] = firstang['unit']
        angq['value'] = [firstang['value']]

        for angstr in angstrlist[1:]:
            angq['value'].append(_qa.toangle(angstr)['value'])
    else:
        angq['unit'] = 'deg'                    # This is an assumption!
        angq['value'] = [float(a) for a in angstrlist]

    return {'comment': radec_col['comment'],
            'data': {'unit': angq['unit'],
                     'value': scipy.array(angq['value'])}}

def get_num_from_str(fstr, wanted="float"):
    """
    Like float(fstr) on steroids, in that it ignores things in fstr that aren't
    numbers.  Returns False on failure.

    wanted: an optional label for the type of number you wanted.
            Only used for distinguishing error messages.
            
    Example:
    >>> from JPLephem_reader import get_num_from_str
    >>> get_num_from_str('  Sidereal rot. period  =    58.6462 d  ')
    58.6462
    >>> get_num_from_str('Rotation period = 16.11+-0.01 hr', wanted='rotation period')
    16.109999999999999
    >>> get_num_from_str('Rotation period = Synchronous', wanted='rotation period')
    Could not convert "Rotation period = Synchronous" to a rotation period.
    False
    """
    match = re.search(r'([-+]?(\d+(\.\d*)?|\d*\.\d+)([eEdD][-+]?\d+)?)', fstr)
    if match:
        value = float(match.group(1))
    else:
        print("Could not convert \"%s\" to a %s." % (fstr, wanted))
        value = False
    return value

def mean_radius(a, b, c):
    """
    Return the average apparent mean radius of an ellipsoid with semiaxes
    a >= b >= c.
    "average" means average over time naively assuming the pole orientation
    is uniformly distributed over the whole sphere, and "apparent mean radius"
    means a radius that would give the same area as the apparent disk.
    """
    # This is an approximation, but it's not bad.
    # The exact equations for going from a, b, c, and the Euler angles to the
    # apparent ellipse are given in Drummond et al, Icarus, 1985a.
    # It's the integral over the spin phase that I have approximated, so the
    # approximation is exact for b == a, and appears to hold well for b << a.
    R = 0.5 * c**2 * (1.0 / b**2 + 1.0 / a**2)   # The magic ratio.
    if R < 0.95:
        sqrt1mR = scipy.sqrt(1.0 - R)
        # There is fake singularity (RlnR) at R = 0, but it is unlikely to
        # be a problem.
        try:
            Rterm = 0.5 * R * scipy.log((1.0 + sqrt1mR) / (1.0 - sqrt1mR)) / sqrt1mR
        except:
            Rterm = 0.0
    else:
        # Use a (rapidly converging) series expansion to avoid a fake
        # singularity at R = 1.
        Rterm = 1.0               # 0th order
        onemR = 1.0 - R
        onemRtothei = 1.0
        for i in range(1, 5):    # Start series at 1st order.
            onemRtothei *= onemR
            Rterm -= onemRtothei / (0.5 + 2.0 * i**2)
    avalfabeta = 0.5 * a * b * (1.0 + Rterm)
    return scipy.sqrt(avalfabeta)

def mean_radius_with_known_theta(retdict):
    """
    Return the average apparent mean radius of an ellipsoid with semiaxes
    a >= b >= c (= retdict['radii']['value']).
    "average" means average over a rotation period, and "apparent mean radius"
    means the radius of a circle with the same area as the apparent disk.
    """
    a = retdict['radii']['value'][0]
    b2 = retdict['radii']['value'][1]**2
    c2 = retdict['radii']['value'][2]**2
    onemboa2 = 1.0 - b2 / a**2
    units = {}
    values = {}
    for c in ['RA', 'DEC', 'NP_RA', 'NP_DEC']:
        units[c] = retdict['data'][c]['data']['unit']
        values[c] = retdict['data'][c]['data']['value']
    av = 0.0
    nrows = len(retdict['data']['RA']['data']['value'])
    for i in range(nrows):
        radec = _me.direction('app', {'unit': units['RA'], 'value': values['RA'][i]},
                             {'unit': units['DEC'], 'value': values['DEC'][i]})
        np = _me.direction('j2000', {'unit': units['NP_RA'], 'value': values['NP_RA'][i]},
                          {'unit': units['NP_DEC'], 'value': values['NP_DEC'][i]})
        szeta2 = scipy.sin(_qa.convert(_me.separation(radec, np), 'rad')['value'])**2
        csinz2 = c2 * szeta2
        bcosz2 = b2 * (1.0 - szeta2)
        bcz2pcsz2 = bcosz2 + csinz2
        m = csinz2 * onemboa2 / bcz2pcsz2
        av += (scipy.sqrt(bcz2pcsz2) * scipy.special.ellipe(m) - av) / (i + 1.0)
    return scipy.sqrt(2.0 * a * av / scipy.pi)

def datestr_to_epoch(datestr):
    """
    Given a UT date like "2010-May-01 00:00", returns an epoch measure.
    """
    return _me.epoch(rf='UTC', v0=_qa.totime(datestr))

def datestrs_to_MJDs(cdsdict):
    """
    All of the date strings must have the same reference frame (i.e. UT).
    """
    datestrlist = cdsdict['data']

    # Convert to FITS format, otherwise qa.totime() will silently drop the hours.
    datestrlist = [d.replace(' ', 'T') for d in datestrlist]
    
    timeq = {}
    # Do first conversion to get unit.
    firsttime = _qa.totime(datestrlist[0])
    timeq['unit'] = firsttime['unit']
    timeq['value'] = [firsttime['value']]
    
    for datestr in datestrlist[1:]:
        timeq['value'].append(_qa.totime(datestr)['value'])

    return {'unit': timeq['unit'],
            'value': scipy.array(timeq['value'])}

def construct_tablepath(fmdict, prefix=''):
    """
    Construct a suitable pathname for a CASA table made from fmdict,
    starting with prefix.  prefix can contain a /.

    If prefix is not given, it will be set to
    "ephem_JPL-Horizons_%s" % fmdict['NAME']
    """
    if not prefix:
        prefix = "ephem_JPL-Horizons_%s" % fmdict['NAME']
    return prefix + "_%.0f-%.0f%s%s.tab" % (fmdict['earliest']['m0']['value'],
                                            fmdict['latest']['m0']['value'],
                                            fmdict['latest']['m0']['unit'],
                                            fmdict['latest']['refer'])

def dict_to_table(indict, tablepath, kwkeys=[], colkeys=[], info=None, keepcolorder=False):
    """
    Converts a dictionary to a CASA table, and attempts to
    save it to tablepath.  Returns whether or not it was successful.

    kwkeys is a list of keys in dict that should be treated as table keywords,
    and colkeys is a list of keys to be treated as table columns.  If a key in
    indict is not in either kwkeys or colkeys, it will be appended to colkeys
    if it refers to a list, array, or specially formed dict with the right
    number of rows, or kwkeys otherwise.

    "Specially formed dict" means a python dictionary with the right keys to
    provide a comment and/or keywords to specify a (measure) frame or
    (quantity) unit for the column.

    The number of rows is set by the first column.  The order of the columns is
    the order of colkeys, followed by the remaining columns in alphabetical
    order.

    Example:
    mydict = {'delta': [1.2866, 1.2957, 1.3047],
              'obs_code': ['*', 'U', 't'],
              'date': {'m0': {'unit': 'd',
                              'value': [55317.0, 55318.0, 55319.0]},
                       'refer': 'UT1',
                       'type': 'epoch'},
              'phang': {'comment': 'phase angle',
                        'data': {'unit': 'deg',
                                 'value': array([37.30, 37.33, 37.36])}}}
                                 
    # Produces a table with, in order, a measure column (date), two bare
    # columns (delta and obs_code), and a commented quantity column (phang).
    # The comment goes in the 'comment' field of the column description.
    # Measure and straight array columns can also be described by using a
    # {'comment': (description), 'data': (measure, quantity, numpy.array or
    # list)} dict.
    dict_to_table(mydict, 'd_vs_phang.tab')

    TODO: detect non-float data types, including array cells.
    """
    nrows = 0
    dkeys = list(indict.keys())
    keywords = []
    cols = []

    def get_bare_col(col):
        """
        Given a col that could be a bare column (list or array), or measure or
        quantity containing a bare column, return the bare column.
        """
        barecol = col
        if isinstance(barecol,dict):
            if 'comment' in barecol:
                barecol = barecol.get('data')
            if type(barecol)==dict and _me.ismeasure(barecol):
                barecol = barecol['m0']
            # if qa.isquantity(data) can't be trusted.
            if isinstance(barecol,dict) and 'unit' in barecol and 'value' in barecol:
                barecol = barecol['value']
        return barecol
        
    # Divvy up the known keywords and columns, if present, preserving the
    # requested order.
    for kw in kwkeys:
        if kw in dkeys:
            # Take kw out of dkeys and put it in keywords.
            keywords.append(dkeys.pop(dkeys.index(kw)))
    for c in colkeys:
        if c in dkeys:
            cols.append(dkeys.pop(dkeys.index(c)))
            if nrows == 0:
                nrows = len(get_bare_col(indict[c]))
                print("Got nrows = %s from %s" % (nrows,c))

    # Go through what's left of dkeys and assign them to either keywords or
    # cols.
    dkeys.sort()
    for d in dkeys:
        used_as_col = False
        colcand = get_bare_col(indict[d])
        # Treat it as a column if it has the right number of rows.
        if type(colcand) in (list, numpy.ndarray):
            if nrows == 0:
                nrows = len(colcand)
            if len(colcand) == nrows:
                cols.append(d)
                used_as_col = True
        if not used_as_col:
            keywords.append(d)

    # Make the table's description.
    tabdesc = {}
    # Initialize the column descriptor with defaults (these come from
    # data/ephemerides/DE200, but I replaced IncrementalStMan with StandardStMan).
    coldesc = {'comment': '',
               'dataManagerGroup': '',
               'dataManagerType': 'StandardStMan',
               'maxlen': 0,
               'option': 0,
               'valueType': 'double'} # Use double (not float!) for columns
                                      # that will be read by MeasIERS.
    for c in cols:
        #print "Setting coldesc for", c
        data = indict[c]  # Place to find the valueType.

        if isinstance(data,dict):
            #print "comment =", data.get('comment', '')
            coldesc['comment'] = data.get('comment', '')
            
        data = get_bare_col(data)
        datatype = type(data[0])
        if datatype == float or datatype == numpy.float:
            valtype = "float"
        elif datatype == numpy.float64:
            valtype = "double"
        elif datatype == int or datatype == numpy.int32 or datatype == numpy.int16 or datatype == numpy.int:
            valtype = integer
        elif datatype == str:
            valtype = 'string'

        # Use double (not float!) for columns that will be read by MeasIERS.
        if valtype == 'float':
            valtype = 'double'
            
        coldesc['valueType'] = valtype

        tabdesc[c] = coldesc.copy()

    # Since tables are directories, it saves a lot of grief if we first check
    # whether the table exists and is under svn control.
    svndir = None
    if os.path.isdir(tablepath):
        if os.path.isdir(tablepath + '/.svn'):
            # tempfile is liable to use /tmp, which can be too small and/or slow.
            # Use the directory that tablepath is in, since we know the user
            # approves of writing to it.
            workingdir = os.path.abspath(os.path.dirname(tablepath.rstrip('/')))

            svndir = tempfile.mkdtemp(dir=workingdir)
            shutil.move(tablepath + '/.svn', svndir)
        print("Removing %s directory %s" % tablepath)
        shutil.rmtree(tablepath)

    # Create and fill the table.
    retval = True
    try:
        mytb = tbtool()
        tmpfname='_tmp_fake.dat'
        if keepcolorder:
            # try to keep order of cols 
            # Ugly, but since tb.create() cannot accept odered dictionary
            # for tabledesc, I cannot find any other way to keep column order.
            # * comment for each column will not be filled
            f = open(tmpfname,'w')
            zarr=numpy.zeros(len(cols))
            szarr=str(zarr.tolist())
            szarr=szarr.replace('[','')
            szarr=szarr.replace(']','')
            szarr=szarr.replace(',','')
            scollist=''
            sdtypes='' 
            for c in cols:
                scollist+=c+' '   
                vt=tabdesc[c]['valueType']
                if vt=='string':
                   sdtypes+='A '    
                elif vt=='integer':
                   sdtypes+='I '
                elif vt=='double':
                   sdtypes+='D '
                elif vt=='float':
                   sdtypes+='R '

            f.write(scollist+'\n')
            f.write(sdtypes+'\n')
            f.write(szarr)

            f.close()
            mytb.fromascii(tablepath,tmpfname,sep=' ')     
            # close and re-open since tb.fromascii(nomodify=False) has not
            # implemented yet
            mytb.close() 
            os.remove(tmpfname) 
            mytb.open(tablepath, nomodify=False)
            mytb.removerows(0)
        else: 
            mytb.create(tablepath, tabdesc)
        if type(info) == dict:
            mytb.putinfo(info)
        mytb.addrows(nrows)     # Must be done before putting the columns.

    except Exception as e:
        print("Error %s trying to create %s" % (e,tablepath))
        retval = False

    for c in cols:
        try:
            #print "tabdesc[%s] =" % c, tabdesc[c]
            data = indict[c]  # Note the trickle-down nature below.
            if isinstance(indict[c],dict) and 'comment' in indict[c]:
                data = data['data']
            if type(data)==dict and _me.ismeasure(data):
                mytb.putcolkeyword(c, 'MEASINFO', {'Ref': data['refer'],
                                                   'type': data['type']})
                data = data['m0']   # = quantity         
            # if qa.isquantity(data) can't be trusted.
            if isinstance(data,dict) and 'unit' in data and 'value' in data:
                mytb.putcolkeyword(c, 'QuantumUnits',
                                 numpy.array([data['unit']]))
                data = data['value']
            mytb.putcol(c, data)
        except Exception as e:
            print("Error %s trying to put column %s in %s" % (e,c,tablepath))
            print("data[0] = %s" % data[0])
            print("tabdesc[c] = %s" % tabdesc[c])
            retval = False

    for k in keywords:
        try:
            mytb.putkeyword(k, indict[k])
        except Exception as e:
            print("Error %s trying to put keyword %s in %s" % (e,k,tablepath))
            retval = False
    mytb.close()

    if svndir:
        shutil.move(svndir, tablepath + '/.svn')

    return retval

def ephem_dict_to_table(fmdict, tablepath='', prefix=''):
    """
    Converts a dictionary from readJPLephem() to a CASA table, and attempts to
    save it to either to tablepath or a constructed directory name.
    Returns whether or not it was successful.

    If tablepath is blank and prefix is not given, the table will go to
    something like ephem_JPL-Horizons_NAME_EARLIEST-LATESTdUTC.tab.

    If tablepath is blank and prefix is given, the table will go to
    something like prefix_EARLIEST-LATESTdUTC.tab.  prefix can contain a /.
    """
    if not tablepath:
        tablepath = construct_tablepath(fmdict, prefix)
        print("Writing to %s" % tablepath)

    # safe gaurd from zapping current directory by dict_to_table()
    if tablepath=='.' or tablepath=='./' or tablepath.isspace():
        raise Exception("Invalid tablepath: %s" % tablepath)
    retval = True
    # keepcolorder=T preserves column ordering in collist below
    #keepcolorder=False
    keepcolorder=True
    try:
        outdict = fmdict.copy() # Yes, I want a shallow copy.
        #kws = fmdict.keys()
        # reorder the keywords
        okws=['VS_CREATE','VS_DATE','VS_TYPE', 'VS_VERSION', 'NAME', 'MJD0', 'dMJD', 
              'GeoDist', 'GeoLat', 'GeoLong', 'obsloc', 'posrefsys','earliest','latest',
              'radii','meanrad','orb_per','data']
        oldkws = list(fmdict.keys())
        kws=[]
        for ik in okws:
            if oldkws.count(ik):
              kws.append(ik)
              oldkws.remove(ik)
        kws+=oldkws 
        kws.remove('data')
        collist = list(outdict['data'].keys())

        # For cosmetic reasons, encourage a certain order to the columns, i.e.
        # start with alphabetical order,
        collist.sort()
        # but put these ones first, in the listed order (ignore the reverse and
        # the pops) if they are present.
        #put_these_first = ['MJD', 'RA', 'DEC', 'Rho', 'RadVel', 'NP_RA', 'NP_DEC',
        #                   'DiskLong', 'DiskLat', 'sl_lon', 'sl_lat', 'r',
        #                   'ang_sep', 'obs_code']
        put_these_first = ['MJD', 'RA', 'DEC', 'Rho', 'RadVel', 'NP_ang', 'NP_dist',
        #                   'Obs_Long', 'Obs_Lat', 'Sl_lon', 'Sl_lat', 'r','rdot']
                           'DiskLong', 'DiskLat', 'Sl_lon', 'Sl_lat', 'r','rdot']
        # Like l.sort(), reverse() acts on its instance instead of returning a value.
        put_these_first.reverse()
        for c in put_these_first:
            if c in collist:
                collist.remove(c)
                collist.insert(0, c)
        
        clashing_cols = [c for c in collist if c in kws]
        if clashing_cols:
            raise ValueError('The input dictionary lists %s as both keyword(s) and column(s)' % ', '.join(clashing_cols))

        # This promotes the keys in outdict['data'] up one level, and removes
        # 'data' as a key of outdict.
        outdict.update(outdict.pop('data'))

        # This is primarily because MeasComet insists on it, not because it
        # ever gets used.  Maybe subType should be changed to 'Asteroid',
        # 'Moon', or 'Planet', but I'm leaving it at 'Comet' for now.
        info = {'readme': 'Derived by JPLephem_reader.py from a JPL-Horizons ephemeris (http://ssd.jpl.nasa.gov/horizons.cgi#top)',
                'subType': 'Comet', 'type': 'IERS'}

        retval = dict_to_table(outdict, tablepath, kws, collist, info, keepcolorder)
    except Exception as e:
        print('Error %s trying to export an ephemeris dict to %s' % (e,tablepath))
        retval = False

    return retval


def jplfiles_to_repository(objs, jpldir='.', jplext='.ephem',
                           log='null'):
    """
    For each Solar System object obj in the list objs,
        look for matching JPL-Horizons ASCII files with jplext in jpldir,
        read them into python dictionaries,
        write the dicts to CASA tables in $CASAROOT/data/ephemerides/JPL-Horizons/,
        and check that they can be read by me.framecomet().
    Returns the number of ephemerides processed + readable by me.framecomet.

    jpldir and jplext can be glob patterns.

    $CASAROOT is derived from $CASAPATH.

    Log messages will be directed to log for the duration of this function.
    Note that 'null' makes a NullLogSink, so it might be better than /dev/null.

    Example:
    import recipes.ephemerides.request as jplreq
    objs = jplreq.asteroids.keys() + jplreq.planets_and_moons.keys()
    jplfiles_to_repository(objs, os.getenv('CASAPATH').split()[0])
    """
    neph = 0
    casapath = os.getenv('CASAPATH')
    if not casapath:
        print("CASAPATH is not set.")
        return 0
    datadir = casapath.split()[0] + '/data/ephemerides/JPL-Horizons'
    if not os.path.isdir(datadir):
        try:
            os.mkdir(datadir)
            print("Created %s" % datadir)
            print("You should probably svn add it.")
        except Exception as e:
            print("Error %s creating %s" % (e,datadir))
            return 0
    datadir += '/'

    #oldlog = casalog.logfile()
    # This is needed to stop WARN and above from printing to the console,
    # but it permanently severs the logger window.
    #casalog.setglobal(True)
    #casalog.setlogfile(log)

    if jpldir[-1] != '/':
        jpldir += '/'
    for sob in objs:
        capob = sob.capitalize()
        lob = sob.lower()
        jplfiles = glob(jpldir + lob + jplext) + glob(jpldir + capob + jplext)
        for jplfile in jplfiles:
            casalog.post('Reading ' + jplfile)
            fmdict = readJPLephem(jplfile)
            tabpath = construct_tablepath(fmdict, datadir + capob)
            ephem_dict_to_table(fmdict, tabpath)

            # Check if it is readable by me.framecomet.
            epoch = fmdict['earliest']
            epoch['m0']['value'] += 0.5 * (fmdict['latest']['m0']['value'] -
                                           epoch['m0']['value'])
            _me.doframe(epoch)
            if _me.framecomet(tabpath):
                neph += 1
            else:
                casalog.post(tabpath + " was not readable by me.framecomet.",
                             'WARN')

    #casalog.setlogfile(oldlog)

    return neph
