#!/bin/sh
#set -e # exit on errors

ssh -vT git@github.com

export SCRAM_ARCH=slc6_amd64_gcc493
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
. $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW CMSSW_7_6_3
cd CMSSW_7_6_3/src
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
git cms-merge-topic --ssh -u KappaAnalysis:Kappa_CMSSW_763
git cms-addpkg RecoMET/METPUSubtraction
git cms-addpkg DataFormats/METReco
#Electron cutBased Id and MVA Id
#https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_747
#https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_747_Spring15_MVA_tra
#"git cms-merge-topic ikrav:egm_id_747_v2
git clone git@github.com:artus-analysis/TauRefit.git VertexRefit/TauRefit

#Check out Kappa
git clone git@github.com:KappaAnalysis/Kappa.git -b ${KAPPA_BRANCH}

scram b -v -j `grep -c ^processor /proc/cpuinfo` || {
      echo "The ${CMSSW_BASE} with Kappa could not be built"
      exit 1
}
