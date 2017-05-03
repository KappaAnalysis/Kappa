#!/bin/sh
echo "# ================= #"
echo "# ls cvmfs"
echo "# ================= #"
ls /etc/cvmfs/
echo "# ================= #"
echo "# run-cvmfs.sh"
echo "# ================= #"
cat /etc/cvmfs/run-cvmfs.sh
echo "# ================= #"
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

git clone https://github.com/artus-analysis/TauRefit.git VertexRefit/TauRefit"

echo "# ================= #"
echo "# Building in CMSSW #"
echo "# ================= #"

scram b -v -j 2 || exit 1

echo "# =================== #"
echo "# Building standalone #"
echo "# =================== #"
