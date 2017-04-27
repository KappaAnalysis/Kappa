#!/bin/sh

echo "# very specific tests of input files"

echo ":: /etc/yum.repos.d/cernvm.repo "
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

cd src/

mkdir Kappa
cp -r /home/travis/* Kappa/

echo "# ================= #"
echo "# Building in CMSSW #"
echo "# ================= #"

scram b -v -j 2 || exit 1

echo "# =================== #"
echo "# Building standalone #"
echo "# =================== #"
