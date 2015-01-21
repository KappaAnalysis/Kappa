Todo list {#todo}
=================

## Important

1. to be fixed in the C++ code:
    - dz, dxy in KMuon is not filled correctly (IPTools) http://www-ekp.physik.uni-karlsruhe.de/~berger/kappa/struct_k_muon.html#a62be02f7980e717c78fee69e0457389a -> fix it
2. to be fixed/checked in the configuration
    - is the JetID, JetPUID, btag, electron MVA-ID, tau discriminators configured correctly?
    - configure pt thresholds as agreed upon in a meeting (~ 8GeV Leptons, 10 GeV Jets)
    - use snippet by Andrew to select genParticles (only ME + tau decay chain)
    - remove 'PFCandidates' from active (most important point for smaller skims)


## Other todos

Frage:
- was ist binValue?
- warum TBronch
- warum hxx und nicht in KDebug.cpp?

List:
- renaming IDs/Ids
- Make debug output reflect new data format

- versions:
  - CMSSW 5.3.14 (old)
  - CMSSW 5.3.22 (new 2012)
  - CMSSW 7.0.7_patch1  (CSA)
  - CMSSW 7.2.2 (Phsy14)
  - MiniAOD
- Rewrite TauProducer
- add scripts to KappaTools
- install for skimming
- usage for analysis
  - see KappaTools
- check recipe
- No producer for?
- clean up Producer headers
- remove template from BasicTau
- move lepton in extra file
- Filters
- guidelines: C++11?, must compile with make and scram, 
- timing: run/lumi/event time per prod. CMSSW (rot) Kappa (blau, stacked) pro event
- Kappa tag from git
- Profile: off, auto, on (auto=if cmssw w
- no ints? short or long?
- Recipe: QG, PUJetID, JetID, MVAMET
- list of files that can be run if present
- hltNames: Electron
- unified status scheme following HepMC: 0-4+11->7
- KLeptonProducer
- CMSSW Jet ID als configurable binary ID
- Handles everywhere!

## Documentation
- add todos
- KappaTools doc?
- compare jet und tagged jet in size
- HEPMCProducer raus in eigenene ehader
- Tower im plural?
- Triggerobjects als vector?
- ../../Producers/interface/KGenParticleProducer.h:#define KAPPA_PARTONPRODUCER_H
../../Producers/interface/KHCALNoiseSummaryProducer.h:#define KAPPA_HCALNOISEPRODUCER_H
../../Producers/interface/KLorentzProducer.h:#define KAPPA_LORENTZPRODUCER_H -> LV
../../Producers/interface/KPFCandidateProducer.h:#define KAPPA_PFCandidatePRODUCER_H
../../Producers/interface/KTreeMetadataProducer.h:#define KAPPA_TREE_METADATAPRODUCER_H
- classes + UP in test -> py
- Jet producer must derive from BasicJet producer!
- get json
- reweighting
- 

# CMSSW
[CMSSW on github](https://github.com/cms-sw/cmssw)
[CMSSW Doxygen](https://cmssdt.cern.ch/SDT/doxygen/)
[CMSSW LXR]()
[grid-control]()
[CSA14](https://twiki.cern.ch/twiki/bin/viewauth/CMS/CSA14)
[SCRAM](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideScram)
[EDM](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideEDMGetDataFromEvent)



Jets
----
pt > 5 GeV for Jet studies

Reduce to 2 tags: qg, b and PUIDs


PFCandidates
------------
pt > 10 GeV?
Only within DR 0.5


More things:
- checktools
- list of mandatory skim configs
  - valid commit = make + scram + all mandatory skim configs
- valid for data + mc
- check skim size before/after
- new isolation and IDs (delta beta, no ecal hcal)
- what is kappaNick?
- wie geht update_authors?
- where to host docs?
- required packages: comment in KXXX_cff.py if os.path.exists('PhysicsTools/PatAlgos'): print "Needed"
- sort archive
- reduce examples to: (1) minimal, (2) configured, (3) using KXX_cff, (4) with checkouts=full, (4-5) evtl. noch extras 
- filename list, check, first available taken, order: ekp (default, users), naf (default, users), xrootd
- check for commit: compiles in all versions, runs in all versions with all versions, test outputs


Checks:
CMSSW version  config
5.3.14         1,2,3,4,Higgs,zjet
5.3.22_patch1  1,2,3,4,
7.0.7          1,2,3,4,
7.2.2          1,2,3,4,
