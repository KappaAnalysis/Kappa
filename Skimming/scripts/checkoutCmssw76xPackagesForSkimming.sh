#!/bin/bash
set -e # exit on errors

echo "set param"
export SCRAM_ARCH=slc6_amd64_gcc493
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

echo "set cmssw"
scramv1 project CMSSW CMSSW_7_6_3
cd CMSSW_7_6_3/src
#eval `scramv1 runtime -sh`
cmsenv

echo "Checking system variables"
echo "PYTHONSTARTUP=$PYTHONSTARTUP"
echo "PYTHONPATH=$PYTHONPATH"
echo "SCRAM_ARCH=$SCRAM_ARCH"
echo "VO_CMS_SW_DIR=$VO_CMS_SW_DIR"
echo "CMSSW_VERSION=$CMSSW_VERSION"
echo "CMSSW_GIT_HASH=$CMSSW_GIT_HASH"
echo "CMSSW_BASE=$CMSSW_BASE"
echo "CMSSW_RELEASE_BASE=$CMSSW_RELEASE_BASE"

# Re-configure git if needed
set +e
echo "set git config"
git_github="$(git config --global --get-all user.github)"
git_email="$(git config --global --get-all user.email)"
git_name="$(git config --global --get-all user.name)" 
echo "git config before:" $git_github $git_email $git_name

while getopts :g:e:n: option
do
	case "${option}"
	in
	g) git config --global user.github ${OPTARG};;
	e) git config --global user.email ${OPTARG};;
	n) git config --global user.name "\"${OPTARG}\"";;
	esac
done

git_github=`git config --get user.github`
git_email=`git config --get user.email`
git_name=`git config --get-all user.name`
echo "git config after:" $git_github $git_email $git_name
set -e

cd $CMSSW_BASE/src
git cms-merge-topic -u KappaAnalysis:Kappa_CMSSW_763
git cms-addpkg RecoMET/METPUSubtraction
git cms-addpkg DataFormats/METReco
#Electron cutBased Id and MVA Id
#https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_747
#https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_747_Spring15_MVA_tra
#"git cms-merge-topic ikrav:egm_id_747_v2
git clone https://github.com/artus-analysis/TauRefit.git VertexRefit/TauRefit

#Check out Kappa
git clone https://github.com/KappaAnalysis/Kappa.git

scram b -j 4 -v || {
      echo "The ${CMSSW_BASE} with Kappa could not be built"
      exit 1
}

