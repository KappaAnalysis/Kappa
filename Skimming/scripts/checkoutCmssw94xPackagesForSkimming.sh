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

cd $CMSSW_BASE/src
##Electron cutBased Id and MVA Id
##https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_8_0
##https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_regular_users_common
#git cms-addpkg RecoMET/METPUSubtraction
#git cms-addpkg DataFormats/METReco
#git cms-addpkg PhysicsTools/PatUtils
#git cms-addpkg PhysicsTools/PatAlgos

git cms-addpkg DataFormats/PatCandidates
git cms-addpkg RecoTauTag/Configuration
git cms-addpkg RecoTauTag/RecoTau

git cms-merge-topic lsoffi:CMSSW_9_4_0_pre3_TnP

mkdir $CMSSW_BASE/tmp_external
#cd $CMSSW_BASE/tmp_external
#git clone https://github.com/lsoffi/RecoEgamma-PhotonIdentification.git data/RecoEgamma/PhotonIdentification/data
#cd data/RecoEgamma/PhotonIdentification/data
#git checkout CMSSW_9_4_0_pre3_TnP

#fetch xml files for Egamma Id from private repository
cd $CMSSW_BASE/tmp_external
git clone https://github.com/lsoffi/RecoEgamma-ElectronIdentification.git data/RecoEgamma/ElectronIdentification/data
cd data/RecoEgamma/ElectronIdentification/data
git checkout CMSSW_9_4_0_pre3_TnP
cp -r Fall17 $CMSSW_BASE/src/RecoEgamma/ElectronIdentification/data
# Go back to the src/
cd $CMSSW_BASE/src
rm -rf tmp_external

#Check out Refitting package
git clone git@github.com:artus-analysis/TauRefit.git VertexRefit/TauRefit
#
##Remove the .git folder as it is not needed and contains a lot of useless data
#rm -rf RecoEgamma/ElectronIdentification/data/.git

#Check out Kappa
git clone git@github.com:KappaAnalysis/Kappa.git -b ${KAPPA_BRANCH}

wget https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py  -P $CMSSW_BASE/src/Kappa/Skimming/python/

scram b -j `grep -c ^processor /proc/cpuinfo`
