#!/bin/bash
set -e # exit on errors

export SCRAM_ARCH=slc6_amd64_gcc491
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW CMSSW_5_3_35
cd CMSSW_5_3_35/src
eval `scramv1 runtime -sh`

# Re-configure git if needed
set +e
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

#Electrons
git cms-addpkg EgammaAnalysis/ElectronTools
cd $CMSSW_BASEE/src/EgammaAnalysis/ElectronTools/data/
cat download.url | xargs wget
cd $CMSSW_BASE/src

# https://twiki.cern.ch/twiki/bin/view/CMS/GluonTag
git clone git://github.com/amarini/QuarkGluonTagger.git -b v1-2-3

# PU Jet ID as used in TauTau and needed for MVA MET (does not work with git cms-cvs-history and does not compile with cvs co)
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet#CMSSW_5_3_22_patch1_requires_slc


#PAT Recipe (https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X)
git cms-addpkg PhysicsTools/PatAlgos
git cms-merge-topic -u cms-analysis-tools:5_3_16_patch1-testNewTau

#MET Recipe (https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMETRecipe53X)
git cms-merge-topic -u TaiSakuma:53X-met-140217-01

#MVA & No-PU MET Recipe
git-cms-merge-topic -u cms-met:53X-MVaNoPuMET-20140606-01

git clone git://github.com/ajaykumar649/Jets_Short.git
cp -r Jets_Short/* $CMSSW_BASE/src
rm -rf Jets_Short

# PF isolation
git-cms-addpkg CommonTools/ParticleFlow

# Tau Jets
git cms-addpkg PhysicsTools/JetMCAlgos

#Check out Kappa
git clone https://github.com/KappaAnalysis/Kappa.git


# fixes for SLC6
cp Kappa/Skimming/higgsTauTau/kappa_sl6_fix/CMSDAS12ThreejetTestAnalyzer.cc  RecoJets/JetAnalyzers/src/CMSDAS12ThreejetTestAnalyzer.cc
cp Kappa/Skimming/higgsTauTau/kappa_sl6_fix/JetSubstructurePlotsExample.cc  RecoJets/JetAnalyzers/src/JetSubstructurePlotsExample.cc
cp Kappa/Skimming/higgsTauTau/kappa_sl6_fix/myFastSimVal.cc  RecoJets/JetAnalyzers/src/myFastSimVal.cc
cp Kappa/Skimming/higgsTauTau/kappa_sl6_fix/myJetAna.cc  RecoJets/JetAnalyzers/src/myJetAna.cc

# fixes for classes
cp Kappa/Skimming/higgsTauTau/kappa_fixmissing_class/classes_def.xml Kappa/DataFormats/src/classes_def.xml

scram b -j 4 -v || {
      echo "The ${CMSSW_BASE} with Kappa could not be built"
      exit 1
}
