#!/bin/bash

#for electron channel, source with `. checkout74.sh ee`

git cms-addpkg CommonTools/ParticleFlow
git cms-addpkg CommonTools/PileupAlgos
if [ ${1:-''} = 'ee' ]; then
	git cms-merge-topic ikrav:egm_id_7.4.12_v1 # needs CMSSW 7.4.12 or higher 7.4.X
else
	git cms-merge-topic nhanvtran:puppi-etadep-742p1-v6
fi
git clone git@github.com:KappaAnalysis/Kappa.git -b development

#TauRefit (needed for compiling the KRefitVertexProducer)
git clone https://github.com/artus-analysis/TauRefit.git VertexRefit/TauRefit
