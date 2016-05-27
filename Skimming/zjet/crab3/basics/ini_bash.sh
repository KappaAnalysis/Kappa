#!/bin/sh 



if [ -z "$CMSSW_BASE" ]; then
    source /cvmfs/cms.cern.ch/cmsset_default.sh
fi

cmsenv



source /cvmfs/cms.cern.ch/crab3/crab.sh
export PYTHONPATH=$PYTHONPATH:$CMSSW_BASE/src/Kappa/Skimming/zjet/crab3/basics


if [[ $USER == *"wayand" ]]; then
    if [[ $HOSTNAME == *"naf"* ]]; then
	export X509_USER_PROXY=/nfs/dust/cms/user/${USER}/.grid_proxy/k5-ca-proxy.pem
    else
	export X509_USER_PROXY=/portal/ekpcms5/home/${USER}/.grid_proxy/k5-ca-proxy.pem
    fi
fi

echo "voms-proxy-init --voms cms:/cms/dcms --valid 192:00 --out ${X509_USER_PROXY}"
echo "the --out option is mandatory since the default /tmp/directory is not mounted (or have differnt mount) on batch system"
