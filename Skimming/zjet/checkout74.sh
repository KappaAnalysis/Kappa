#!/bin/bash

cd $CMSSW_BASE/src
git-cms-addpkg CommonTools/ParticleFlow
git clone git@github.com:KappaAnalysis/Kappa.git -b development
