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

scram project ${TEST_CMSSW_VERSION}

cd ${TEST_CMSSW_VERSION}

cmsenv
echo "# ================= #"
echo "# curl -O"
echo "# ================= #"
echo "curl -O https://cernbox.cern.ch/index.php/s/BgWZaBJFB2y4688/download /home"
curl -O https://cernbox.cern.ch/index.php/s/BgWZaBJFB2y4688/download /home
echo"ls /home"
ls /home
echo
echo "# ================= #"
echo "# xrootd"
echo "# ================= #"
xrootd -d l -f root://eosuser.cern.ch://eos/user/o/ohlushch/kappatest_inputfiles/input/SUSYGluGluToHToTauTau_M-160_fall15_miniAOD.root
#root -l root://eosuser.cern.ch://eos/user/o/ohlushch/kappatest_inputfiles/input/SUSYGluGluToHToTauTau_M-160_fall15_miniAOD.root
echo

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
cd $CMSSW_BASE 
echo
echo
echo "# ================= #"
echo "# Building in CMSSW #"
echo "# ================= #"
scram b -v -j 2 || exit 1

echo "# =================== #"
echo "# Building standalone #"
echo "# =================== #"

echo $CMSSW_BASE
#make -C Kappa/DataFormats/test -j2 || exit 1

