#!/bin/sh
echo
echo "# very specific tests of input files"
echo "Testing most probably included in the image files"
echo "1) /etc/yum.repos.d/cernvm.repo "
cat /etc/yum.repos.d/cernvm.repo
echo
echo ":: /etc/cvmfs/default.local"
cat /etc/cvmfs/default.local
echo
echo ":: /etc/cvmfs/domain.d/cern.ch.local"
cat /etc/cvmfs/domain.d/cern.ch.local
echo 
echo ":: /etc/cvmfs/keys"
cat /etc/cvmfs/keys
echo
echo "/etc/cvmfs/run-cvmfs.sh"
cat /etc/cvmfs/run-cvmfs.sh
echo
echo "###################"
echo "# ================= #"
echo "# ls cvmfs"
echo "# ================= #"
ls /etc/cvmfs/

echo ""
echo "# ================= #"
echo "# run-cvmfs.sh"
echo "# ================= #"
cat /etc/cvmfs/run-cvmfs.sh
echo "# ================= #"
echo ""
/etc/cvmfs/run-cvmfs.sh

# export SCRAM_ARCH=slc6_amd64_gcc481
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

mkdir -p /home/build && cd /home/build

echo "# ================= #"
echo "# cmsset_default.sh"
echo "# ================= #"
cat $VO_CMS_SW_DIR/cmsset_default.sh
echo "# ================= #"
. $VO_CMS_SW_DIR/cmsset_default.sh

echo "# ================= #"
echo "# Compiling CMSSW"
echo "# ================= #"
scram project ${TEST_CMSSW_VERSION}

cd ${TEST_CMSSW_VERSION}

cmsenv

echo "number of processors:"
cat /proc/cpuinfo | awk '/^processor/{print $3}'

echo "# ================= #"
echo "# curl -O root files"
echo "# ================= #"
echo "curl -O https://cernbox.cern.ch/index.php/s/BgWZaBJFB2y4688/download /home"
# single file: curl -O https://cernbox.cern.ch/index.php/s/BgWZaBJFB2y4688/download 
curl -o short_rootfiles.tar https://cernbox.cern.ch/index.php/s/WeawecKp2BD2BH2/download /home
tar -xvf short_rootfiles.tar

echo "\nCurrect dir:"
pwd
echo
echo "Content of ~/short:"
ls ~/short 
echo
exit 1

#echo "# ================= #"
#echo "# xrootd"
#echo "# ================= #"
#xrootd -d l -f root://eosuser.cern.ch://eos/user/o/ohlushch/kappatest_inputfiles/input/SUSYGluGluToHToTauTau_M-160_fall15_miniAOD.root
#root -l root://eosuser.cern.ch://eos/user/o/ohlushch/kappatest_inputfiles/input/SUSYGluGluToHToTauTau_M-160_fall15_miniAOD.root
#echo

echo "# ================= #"
echo "# download checkout script for Kappa"
echo "# ================= #"
#mkdir Kappa
#cp -r /home/travis/* Kappa/
cd ../../
curl -O https://raw.githubusercontent.com/KappaAnalysis/Kappa/master/Skimming/scripts/${CHECKOUTSCRIPT}
git config --global user.github greyxray
git config --global user.email 'greyxray@gmail.com'
git config --global user.name 'kappa test'
printf "no\n" | python ${CHECKOUTSCRIPT}
test ! -z $CMSSW_BASE
cd $CMSSW_BASE 

echo "# ================= #"
echo "# Building in CMSSW_BASE #"
echo "# ================= #"
scram b -v -j 4 || exit 1
cd src/Kappa
mkdir kappa_run
cd kappa_run

echo "# =================== #"
echo "# Test standalone #"
echo "# =================== #"

uname -a
echo "HOSTNAME=$HOSTNAME"
echo "SHELL=$SHELL"
python --version

echo "python:" $(which python)
echo "PYTHONSTARTUP=$PYTHONSTARTUP"
echo "PYTHONPATH=$PYTHONPATH"
echo "SCRAM_ARCH=$SCRAM_ARCH"
echo "VO_CMS_SW_DIR=$VO_CMS_SW_DIR"
echo "CMSSW_VERSION=$CMSSW_VERSION"
echo "CMSSW_GIT_HASH=$CMSSW_GIT_HASH"
echo "CMSSW_BASE=$CMSSW_BASE"
echo "CMSSW_RELEASE_BASE=$CMSSW_RELEASE_BASE"

echo "# =================== #"
echo "# Test Config #"
echo "# =================== #"
python $CMSSW_BASE/Kappa/Skimming/examples/skim_tutorial1_basic.py
#higgsTauTau/kSkimming_run2_cfg.py

echo "# =================== #"
echo "# Test cmsRun #"
echo "# =================== #"
python $CMSSW_BASE/Kappa/Skimming/examples/skim_tutorial1_basic.py
#higgsTauTau/kSkimming_run2_cfg.py


echo "# =================== #"
echo "# Test Output root file #"
echo "# =================== #"
ls -l kappa.root
test -f kappa.root

echo "The end"
#make -C Kappa/DataFormats/test -j2 || exit 1

