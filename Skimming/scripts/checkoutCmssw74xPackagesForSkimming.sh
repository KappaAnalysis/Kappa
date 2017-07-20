#!/bin/sh
set -e # exit on errors

export SCRAM_ARCH=slc6_amd64_gcc491
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
. $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW CMSSW_7_4_16_patch2;
cd CMSSW_7_4_16_patch2/src
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
# do the git cms-addpkg before starting with checking out cvs repositories

#MVA & No-PU MET Recipe
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet#Instructions_for_7_4_X
#everything needed is already in the 7_4_6 release -> only use 7_4_7 due to bugfix!
#Jan"s multi-MET Producer
git cms-addpkg RecoMET/METPUSubtraction
cd $CMSSW_BASE/src/RecoMET/METPUSubtraction/plugins
wget https://raw.githubusercontent.com/CERN-PH-CMG/cmg-cmssw/CMGTools-from-CMSSW_7_4_3/RecoMET/METPUSubtraction/plugins/PFMETProducerMVATauTau.cc
wget https://raw.githubusercontent.com/CERN-PH-CMG/cmg-cmssw/CMGTools-from-CMSSW_7_4_3/RecoMET/METPUSubtraction/plugins/PFMETProducerMVATauTau.h
#"git remote add cmgtools https://github.com/CERN-PH-CMG/cmg-cmssw.git
#"git pull cmgtools
#"git checkout CMGTools-from-CMSSW_7_4_7
cd $CMSSW_BASE/src/RecoMET/METPUSubtraction/
git clone https://github.com/rfriese/RecoMET-METPUSubtraction data -b 74X-13TeV-Summer15-July2015 --depth 1
rm -rf $CMSSW_BASE/src/RecoMET/METPUSubtraction/data/.git/
cd $CMSSW_BASE/src

git cms-addpkg PhysicsTools/PatUtils
sed "/pat::MET outMET/a \ \ \  outMET\.setSignificanceMatrix\(srcMET\.getSignificanceMatrix\(\)\)\;" PhysicsTools/PatUtils/plugins/CorrectedPATMETProducer.cc -i

#PF MET with NoHF MET
#https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription
git cms-merge-topic -u cms-met:METCorUnc74X

#Electron cutBased Id and MVA Id
#https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_747
#https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_747_Spring15_MVA_tra
git cms-merge-topic ikrav:egm_id_747_v2

#Check out Kappa
git clone https://github.com/KappaAnalysis/Kappa.git -b ${KAPPA_BRANCH}

scram b -v -j 4 || {
      echo "The ${CMSSW_BASE} with Kappa could not be built"
      exit 1
}
