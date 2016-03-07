#!/bin/sh 
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -z "$CMSSW_BASE" ]; then
  cmsenv
fi
/bin/bash --init-file $CMSSW_BASE/src/Kappa/Skimming/zjet/crab3/basics/ini_bash.sh
