#!/bin/bash
# Copy over the time-dependent measures tables from ASTRON
# D.Petry, ESO, Jun 2015, Jan, Feb, Jun 2016, Apr 2018, Feb 2020

export MYVERSION="v1.3"

export MAILADDRESSEES="-c vsuorant@nrao.edu dpetry@eso.org"
#export MAILADDRESSEES="dpetry@eso.org"

export DRYRUN="FALSE"
#export DRYRUN="TRUE"

export REFREPO="ftp://ftp.astron.nl/outgoing/Measures/"
export REFTARBALL="WSRT_Measures.ztar"

export DATAREPO="/diska/home/dpetry/temp/casa/svn-data"
#export DATAREPO="/diska/home/dpetry/temp/test-data/data"

export TMPDIR="/tmp/fromASTRON"
export THEEXEC="/diska/home/dpetry/update_meastabs/update_meastabs.sh"
export THEEXECTIME="19:15"
export LOGFILE="/diska/home/dpetry/update_meastabs/update_meastabs.log"
export LOGFILEOLD="/diska/home/dpetry/update_meastabs/update_meastabs.log.previous"
export TMEASURE="/diska/home/dpetry/temp/casa/buildcasacore/measures/Measures/test/tMeasure"
export TMEASUREROOT="/diska/home/dpetry/temp/casa"


export GEODETIC_TABLES="IERSeop2000  IERSpredict IGRF  KpApF107 IERSeop97 IMF TAI_UTC SCHED_locations"

export EPHEMERIDES_TABLES="DE200  DE405  Lines  Sources  VGEO  VTOP"

export MODMESSAGE=""

rm -rf $TMPDIR
rm -rf $LOGFILEOLD
if [ -e $LOGFILE ]; then
    mv $LOGFILE $LOGFILEOLD
fi

echo "update_meastabs.sh "${MYVERSION}" Log" > $LOGFILE
date | tee -a $LOGFILE

echo "Next execution after this one:" >> $LOGFILE 2>&1
at -f $THEEXEC $THEEXECTIME >> $LOGFILE 2>&1

echo "Creating $TMPDIR ..."  | tee -a $LOGFILE
 
mkdir $TMPDIR >> $LOGFILE 2>&1
if [ ! $? == 0 ]; then
    echo "ERROR creating $TMPDIR" 
    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 1
fi

cd $TMPDIR >> $LOGFILE 2>&1

echo "Downloading $REFREPO ..."  | tee -a $LOGFILE

wget -q ${REFREPO}/$REFTARBALL >> $LOGFILE 2>&1
if [ ! $? == 0 ]; then
    echo "ERROR downloading $REFREPO"
    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 1
fi

if [ ! -e $REFTARBALL ]; then
    echo "ERROR: $REFTARBALL was not downloaded"
    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 1
fi

echo "Unpacking $REFTARBALL ..."  | tee -a $LOGFILE

tar xf $REFTARBALL >> $LOGFILE 2>&1
if [ ! -d geodetic ]; then
    echo "ERROR:  $REFTARBALL did not contain \"geodetic\"" | tee -a $LOGFILE
    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 2
fi
if [ ! -d ephemerides ]; then
    echo "ERROR:  $REFTARBALL did not contain \"ephemerides\""  | tee -a $LOGFILE
    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 2
fi

echo "Updating $DATAREPO to presently latest version ..."  | tee -a $LOGFILE

cd ${DATAREPO}/geodetic
if [ $? == 0 ]; then
    rm -rf *
    svn update 2>> $LOGFILE
    if [ ! $? == 0 ]; then
	echo "ERROR: could not run svn update in geodetic."  | tee -a $LOGFILE
	mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
	exit 3
    fi
    cd ../ephemerides
    rm -rf *
    svn update 2>> $LOGFILE
    if [ ! $? == 0 ]; then
	echo "ERROR: could not run svn update in ephemerides."  | tee -a $LOGFILE
	mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
	exit 3
    fi
else
    echo "ERROR: ${DATAREPO}/geodetic does not exist"  | tee -a $LOGFILE
    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 2
fi

echo "Copying new version into $DATAREPO ..."  | tee -a $LOGFILE

export ERRORTYPE4=FALSE

cd $TMPDIR
cd geodetic >> $LOGFILE 2>&1
rm -f IERSeop97/table.lock.org # make up for bug on the ASTRON side
for NAME in $GEODETIC_TABLES; do
    if [ -d $NAME ]; then
	for NAMEB in `ls $NAME/*`; do
	    if [ -e ${DATAREPO}/geodetic/$NAMEB ]; then
		echo "copying over ${DATAREPO}/geodetic/$NAMEB : cp $NAMEB ${DATAREPO}/geodetic/$NAMEB"
		rm -f ${DATAREPO}/geodetic/$NAMEB
		cp $NAMEB ${DATAREPO}/geodetic/$NAMEB
	    else
		echo "ERROR: repository does not contain geodetic/$NAMEB but reference does"  | tee -a $LOGFILE	    
		export ERRORTYPE4=TRUE
	    fi
	done
    else
	echo "ERROR: $REFTARBALL does not contain geodetic/$NAME"  | tee -a $LOGFILE
	export ERRORTYPE4=TRUE
    fi
done

cd ../ephemerides
for NAME in $EPHEMERIDES_TABLES; do
    if [ -d $NAME ]; then
	for NAMEB in `ls $NAME/*`; do
	    if [ -e ${DATAREPO}/ephemerides/$NAMEB ]; then
		echo "copying over ${DATAREPO}/ephemerides/$NAMEB : cp $NAMEB ${DATAREPO}/ephemerides/$NAMEB"
		rm -f ${DATAREPO}/ephemerides/$NAMEB
		cp $NAMEB ${DATAREPO}/ephemerides/$NAMEB
	    else
		echo "ERROR: repository does not contain ephemerides/$NAMEB but reference does"  | tee -a $LOGFILE	    
		export ERRORTYPE4=TRUE
	    fi	    
	done
    else
	echo "ERROR: $REFTARBALL did not contain ephemerides/$NAME" | tee -a $LOGFILE
	export ERRORTYPE4=TRUE
    fi
done

cd ..

if [ $ERRORTYPE4 == "TRUE" ]; then
    mail -s "PROBLEM TYPE 4 IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 4
fi

echo "Testing whether tMeasure still passes ..."  | tee -a $LOGFILE

if [ -e $TMEASURE ]; then
    if [ -L $TMEASUREROOT/data ]; then
	rm -f $TMEASUREROOT/data 
	ln -sf $DATAREPO $TMEASUREROOT/data
    fi    
    source $TMEASUREROOT/casainit.sh
    echo "Running tMeasure ... "  | tee -a $LOGFILE
    $TMEASURE  >> $LOGFILE
    if [ ! $? == 0 ]; then
	echo "ERROR: tMeasure did not pass. Will not commit update."  | tee -a $LOGFILE
	mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
	exit 3
    fi
    echo "Updating repository ..."  | tee -a $LOGFILE
    echo "Automatic update by copy from "${REFREPO}/$REFTARBALL > message.txt
    date >> message.txt
    cd ${DATAREPO}/geodetic  >> $LOGFILE 2>&1
    svn -v status  > $TMPDIR/status-geodetic.txt
    grep "M   " $TMPDIR/status-geodetic.txt  >> $LOGFILE
    grep "M   " $TMPDIR/status-geodetic.txt 
    if [ $? == 0 ]; then
	export MODMESSAGE=${MODMESSAGE}" geodetic"
    fi
    if [ $DRYRUN == "TRUE" ]; then
	echo "Dry run. Not committing."  | tee -a $LOGFILE
	svn -v status  >> $LOGFILE
    else
	echo "Committing geodetic ..."  | tee -a $LOGFILE
	svn commit --non-interactive -F $TMPDIR/message.txt >> $LOGFILE
	if [ ! $? == 0 ]; then
	    echo "ERROR: could not commit change to geodetic."  | tee -a $LOGFILE
	    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
	    exit 3
	fi
    fi
    cd ../ephemerides
    svn -v status  > $TMPDIR/status-ephemerides.txt
    grep "M   " $TMPDIR/status-ephemerides.txt >> $LOGFILE
    grep "M   " $TMPDIR/status-ephemerides.txt
    if [ $? == 0 ]; then
	export MODMESSAGE=${MODMESSAGE}" ephemerides"
    fi
    if [ $DRYRUN == "TRUE" ]; then
	echo "Dry run. Not committing."  | tee -a $LOGFILE
    else
	echo "Committing ephemerides ..."  | tee -a $LOGFILE
	svn commit --non-interactive -F $TMPDIR/message.txt >> $LOGFILE
	if [ ! $? == 0 ]; then
	    echo "ERROR: could not commit change to ephemerides."  | tee -a $LOGFILE
	    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
	    exit 3
	fi
    fi
    cd $TMPDIR  >> $LOGFILE 2>&1
else
    echo "ERROR: $TMEASURE not available. Will not commit update."  | tee -a $LOGFILE
    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 3
fi

echo "Done." | tee -a $LOGFILE
if [ ! "a$MODMESSAGE" == "a" ]; then
    MODMESSAGE=", modifications applied in: "$MODMESSAGE
fi
mail -s "CASA Measuresdata update completed$MODMESSAGE" $MAILADDRESSEES < $LOGFILE
