#!/bin/bash
#set -e # exit on errors

ssh -vT git@github.com

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_9_4_11_cand2
cd CMSSW_9_4_11_cand2/src
eval `scramv1 runtime -sh`

export KAPPA_BRANCH="dictchanges_CMSSW94X"
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
#References:
##https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_92X
##https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recommended_MVA_Recipe_for_regul
##https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_8_0
##https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_regular_users_common



git cms-init

# Get DeepFlavour b-tagger (optional)
git cms-addpkg RecoBTag/TensorFlow
git cherry-pick 94ceae257f846998c357fcad408986cc8a039152

# Get working version of HTXSRivetProducer (mainly relevant for SM HTT)
#TODO the new version in CMSSW_9_4_11_cand1 is validated. To be followed up
#git cms-addpkg GeneratorInterface/RivetInterface
#cd GeneratorInterface/RivetInterface/plugins
#rm HTXSRivetProducer.cc
#wget https://raw.githubusercontent.com/perrozzi/cmssw/HTXS_clean/GeneratorInterface/RivetInterface/plugins/HTXSRivetProducer.cc
#cd -

# Get code for electron V2 ID's (trained on 94X MC's)
git cms-merge-topic guitargeek:EgammaID_949



# Get code for electron scale & smear corrections
git cms-merge-topic cms-egamma:EgammaPostRecoTools_940

# Get recipes to re-correct MET (also for ECAL noise)
git cms-merge-topic cms-met:METFixEE2017_949_v2 #https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETUncertaintyPrescription#Instructions_for_9_4_X_X_9_for_2

# Get deep Tau & DPF based Tau ID (and Tau ID Embedder) (deep Tau & DPF Tau optional)
git cms-merge-topic ocolegro:dpfisolation # consists updated version of runTauIdMVA.py (RecoTauTag/RecoTau/python/runTauIdMVA.py). Originally, this .py file comes from https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py

rm -rf RecoTauTag/RecoTau/data/


#---------OLD--------
# TAU: Packages needed to rerun tau id
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Rerunning_of_the_tau_ID_on_M_AN1
# NEEDS UPDATE
#wget https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py  -P $CMSSW_BASE/src/Kappa/Skimming/python/


# Get latest anti-e discriminator MVA6v2 (2017 training) (optional)
#TODO some files need to be copied from afs. A proper integration of the files will be done by Tau POG. To be followed up.
git cms-merge-topic cms-tau-pog:CMSSW_9_4_X_tau-pog_updateAntiEDisc

# CP: Refitting package
git clone git@github.com:artus-analysis/TauRefit.git VertexRefit/TauRefit

#Check out Kappa
git clone git@github.com:KappaAnalysis/Kappa.git -b ${KAPPA_BRANCH}

# B-tag:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
# NEEDS UPDATE


scram b -j `grep -c ^processor /proc/cpuinfo`
