#!/bin/bash

git cms-addpkg CommonTools/ParticleFlow
git cms-addpkg CommonTools/PileupAlgos
git cms-merge-topic nhanvtran:puppi-etadep-742p1-v6
git clone git@github.com:KappaAnalysis/Kappa.git -b development
