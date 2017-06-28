#!/bin/bash
echo "what is \$0: $0"
set -e # exit on errors

echo "set param"
export SCRAM_ARCH=slc6_amd64_gcc491
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
. $VO_CMS_SW_DIR/cmsset_default.sh

echo "Set CMSSW"
scramv1 project CMSSW_7_4_1_patch4;
cd CMSSW_7_4_1_patch4/src
eval `scramv1 runtime -sh`
echo "CMSSW setting is done"

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
# do the git cms-addpkg before starting with checking out cvs repositories

#MVA & No-PU MET Recipe
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet#Instructions_for_7_4_X
#Jan"s multi-MET Producer
git cms-addpkg RecoMET/METPUSubtraction
cd $CMSSW_BASE/src/RecoMET/METPUSubtraction/plugins
wget https://raw.githubusercontent.com/CERN-PH-CMG/cmg-cmssw/CMGTools-from-CMSSW_7_4_3/RecoMET/METPUSubtraction/plugins/PFMETProducerMVATauTau.cc
wget https://raw.githubusercontent.com/CERN-PH-CMG/cmg-cmssw/CMGTools-from-CMSSW_7_4_3/RecoMET/METPUSubtraction/plugins/PFMETProducerMVATauTau.h
cd $CMSSW_BASE/src/RecoMET/METPUSubtraction/
git clone https://github.com/rfriese/RecoMET-METPUSubtraction data -b 74X-13TeV-Summer15-July2015 --depth 1
rm -rf $CMSSW_BASE/src/RecoMET/METPUSubtraction/data/.git/
cd $CMSSW_BASE/src
sed "/mvaOutputCovU1_\ = GetR/c \ \ mvaOutputCovU1_ = std\:\:pow\(GetResponse\(mvaReaderCovU1_, varForCovU1_\)\* mvaOutputU\_ \* var\_\[\"particleFlow\_U\"\]\, 2\)\;" RecoMET/METPUSubtraction/src/PFMETAlgorithmMVA.cc -i
sed "/mvaOutputCovU2_\ = GetR/c \ \ mvaOutputCovU2_ = std\:\:pow\(GetResponse\(mvaReaderCovU2_, varForCovU2_\)\* mvaOutputU\_ \* var\_\[\"particleFlow\_U\"\]\, 2\)\;" RecoMET/METPUSubtraction/src/PFMETAlgorithmMVA.cc -i

git cms-addpkg PhysicsTools/PatUtils
sed "/pat::MET outMET/a \ \ \  outMET\.setSignificanceMatrix\(srcMET\.getSignificanceMatrix\(\)\)\;" PhysicsTools/PatUtils/plugins/CorrectedPATMETProducer.cc -i
cd $CMSSW_BASE/src/PhysicsTools/PatUtils/data
wget https://github.com/cms-met/cmssw/blob/METCorUnc74X/PhysicsTools/PatUtils/data/Summer15_50nsV4_DATA_UncertaintySources_AK4PFchs.txt
cd $CMSSW_BASE/src

#PF MET with NoHF MET
#https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription
#"git cms-merge-topic -u cms-met:METCorUnc74X

#Electron cutBased Id and MVA Id
#https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_7_4
#https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_7412_Spring15_MVA_tr
git cms-merge-topic ikrav:egm_id_7.4.12_v1

#Check out Kappa
git clone https://github.com/KappaAnalysis/Kappa.git

scram b -j 4 -v || {
      echo "The ${CMSSW_BASE} with Kappa could not be built"
      exit 1
}
