#!/bin/sh
#
# Checkout script for Kappa (skimming)
######################################
#
# analysis:       JEC
# description:    derivation of L3Residual corrections with Z+Jets data
# CMSSW version:  CMSSW_8_0_26_patch1
# created:        2017-07-22


_CMSSW_VERSION="CMSSW_8_0_26_patch1"

# checkout workflow
# =================

# -- checks

# check for CMSSW
if [ -z "${CMS_PATH}" ]; then
    echo "[ERROR] Cannot find CMSSW: environment variable \$CMS_PATH is not set!"
    echo "[INFO] Have you done `source /cvmfs/cms.cern.ch/cmsset_default.sh`?"
fi



# -- initialization

# create a CMSSW working directory
echo "[INFO] Can create working area '${_CMSSW_VERSION}'?"
if [ -d "${_CMSSW_VERSION}" ]; then
    echo "[ERROR] Cannot create working area '${_CMSSW_VERSION}': directory already exists!"
fi
scramv1 project CMSSW "${_CMSSW_VERSION}"

cd "${_CMSSW_VERSION}/src"
eval `scramv1 runtime -sh`

# initialize git repository from CMSSW
git cms-init

# checkout several CMSSW modules explicitly
git cms-addpkg PhysicsTools/PatUtils



# -- apply CMSSW modifications, backports, etc. (user code)

# Tau POG backport of tauID to CMSSW_8_0_26_patch1
git cms-merge-topic -u cms-tau-pog:CMSSW_8_0_X_tau-pog_miniAOD-backport-tauID

# find-and-replace-fixes in code
sed "/import\ switchJetCollection/a from\ RecoMET\.METProducers\.METSignificanceParams_cfi\ import\ METSignificanceParams_Data" PhysicsTools/PatUtils/python/tools/runMETCorrectionsAndUncertainties.py -i



# -- get some modules directly from github

# Kappa
git clone https://github.com/KappaAnalysis/Kappa.git

# TauRefit (needed by Kappa)
git clone https://github.com/artus-analysis/TauRefit.git VertexRefit/TauRefit

# Jet Toolbox
git clone https://github.com/cms-jet/JetToolbox.git JMEAnalysis/JetToolbox --branch jetToolbox_80X


# -- compile using scram
scramv1 b -j10
