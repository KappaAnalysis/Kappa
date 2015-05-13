#!/bin/bash

# use scram b with
# USER_CXXFLAGS="-Wno-delete-non-virtual-dtor -Wno-error=unused-but-set-variable -Wno-error=unused-variable"
#

cd $CMSSW_BASE/src
git-cms-addpkg CommonTools/ParticleFlow
git clone git@github.com:KappaAnalysis/Kappa.git -b development
git clone https://github.com/amarini/QuarkGluonTagger.git -b v1-2-6

#PU Jet ID
git clone git://github.com/ajaykumar649/Jets_Short.git
cp -r Jets_Short/* .
rm -rf Jets_Short README.md
