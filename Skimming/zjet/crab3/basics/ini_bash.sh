#!/bin/bash 

source /cvmfs/cms.cern.ch/crab3/crab.sh

export PYTHONPATH=$PYTHONPATH:$CMSSW_BASE/src/Kappa/Skimming/zjet/crab3/basics
thatsme=`whoami`
firstc=$(echo $thatsme | head -c 1)
export X509_USER_PROXY=/nfs/dust/cms/user/${thatsme}/.grid_proxy/k5-ca-proxy.pem
echo "voms-proxy-init --voms cms:/cms/dcms --valid 192:00 --out /nfs/dust/cms/user/${thatsme}/.grid_proxy/k5-ca-proxy.pem"
echo "the --out option is needed since the default /tmp/directory is not mounted (or have differnt mount) on batch system"
