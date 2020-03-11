#!/bin/bash
#set -e # exit on errors

ssh -vT git@github.com

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

echo -n "Enter the Linux release you want to use (SL6, SL7 [default]) and press [ENTER]: "
read sl_version

if [[ $sl_version = "SL6" ]] || [[ $sl_version = "6" ]] || [[ $sl_version = "SLC6" ]]; then
    scramv1 project -n CMSSW_10_2_20_kappa CMSSW CMSSW_10_2_20
elif [[ $sl_version = "SL7" ]] || [[ $sl_version = "7" ]] || [[ $sl_version = "SLC7" ]]; then
    scramv1 project -n CMSSW_10_2_20_kappa CMSSW CMSSW_10_2_20_UL
else
    scramv1 project -n CMSSW_10_2_20_kappa CMSSW CMSSW_10_2_20_UL
fi
cd CMSSW_10_2_20_kappa/src/
eval `scramv1 runtime -sh`

export KAPPA_BRANCH="dictchanges_CMSSW102X"
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

git cms-init

# Get DeepFlavour b-tagger (optional)
# MB: assume that it is not needed with 10_2_16
#git cms-addpkg RecoBTag/TensorFlow
#git cherry-pick 94ceae257f846998c357fcad408986cc8a039152

# Get working version of HTXSRivetProducer (mainly relevant for SM HTT)
# MB: it should be fine with 10_2_16

# Get code for electron scale & smear corrections
# see: https://twiki.cern.ch/twiki/bin/view/CMS/EgammaMiniAODV2
git cms-merge-topic cms-egamma:EgammaPostRecoTools

# Get recipes to re-correct MET (also for ECAL noise)
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETUncertaintyPrescription#Instructions_for_2017_data_with
#git cms-merge-topic cms-met:METFixEE2017_949_v2_backport_to_102X #MB: It got merged with 10_2_7

# Get deepTau 2017v2p1 Tau ID (and Tau ID Embedder)
#git cms-merge-topic 27879 #MB: It got merged with 10_2_17

# add MVA DM code and xml files
git cms-merge-topic -u danielwinterbottom:from-CMSSW_10_2_16-mvaDM

# CP: Refitting package
git clone git@github.com:artus-analysis/TauRefit.git VertexRefit/TauRefit

#Check out Kappa
git clone git@github.com:KappaAnalysis/Kappa.git -b ${KAPPA_BRANCH}

# B-tag:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
# NEEDS UPDATE

scram b -j `grep -c ^processor /proc/cpuinfo`
