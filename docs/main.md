# κappa {#mainpage}

κappa is the Karlsruhe Package for Physics Analysis.
It is a skimming framework constructed to extract the relevant data
from EDM data sets (RECO, AOD, MINIAOD) and store it in a well-defined
and compact ROOT data format.


Installation
============

Skimming:

setup CMSSW

    cmsrel CMSSW_5_3_14
    cd CMSSW_5_3_14/src
    cmsenv

checkout Kappa

    git clone -b dictchanges https://ekptrac.physik.uni-karlsruhe.de/git/Kappa

compile

    scram b

run

    cmsRun Kappa/Skimming/skim_tutorial_53x.py


The output looks similar to:

    01-Jan-2015 00:00:00 CET  Initiating request to open file file:/path/to/file.root
    01-Jan-2015 00:00:00 CET  Successfully opened file file:/path/to/file.root
    --- Reader                   : Booking "BDT" of type ... if electrons configured
    Electron ID MVA Completed                                until here
    Start Kappa producer KTuple
    Init producer TreeInfo      ... for each configured Kappa producer
    Taking trigger from process HLT (label = TriggerResults)
    Begin processing the 1st record. Run 1, Event 100000, LumiSection 2500 at 01-Jan-2015 00:01:00 CET


Usage and options
-----------------

The Kappa-CMSSW EDProducer has a few options:

- `verbose` (int): Level of verbosity (default: 0)
- `profile` (bool): Enables profiling (default: False)
- `outputFile` (str): Name of the Kappa output file, (e.g. `"kappa.root"`)
- `active` (list): List of object names that should be written out (e.g. `['Electrons']`)

check skim (KappaTools)

- check sizes
- check runtime
- diff skims
- look at distributions


Documentation
=============

The objects of the Kappa data formats can be directly printed on standard out.
Here is an example for jets:

    KJet jet;
    KJets jets;
    std::cout << jet;                    // print the relevant members of the object
    std::cout << displayVector(jets);    // print the vector size and all elements.
    std::cout << displayVector(jets, 2); // print the vector size and the first two elements


Producers hierachy
------------------------------

The base classes for all producers follow this hierarchy structure:

- KBaseProducer
  - KBaseProducerWP: With provenance
    - KInfoProducer: Produce general information of the tree (e.g. KEventInfo)
    - KBaseMatchingProducer: Regular expression matching
      - KBaseMultiProducer: Produce objects per event (e.g. KMET)
        - KBaseMultiVectorProducer: Produce lists (`std::vector`) of objects per event (e.g. KVertices)
          - KBaseMultiLVProducer: Produce lists of particles or other Lorentz-vector objects (e.g KElectron)

The data types of member variables are the same as in CMSSW in order to
not loose precision but at the same time not waste space in the skim.
Note: Even if some member functions of CMSSW data formats return an
int or double type, the underlying member variable is only of char,
short or float precision and therefore the latter is used.

[Minimum sizes](http://www.cplusplus.com/doc/tutorial/variables/):
 8 char
16 short, int
32 long
64 long long
32 float
64 double

Boolean values are mostly stored in bitmaps. Strings should not be part
of a data format of the Events tree. In most cases this information can be stored in the Lumis tree.

Naming scheme {#main-naming}
============================

- K<Object> for all physical objects (e.g. KJet)
- in case there are different versions for one object the object for the
  standard use case is called in the most simple way K<Object>.
  More complicated objects can be named "KExtended<Object>".
  Simpler versions are called "KBasic<Objects>" (e.g. KBasicJet).
- K<Object>Summary for summaries of vector quantities (e.g. KVertexSummary).
- K<Tree>Info for general tree information (e.g KEventInfo).
- K<Object>Metadata for objects stored in lumi tree containing
  information about the corresponding object in the event tree


Changes in Kappa 2.0 {#main-changes}
====================================

The changes can be seen using this command:
``git log 39aeb59..electronunification``
or in the [change log](https://ekptrac.physik.uni-karlsruhe.de/trac/Kappa/timeline).

- **Changes in Lorentz vector definitions**:

  There are two ROOT::Math Lorentz vectors:
  RMFLV and RMDLV in float and double precision.
  And there is now only one Kappa base class: KLV (float precision)
  which is used as base class for all particles.
  This is chosen because the Lorentz vectors in the reco format are
  float precision.
  - Remove unused KLV
  - Rename KDataLV to KLV
  - Remove the LVWrap
  - Rename RMDataLV to RMFLV and RMLV to RMDLV
  
- **Renaming, moving and removing data format classes and producers**:

  Many classes and files are renamed. This is done to consolidate the
  naming following a consistent [naming scheme](#main-naming):
  - 
  
  These are the commits containing the changes:
  - Rename data format classes and producers ([dbe9b1c]())
  - Update with classes.UP ([91a9b28]())
  - Rename producer headers to match the contained producer class ([a02547e]())
  - Rename object metadata classes ([993b42f]())
  - Rename event and lumi infos
  - Rename KMetadata.h to KInfo.h
  - Move data format definitions (2)
  - Simplify header dependencies
  - Unified naming scheme for branch names
  - Remove KCaloTaus
  - Remove KCandidateProducer

- **Update the data format content**:

  The data format definition is adapted to new needs. The changes are
  done such that it is more flexible for future requirements.
  
  There are no changes in these classes:
  KBasicMET, KDataLumiInfo, KFilterMetadata, KFilterSummary, KGenEventInfo,
  KGenLumiInfo, KEventInfo, KHCALNoiseSummary, KHit, KPileupDensity, KL1Muon,
  KLumiInfo, KMuonTriggerCandidate, KProvenance, KTrackSummary, KVertex,
  KVertexSummary.

  KTriggerObjectMetadata, KTriggerObjects, ,  
  KGenParticle, KGenPhoton, KGenTau, KPFCandidate,  

  - KParticle (new)
  - KBeamSpot (
  - KTrack
  - KLepton
  - KElectron, KElectronMetadata
  - KMuon, KMuonMetadata
  - KBasicTau
  - KTau, KTauMetadata
  - KCaloJet
  - KBasicJet
  - KJet, KJetMetadata
  - KMET
  - Documentation of all dataformats


- **Changes in the producers**:

- Infrastructure changes:
  - classes is now written in [Markdown]
  - classes.UP also handles LinkDef.h
  - update with new classes.UP

- Implementation of missing debug output for new classes:
  KElectronMetadata, KFilterMetadata, KGenPhoton, KHCALNoiseSummary,
  KJetMetadata, KL1Muon, KLepton, KMuon, KMuonTriggerCandidate,
  KParticle, KPhoton, KTau, KTrack, KTriggerObjects,
  KTriggerObjectMetadata.
- All producers run without extra CMSSW configs
- Add Minimal Kappa config
- Sort Skimming folder

________________________________________________________________________________
This file is written in [Markdown].

[KIT]:      http://www.ekp.kit.edu "Institut für Experimentelle Kernphysik"
[code]:     https://ekptrac.physik.uni-karlsruhe.de/trac/Kappa "Trac on ekptrac"
[CMSSW]:    https://github.com/cms-sw/cmssw "CMSSW on github"
[CMS Wiki]: https://twiki.cern.ch/twiki/bin/viewauth/CMS/WebHome "CMS twiki"
[Workbook]: https://twiki.cern.ch/twiki/bin/viewauth/CMS/OnlineWB "CMS Workbook"
[Doxygen]:  http://www.stack.nl/~dimitri/doxygen/index.html "Doxygen"
[Markdown]: http://daringfireball.net/projects/markdown "Markdown"


