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
#git cms-addpkg RecoEgamma/ElectronIdentification
##This needs to be checked out first since there are conflicts with MVA MET otherwise and then 63 packages are checked out...
#git cms-merge-topic --ssh -u ikrav:egm_id_80X_v2
## additional metfilters
#git cms-merge-topic --ssh -u cms-met:fromCMSSW_8_0_20_postICHEPfilter
#git cms-merge-topic --ssh cms-met:METRecipe_8020 -u
#git cms-merge-topic --ssh cms-met:METRecipe_80X_part2 -u
#sed -i "/produces<edm::PtrVector<reco::Muon>>/a \	  produces<bool>();" RecoMET/METFilters/plugins/BadGlobalMuonTagger.cc
#sed -i "/iEvent.put(std::move(out),/a \	iEvent.put(std::auto_ptr<bool>(new bool(found)));" RecoMET/METFilters/plugins/BadGlobalMuonTagger.cc
##packages needed to rerun tau id
#git cms-merge-topic --ssh -u cms-tau-pog:CMSSW_8_0_X_tau-pog_miniAOD-backport-tauID
#
##correct jet corrections for mvamet
#git cms-merge-topic --ssh -u cms-met:METRecipe_8020
##Mvamet package based on Summer16 Training
#git cms-merge-topic --ssh -u macewindu009:mvamet8026
##copy training weightfile
#mkdir $CMSSW_BASE/src/RecoMET/METPUSubtraction/data
#cd $CMSSW_BASE/src/RecoMET/METPUSubtraction/data
#wget https://github.com/macewindu009/MetTools/raw/nicobranch/MVAMET/weightfiles/weightfile.root
#
#cd $CMSSW_BASE/src
#sed "/import\ switchJetCollection/a from\ RecoMET\.METProducers\.METSignificanceParams_cfi\ import\ METSignificanceParams_Data" PhysicsTools/PatUtils/python/tools/runMETCorrectionsAndUncertainties.py -i
git clone git@github.com:artus-analysis/TauRefit.git VertexRefit/TauRefit
#fetch xml files for Egamma Id from private repository
#git clone git@github.com:ikrav/RecoEgamma-ElectronIdentification.git tempData/RecoEgamma/ElectronIdentification/data
#cd $CMSSW_BASE/src/tempData/RecoEgamma/ElectronIdentification/data
#git checkout egm_id_80X_v1
#cd $CMSSW_BASE/src/tempData/
#cp -r * $CMSSW_BASE/src
#cd $CMSSW_BASE/src
#rm -rf tempData
#
##Remove the .git folder as it is not needed and contains a lot of useless data
#rm -rf RecoEgamma/ElectronIdentification/data/.git
#Check out Kappa
git clone git@github.com:KappaAnalysis/Kappa.git -b ${KAPPA_BRANCH}

wget https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py  -P $CMSSW_BASE/src/Kappa/Skimming/python/

scram b -j `grep -c ^processor /proc/cpuinfo`
