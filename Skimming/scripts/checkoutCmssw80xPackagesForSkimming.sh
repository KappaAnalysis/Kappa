#!/bin/sh
set -e # exit on errors

export SCRAM_ARCH=slc6_amd64_gcc530
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
. $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW CMSSW_8_0_26_patch1
cd CMSSW_8_0_26_patch1/src
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

# MET:
# Correct jet corrections for mvamet
#git cms-merge-topic -u cms-met:METRecipe_8020
# Mvamet package based on Summer16 Training
git cms-merge-topic -u macewindu009:mvamet8026

# TAU: Packages needed to rerun tau id
# git cms-merge-topic -u -s theirs cms-tau-pog:CMSSW_8_0_X_tau-pog_tauIDOnMiniAOD-legacy-backport-81X

# MET:
# copy training weightfile
mkdir $CMSSW_BASE/src/RecoMET/METPUSubtraction/data
cd $CMSSW_BASE/src/RecoMET/METPUSubtraction/data
wget https://github.com/macewindu009/MetTools/raw/nicobranch/MVAMET/weightfiles/weightfile.root --no-check-certificate

# EM:
# Electron cutBased Id and MVA Id
#https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_8_0
#https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_regular_users_common
git cms-addpkg RecoMET/METPUSubtraction
git cms-addpkg DataFormats/METReco
git cms-addpkg PhysicsTools/PatUtils
git cms-addpkg RecoEgamma/ElectronIdentification
#Above needs to be checked out first since there are conflicts with MVA MET otherwise and then 63 packages are checked out...

# This is an old recipe : https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2Archive
#git cms-merge-topic -u ikrav:egm_id_80X_v2

# MET:
# Additional metfilters
git cms-merge-topic -u cms-met:fromCMSSW_8_0_20_postICHEPfilter
git cms-merge-topic cms-met:METRecipe_8020 -u
git cms-merge-topic cms-met:METRecipe_80X_part2 -u



# CP:
cd $CMSSW_BASE/src
git clone https://github.com/artus-analysis/TauRefit.git VertexRefit/TauRefit

# EM:
# fetch xml files for Egamma Id from private repository
git clone https://github.com/ikrav/RecoEgamma-ElectronIdentification.git tempData/RecoEgamma/ElectronIdentification/data
cd $CMSSW_BASE/src/tempData/RecoEgamma/ElectronIdentification/data
git checkout egm_id_80X_v1
cd $CMSSW_BASE/src/tempData/
cp -r * $CMSSW_BASE/src
cd $CMSSW_BASE/src
rm -rf tempData

# CLEANUP:
# Remove the .git folder as it is not needed and contains a lot of useless data
rm -rf RecoEgamma/ElectronIdentification/data/.git
# Remove Fireworks and SimGeneral - they are only checked out due to failed merge attempts
rm -rf Fireworks
rm -rf SimGeneral
rm -rf RecoEgamma
sed -i '/Fireworks/d' .git/info/sparse-checkout
sed -i '/SimGeneral/d' .git/info/sparse-checkout
sed -i '/RecoEgamma/d' .git/info/sparse-checkout
git read-tree -mu HEAD

# do the sed's afterwards -> bevore, the read-tree fails
sed -i "/produces<edm::PtrVector<reco::Muon>>/a \	  produces<bool>();" RecoMET/METFilters/plugins/BadGlobalMuonTagger.cc
sed -i "/iEvent.put(std::move(out),/a \	iEvent.put(std::auto_ptr<bool>(new bool(found)));" RecoMET/METFilters/plugins/BadGlobalMuonTagger.cc
sed "/import\ switchJetCollection/a from\ RecoMET\.METProducers\.METSignificanceParams_cfi\ import\ METSignificanceParams_Data" PhysicsTools/PatUtils/python/tools/runMETCorrectionsAndUncertainties.py -i

# Check out Kappa:
git clone https://github.com/KappaAnalysis/Kappa.git -b ${KAPPA_BRANCH}


# Compile:
scram b -v -j `grep -c ^processor /proc/cpuinfo` || {
      echo "The ${CMSSW_BASE} with Kappa could not be built"
      exit 1
}
