#!/bin/bash
# Copy over the time-dependent measures tables from ASTRON using the CASA git repository
# D.Petry, ESO, Jun 2015, Jan, Feb, Jun 2016, Mar 2017, Apr 2018, Feb 2020

export MYVERSION="v1.4"

export MAILADDRESSEES="-c vsuorant@nrao.edu dpetry@eso.org"
#export MAILADDRESSEES="dpetry@eso.org"

export DRYRUN="FALSE"
#export DRYRUN="TRUE"

export REFREPO="ftp://ftp.astron.nl/outgoing/Measures/"
export REFTARBALL="WSRT_Measures.ztar"

#export DATAREPO="/diska/home/dpetry/temp/casa/data"
export DATAREPO="/diska/home/dpetry/update_meastabs/data"

export TMPDIR="/tmp/fromASTRON"
export THEEXEC="/diska/home/dpetry/update_meastabs/git-update_meastabs.sh"
export THEEXECTIME="19:00"
export LOGFILE="/diska/home/dpetry/update_meastabs/git-update_meastabs.log"
export LOGFILEOLD="/diska/home/dpetry/update_meastabs/git-update_meastabs.log.previous"
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

echo "git-update_meastabs.sh "${MYVERSION}" Log" > $LOGFILE
date | tee -a $LOGFILE

if [ ! $DRYRUN == "TRUE" ]; then
    echo "Next execution after this one:" >> $LOGFILE 2>&1
    at -f $THEEXEC $THEEXECTIME >> $LOGFILE 2>&1
fi

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

cd ${DATAREPO}
if [ $? == 0 ]; then
    git pull 2>> $LOGFILE
    if [ ! $? == 0 ]; then
	echo "ERROR: could not successfully run git pull."  | tee -a $LOGFILE
	mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
	exit 3
    fi
else
    echo "ERROR: ${DATAREPO} does not exist"  | tee -a $LOGFILE
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
		MYDIR=$PWD
		cd ${DATAREPO}
		git add geodetic/$NAMEB
		cd $MYDIR
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
		MYDIR=$PWD
		cd ${DATAREPO}
		git add ephemerides/$NAMEB
		cd $MYDIR
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
    cd ${DATAREPO}
    git reset 
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
	cd ${DATAREPO}
	git reset 
	mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
	exit 3
    fi
    echo "Updating repository ..."  | tee -a $LOGFILE
    echo "Automatic update by copy from "${REFREPO}/$REFTARBALL > message.txt
    date >> message.txt
    cd ${DATAREPO}  >> $LOGFILE 2>&1
    
    git commit --dry-run > $TMPDIR/status-geoephem.txt 2>&1
    grep "modified" $TMPDIR/status-geoephem.txt  >> $LOGFILE
    grep "modified" $TMPDIR/status-geoephem.txt
    if [ $? == 0 ]; then
	grep "geodetic" $TMPDIR/status-geoephem.txt > /dev/null
	if [ $? == 0 ]; then
    	    export MODMESSAGE=${MODMESSAGE}" geodetic"
	fi
	grep "ephemerides" $TMPDIR/status-geoephem.txt > /dev/null
	if [ $? == 0 ]; then
    	    export MODMESSAGE=${MODMESSAGE}" ephemerides"
	fi
    fi

    if [ ! "a$MODMESSAGE" == "a" ]; then

	if [ $DRYRUN == "TRUE" ]; then
	    echo "Dry run. Not committing."  | tee -a $LOGFILE
	    git commit --dry-run -F $TMPDIR/message.txt >> $LOGFILE
	    if [ ! $? == 0 ]; then
		cd ${DATAREPO}
		git reset 
		echo "ERROR: could not dry-run commit."  | tee -a $LOGFILE
		mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
		exit 3
	    fi
	else
	    echo "Committing geodetic and ephemerides ..."  | tee -a $LOGFILE
	    git commit -F $TMPDIR/message.txt >> $LOGFILE
	    if [ ! $? == 0 ]; then
		cd ${DATAREPO}
		git reset 
		echo "ERROR: could not commit changes to geodetic and ephemerides."  | tee -a $LOGFILE
		mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
		exit 3
	    fi
            git push >> $LOGFILE
	    if [ ! $? == 0 ]; then
		cd ${DATAREPO}
		git reset 
		echo "ERROR: could not commit changes to geodetic and ephemerides - git push failed."  | tee -a $LOGFILE
		mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
		exit 3
	    fi
	fi
    else
	cd ${DATAREPO}
	git reset 
	echo "No changes necessary. Nothing to commit or push." >> $LOGFILE
    fi

    cd $TMPDIR  >> $LOGFILE 2>&1
else
    cd ${DATAREPO}
    git reset 
    echo "ERROR: $TMEASURE not available. Will not commit update."  | tee -a $LOGFILE
    mail -s "PROBLEM IN CASA Measuresdata update " $MAILADDRESSEES < $LOGFILE
    exit 3
fi

echo "Done." | tee -a $LOGFILE
if [ ! "a$MODMESSAGE" == "a" ]; then
    MODMESSAGE=", modifications applied in: "$MODMESSAGE
fi
echo "Find git-update-meastabs log in attached file." > temp.txt
mail -s "CASA Measuresdata update completed$MODMESSAGE" -a $LOGFILE $MAILADDRESSEES < temp.txt
