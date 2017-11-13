#!/bin/bash
if [ "$ADDITIONAL_OUTPUT" = true ]; then
    set -x
fi

if ! which wget; then 
    yum install wget -y
    if ! which wget; then 
        echo "Could not get wget"
        exit 1
    fi
fi

echo "# ================= #"
echo "# Setting /etc/cvmfs/config.d/cms.cern.ch.local BEFORE the mount"
echo "# ================= #"
    cat /etc/cvmfs/config.d/cms.cern.ch.local  &>/dev/null || {
    echo "No /etc/cvmfs/config.d/cms.cern.ch.local was found"
    cat >/etc/cvmfs/config.d/cms.cern.ch.local <<EOL
    # Important setting for CMS, jobs will not work properly without!
    # export CMS_LOCAL_SITE=T2_DE_DESY
    export CMS_LOCAL_SITE=/cvmfs/cms.cern.ch/SITECONF/T2_DE_DESY
    # This only needed if you did not configure Squids in /etc/default.[conf|local]
    #CVMFS_HTTP_PROXY="http://<Squid1-url>:<port>|http://<Squid2-url>:<port>[|...]"" > /etc/cvmfs/config.d/cms.cern.ch.local
EOL
    source /etc/cvmfs/config.d/cms.cern.ch.local
    }
echo 


if [ "$ADDITIONAL_OUTPUT" = true ]; then
    echo "# ================= #"
    echo "# Environment checks "
    echo "# ================= #"

        cat /etc/cvmfs/default.local
        echo

        cat /etc/cvmfs/domain.d/cern.ch.local
        echo 

        echo $CMS_LOCAL_SITE
        echo

        cat /etc/cvmfs/run-cvmfs.sh
        echo
    echo
fi


echo "# ================= #"
echo "# Mounting: run-cvmfs.sh"
echo "# ================= #"
/etc/cvmfs/run-cvmfs.sh
echo

if [ "$ADDITIONAL_OUTPUT" = true ]; then
    echo "# ================= #"
    echo "# Find site-local-config.xml"
    echo "# ================= #"
        thesite=local

        ls -ltr /cvmfs/cms.cern.ch/SITECONF
        echo

        ls -ltr /cvmfs/cms.cern.ch/SITECONF/$thesite
        echo

        sitelocaltocheck=/cvmfs/cms.cern.ch/SITECONF/$thesite/JobConfig/site-local-config.xml
    echo
fi


export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

echo "# ================= #"
echo "# check root files"
echo "# ================= #"
    files=(/home/short/*)
    if [ ! ${#files[@]} -gt 0 ]
    then
        curl -o /home/short_rootfiles.tar https://cernbox.cern.ch/index.php/s/WeawecKp2BD2BH2/download
        tar -xvf /home/short_rootfiles.tar -C /home/
        echo
    else
        echo "Files in /home/short are presented"
    fi
echo


echo "# ================= #"
echo "# Download checkout script for Kappa"
echo "# ================= #"
    mkdir -p /home/build && cd /home/build
    curl -O https://raw.githubusercontent.com/KappaAnalysis/Kappa/${KAPPA_BRANCH}/Skimming/scripts/${CHECKOUTSCRIPT}
    chmod +x ${CHECKOUTSCRIPT}
    printf "no\n" | . ./${CHECKOUTSCRIPT} -b ${KAPPA_BRANCH} -g 'greyxray' -e 'greyxray@gmail.com' -n 'kappa test' || {
        echo "The ${CHECKOUTSCRIPT} could not be executed"
        exit 1
    }
echo

echo "# ================= #"
echo "# Set CMSSW variables"
echo "# ================= #"
    source $VO_CMS_SW_DIR/cmsset_default.sh;
    cd $TEST_CMSSW_VERSION/src
    eval `scramv1 runtime -sh`
    cd $CMSSW_BASE/src
echo

if [ "$ADDITIONAL_OUTPUT" = true ]; then
    echo "# =================== #"
    echo "# Env var checks #"
    echo "# =================== #"
    uname -a
    echo "HOSTNAME=$HOSTNAME"
    echo "SHELL=$SHELL"
    python --version

    echo "python:" $(which python)
    echo "PYTHONSTARTUP=$PYTHONSTARTUP"
    echo "PYTHONPATH=$PYTHONPATH"
    echo "SCRAM_ARCH=$SCRAM_ARCH"
    echo "VO_CMS_SW_DIR=$VO_CMS_SW_DIR"
    echo "CMSSW_VERSION=$CMSSW_VERSION"
    echo "CMSSW_GIT_HASH=$CMSSW_GIT_HASH"
    echo "CMSSW_BASE=$CMSSW_BASE"
    echo "CMSSW_RELEASE_BASE=$CMSSW_RELEASE_BASE"
    echo
fi

echo "# =================== #"
echo "# Check the skimming config #"
echo "# =================== #"
    cat $CMSSW_BASE/src/$SKIMMING_SCRIPT &>/dev/null || {
        echo "The ${CMSSW_BASE}/src/${SKIMMING_SCRIPT} could not be read"
        exit 1
    }
echo

echo "# =================== #"
echo "# Test python #"
echo "# =================== #"
cd $CMSSW_BASE/src/Kappa && mkdir kappa_run && cd kappa_run
python $CMSSW_BASE/src/$SKIMMING_SCRIPT || {
    echo "Possible python syntax error "
}
echo

echo "# =================== #"
echo "# Test cmsRun #"
echo "# =================== #"
    cmsRun $CMSSW_BASE/src/$SKIMMING_SCRIPT || {
        echo "The cmsRun could not be run"
        exit 1
    }
echo

echo "# =================== #"
echo "# Test Output root file #"
echo "# =================== #"
    ls -l *.root || {
        echo "The root file was not created"
        exit 1
    }
echo

echo "The end"
