#!/bin/bash
#set -e # exit on errors

ssh -vT git@github.com

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW CMSSW_9_4_2
cd CMSSW_9_4_2/src
eval `scramv1 runtime -sh`

export KAPPA_BRANCH="master"
while getopts :b:g:e:n: option
do
	case "${option}"
	in
	b) export KAPPA_BRANCH=${OPTARG};;
	g) git config --global user.github ${OPTARG};;
	e) git config --global user.email ${OPTARG};;
	n) git config --global user.name "\"${OPTARG}\"";;
	esac
done

##Electron cutBased Id and MVA Id
##https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_8_0
##https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_regular_users_common
git cms-merge-topic lsoffi:CMSSW_9_4_0_pre3_TnP
git cms-merge-topic guitargeek:ElectronID_MVA2017_940pre3
scram b -j `grep -c ^processor /proc/cpuinfo`
#
# Add the area containing the MVA weights (from cms-data, to appear externa).
# Note: the external area appears after scram build is run at least once, as above
#
# Photons - Uncomment if needed
cd $CMSSW_BASE/external
# below, you may have a different architecture, this is just one example from lxplus
cd slc6_amd64_gcc630/
git clone https://github.com/lsoffi/RecoEgamma-PhotonIdentification.git data/RecoEgamma/PhotonIdentification/data
cd data/RecoEgamma/PhotonIdentification/data
git checkout CMSSW_9_4_0_pre3_TnP
#
# Electrons
cd $CMSSW_BASE/external
cd slc6_amd64_gcc630/
git clone https://github.com/lsoffi/RecoEgamma-ElectronIdentification.git data/RecoEgamma/ElectronIdentification/data
cd data/RecoEgamma/ElectronIdentification/data
git checkout CMSSW_9_4_0_pre3_TnP
cd $CMSSW_BASE/src
#
##Remove the .git folder as it is not needed and contains a lot of useless data
#rm -rf RecoEgamma/ElectronIdentification/data/.git
rm -rf $CMSSW_BASE/external/slc6_amd64_gcc630/data/RecoEgamma/ElectronIdentification/data/.git

# git cms-addpkg DataFormats/PatCandidates
# git cms-addpkg RecoTauTag/Configuration
# git cms-addpkg RecoTauTag/RecoTau
#
# mkdir $CMSSW_BASE/tmp_external
# #fetch xml files for Egamma Id from private repository
# cd $CMSSW_BASE/tmp_external
# git clone https://github.com/lsoffi/RecoEgamma-ElectronIdentification.git data/RecoEgamma/ElectronIdentification/data
# cd data/RecoEgamma/ElectronIdentification/data
# git checkout CMSSW_9_4_0_pre3_TnP
# cp -r Fall17 $CMSSW_BASE/src/RecoEgamma/ElectronIdentification/data
# # Go back to the src/
# cd $CMSSW_BASE/src
# rm -rf tmp_external

# MET filters :
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2#Analysis_Recommendations_for_ana
# No new recipe?

# Luminosity :
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM

# JETS to use:
# https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC#Jet_Energy_Corrections_in_Run2
# Cross-check

# Muons to use:
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonPOG#Basic_documentation_description
# No new recipe?

# general reference:
# https://twiki.cern.ch/twiki/bin/view/CMS/WebHome

# CP: Refitting package
git clone git@github.com:artus-analysis/TauRefit.git VertexRefit/TauRefit

#Check out Kappa
git clone git@github.com:KappaAnalysis/Kappa.git -b ${KAPPA_BRANCH}

# B-tag:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
# NEEDS UPDATE

# TAU: Packages needed to rerun tau id
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Rerunning_of_the_tau_ID_on_M_AN1
# NEEDS UPDATE
wget https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py  -P $CMSSW_BASE/src/Kappa/Skimming/python/

scram b -j `grep -c ^processor /proc/cpuinfo`
