#!/bin/bash

cd ${CMSSW_BASE}/src
git cms-addpkg RecoMET/METFilters
git clone https://github.com/KappaAnalysis/Kappa.git && cd Kappa && git checkout newtagging && cd ..
git clone https://github.com/cms-analysis/RecoMET-METAnalyzers.git RecoMET/METAnalyzers

git clone https://github.com/amarini/QuarkGluonTagger.git && cd QuarkGluonTagger && git checkout v1-2-6 && cd ..
git clone https://github.com/h2gglobe/External CMGTools/External && sed -i 's%RecoJets/JetProducers%CMGTools/External%g' CMGTools/External/python/puJetIDAlgo_cff.py

cd ${CMSSW_BASE}
 
