# Physical Objects {#mainpage}

[TOC]

This page describes the physical objects in the Kappa framework.
The list of all dataformat classes as used for the compilation of Kappa is given
in the [Class Listing](md__data_formats_src_classes.html).

For each particle (everything that has a four-vector) listed here, the following
information is provided:

- The **data format** of the particle in Kappa. The link provides information about the
  definitions (members, methods) and inheritance.
  Related formats in parenthesis include the name of the *collection* (plural
  form) of these particles (std::vector). It is used to group all such particles in
  one event.
  Some data formats have configurable meanings of members. The these names are
  then stored in the corresponding *Infos* class which is listed here.
  - The source data format as used in [CMSSW]. The name directly points to its
    definition on github (currently in `CMSSW_7_3_X`).
  - Wiki pages in the cern twiki including the workbook, the POG-twikis,
    ID definitions ...
- The **producers** are listed beginning with the most important one.
  If no producer is available this can have several reasons:
  The data format is a base class and only derived classes are used (*base class*),
  The data format is defined to be used as member in other classes (*member class*),
  It just has not been implemented yet (*not implemented*).
  - The *active* string which turns on the production of this producer in the
    skim when added to `process.kappatuple.active = cms.vstring( … )`.
  - The default configuration can be found in the file KTuple_cff.py as 
    `cms.PSet`. Please search for the producer name (*active*) there.
  - Some producers expect other packages to be installed. These are then listed
    as required [CMSSW] packages.
  - Some producers expect other packages to be run before the actual skimming
    with Kappa. The corresponding [CMSSW] configuration for these packages should
    be given here.

Non-particle data formats ...

Since there were changes on the data format recently, the *Changes* section
lists them including a link to the commits.


Basic objects
=============

Lorentz Vector
--------------
KLV
In case the additional information that comes with the dataformats below is not
needed for your skim, you can skim all physical objects as Lorentz vectors.
This is often done for generator jets for example.

- **data format**: KLV (KLVs)
- **producers**: KLVProducer
  - producer name (active): LVs
  - default configuration: KTuple_cff.py > LVs


Beam Spot
---------
[reco::BeamSpot]()

Hit
---
[reco::Hit]()

Pileup Density
-------------

double

Track
-----

[reco::Track](https://github.com/cms-sw/cmssw/blob/CMSSW_7_3_X/DataFormats/TrackReco/interface/Track.h "CMSSW")
([TrackBase.h](https://github.com/cms-sw/cmssw/blob/CMSSW_7_3_X/DataFormats/TrackReco/interface/TrackBase.h "CMSSW"))


Vertex
------
[reco::Vertex]()

Leptons {#obj-leptons}
======================

KLepton is the base format for leptons. The data format contains the four-vector
(from KLV) the flavour (KLepton::Flavour) charge and the track (KTrack) of the
particle.

Electron {#obj-electron}
------------------------

The KElectron contains information about the electrons and positrons as reconstructed by the CMS detector.
It has an associated KElectronInfos class, storing the names of electron IDs as
keys for the values in electronID.
Recommended \f$p_T\f$ threshold: 8 GeV (because of trigger: Mu17, Mu8).

- **data format**: KElectron (KElectrons, KElectronMetadata)
  - source format:
    [pat::Electron](https://github.com/cms-sw/cmssw/blob/CMSSW_7_3_X/DataFormats/EgammaCandidates/interface/Electron.h "CMSSW")
  - Wiki:
    [E-Gamma POG](https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaPOG "CMS twiki"),
    [IDs](https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaIDRecipes "CMS twiki"),
    [cutbased ID](https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaCutBasedIdentification?rev=32 "CMS twiki"),
    [MVA ID (run 1)](http:// "CMS twiki"),
    [MVA ID (run 2)](https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2 "CMS twiki"),
    [Isolation](https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaPFBasedIsolation?r=54 "CMS twiki")

- **producers**: KElectronProducer
  - producer name (active): Electrons
  - default configuration: KTuple_cff.py > Electrons
  - required CMSSW packages: *none*
  - required CMSSW configuration: KElectrons_cff.py

Changes in Kappa 2:
- Flexible IDs
- isEB functions etc.

Muon {#obj-muon}
----------------

The KMuon contains information about the muons (both particle and anti-particle)
as reconstructed by the CMS detector.
The special tracks for high-$p_T$ muons and the corresponding ID are not stored.
Recommended \f$p_T\f$ threshold: 8 GeV (because of trigger: Mu17/Mu8).

- **data format**: KMuon (KMuons, KMuonMetadata)
  - source format:
    [reco::Muon](https://github.com/cms-sw/cmssw/blob/CMSSW_7_3_X/DataFormats/Muon/interface/Muon.h "CMSSW")
  - Wiki:
    [Muon POG](),
    [Muons](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMuonAnalysis)
    [Muon ID](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMuonId),
    [Muon ID](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMuonAnalysis#MuonId)
    [Muon isolation](https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonIsolation)

- **producers**: KMuonProducer
  - producer name (active): Muons
  - default configuration: KTuple_cff.py > Muons
  - required CMSSW packages: *none*
  - required CMSSW configuration: KMuons_cff.py

Changes in Kappa 2:
- nStripLayers is now what the name says and not nTrackerLayers as before


### L1 Muon {#obj-l1muon}

For trigger studies the L1 muon data format can be used to store the track of
such muons.

- **data format**: KL1Muon (KL1Muons)
  - source format:
    [l1extra::L1MuonParticle](http "CMSSW")
  - Wiki:

- **producers**: KL1MuonProducer, KL2MuonProducer
  - producer name (active): L1Muons
  - default configuration: KTuple_cff.py > L1Muons


### Muon Trigger Candidate {#obj-muoncand}

The exact purpose is currently unknown.

- **data format**: KMuonTriggerCandidate (KMuonTriggerCandidates)
  - source format: reco::RecoChargedCandidate
  - Wiki: out-dated: http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/CMSSW/DQM/HLTEvF/plugins/HLTMuonDQMSource.cc?revision=1.40

Tau {#obj-tau}
--------------

The KMuon contains information about the muons (both particle and anti-particle) as reconstructed by the CMS detector.

- **data format**: KTau (KTaus, KTauMetadata); KBasicTau (KBasicTaus, KTauMetadata)
  - source format:
    [reco::Tau](https://github.com/cms-sw/cmssw/blob/CMSSW_7_3_X/DataFormats/Muon/interface/Muon.h "CMSSW")
  - Wiki:
    [Tau POG](),
    [TauID](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID),

- **producers**: KTauProducer, KBasicTauProducer
  - producer name (active): Muons
  - default configuration: KTuple_cff.py > Muons
  - required CMSSW packages: *none*
  - required CMSSW configuration: KMuons_cff.py

Changes in Kappa 2:
- 

### Basic Tau {#obj-basictau}

The basic taus is a meta class and can not be used for skimming?
The KBasicTau contains information about the taus (both particle and anti-particle) as reconstructed by the CMS detector.

- **data format**: KTau (KTaus, KTauInfos); KBasicTau (KBasicTaus)
  - source format:
    [reco::Tau](https://github.com/cms-sw/cmssw/blob/CMSSW_7_3_X/DataFormats/Muon/interface/Muon.h "CMSSW")
  - Wiki:
    [Tau POG](),
    [TauID](),

- **producers**: KTauProducer, KBasicTauProducer
  - producer name (active): Muons
  - default configuration: KTuple_cff.py > Muons
  - required CMSSW packages: *none*
  - required CMSSW configuration: KMuons_cff.py

Changes in Kappa 2:
- 

### LeptonPair {#obj-leptonpair}

Contains quantites that are defined per lepton pair. The matching between the pair and the leptons is done via `leptonPair.hashLepton<[1|2]> == lepton.getHash()`.


Jets and Missing Energy {#obj-jetmet}
=====================================

Jet {#obj-pfjets}
---------------------------------

- **data format**: KJet (KJets, KMuonInfos)
  - source format:
    [reco::Muon](https://github.com/cms-sw/cmssw/blob/CMSSW_7_3_X/DataFormats/Muon/interface/Muon.h "CMSSW")
  - Wiki:
    [Jet/MET POG]()


- **producers**: KMuonProducer
  - producer name (active): Muons
  - default configuration: KTuple_cff.py > Muons
  - required CMSSW packages: *none*
  - required CMSSW configuration: KMuons_cff.py

Changes in Kappa 2:
- remove redundant energy fractions (...)

### Basic jets {#obj-taggedjets}

Basic jets have a reduced content compared to jets ... but can add an arbitrary
number of binary and float value tags to the data format.
As there are many jets per event, the default jet format is small and
this tagged jet format can be used if needed.

- **dataformat**
  - source format:
  - Wiki:
    [Jet ID](),
    [Pile-up jet ID](),
    [B-tag](),
    [Gluon tag](https://twiki.cern.ch/twiki/bin/viewauth/CMS/GluonTag "CMS Twiki")

- **producers**: KJetProducer
  - producer name (active): TaggedJets
  - default configuration: KTuple_cff.py > TaggedJets
  - required CMSSW packages: *none*
  - required CMSSW configuration: KMuons_cff.py

Calorimeter Jet {#obj-calojets}
--------------------------------

- **data format**: KMuon (KMuons, KMuonInfos)
  - source format:
    [reco::Muon](https://github.com/cms-sw/cmssw/blob/CMSSW_7_3_X/DataFormats/Muon/interface/Muon.h "CMSSW")
  - Wiki:
    [Muon POG](),
    [MuonID](),

- **producers**: KMuonProducer
  - producer name (active): Muons
  - default configuration: KTuple_cff.py > Muons
  - required CMSSW packages: *none*
  - required CMSSW configuration: KMuons_cff.py

Changes in Kappa 2:
- 


Generator Jets {#obj-genjets}
-----------------------------

Generator jets can be skimmed as [KLVs](#obj-klv) or [KParticles](#obj-particle).

MET {#obj-met}
--------------

Changes in Kappa 2:
- renamed from PFMET to MET
- new names of transverse energy fractions following CMSSW

### Basic MET {#obj-basicmet}

For skimming of a non-PF MET (GenMET, CaloMET) with fewer members, this class
can be used.

Changes in Kappa 2:
- renamed from MET to BasicMET

Jet Area {#obj-jetarea}
-----------------------


Particles and Candidates {#obj-particle}
========================================

Particles have an ID indicating the particle type and a status.
These can be used for generator particles, generator jets, PF candidates
and any other particle if the particle type is the only relevant
quantity.

**Particle ID**:
The identity of the particle following the Monte-Carlo numbering
scheme of the Particle Data Group (PDG) taken from the
[PDG Monte-Carlo Numbering Scheme 2014](http://pdg.lbl.gov/2014/reviews/rpp2014-rev-monte-carlo-numbering.pdf "Particle Data Group").
Anti-particles have a negative sign.

Some frequent examples:
Quarks: u (1), d (2), s (3), c (3), b (5), t (6);
Leptons: electron/positron (±11), muon (±13), tau (±15);
Bosons: gluon (21), photon (22), Z (23), W (±24), H (25).

**Charge**:
The electronic charge \f$q\f$ of the particle is calculated from the particle ID.
The current implementations is valid for quarks, leptons, bosons,
diquarks, mesons and baryons. It returns wrong results without further
warning for special, technicolor, SUSY, Kaluza-Klein particles,
R-hadrons and pentaquarks as given by the PDG.
This can be added to the code.

For integer comparisons there is a function chargeTimesThree which
returns \f$3 \cdot q\f$, i.e. 2 for an up-quark and -3 for an electron.
It has the same limitations for exotic particles as the charge function.

**Status**:
The status indicates whether a particle is generated by the hard
process or produced in decays or parton showers.
The status information is read form the `reco::GenParticle` and follows
the conventions in
[CMSSW](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookGenParticleCandidate#GenPCand)
which in turn takes the status information from the generators with
some modification (e.g. status 3 for Herwig++).

**Note**: In general, you can not rely on status codes, except for status 1!

The status codes are defined in the 
[HepMC2 User Manual](http://lcgapp.cern.ch/project/simu/HepMC/20400/HepMC2_user_manual.pdf)
and 
[HepMC2](http://lcgapp.cern.ch/project/simu/HepMC/205/status.html)
but not all generators follow these conventions:

 status    | HepMC definition    | usage in generators  |
 --------: | :------------------ | :------------------- |
 <b>0</b>  | an empty entry, with no meaningful information and therefore to be skipped unconditionally | <b>Herwig++</b>: This is not used.<br/><b>other generators</b>: This also should not happen. |
 <b>1</b>  | a final-state particle, i.e. a particle that is not decayed further by the generator (may also include unstable particles that are to be decayed later, as part of the detector simulation). Such particles must always be labelled ‘1’. | <b>all generators</b>: This is used as defined. |
 <b>2</b>  | a decayed Standard Model hadron or tau or mu lepton, excepting virtual intermediate states thereof (i.e. the particle must undergo a normal decay, not e.g. a shower branching). Such particles must always be labelled ‘2’. No other particles can be labelled ‘2’. | <b>Pythia6</b>: an entry which has decayed or fragmented and is therefore not appearing in the final state, but is retained for event history information.<br/><b>Sherpa</b>: unstable particles (physical particle decaying inside Sherpa)<br/><b>Herwig++</b>: This is used. |
 <b>3</b>  | a documentation entry (defined separately from the event history) | <b>Pythia6</b>: identifes the "hard part" of the interaction, i.e. the partons that are used in the matrix element calculation, including immediate decays of resonances. (“This could include the two incoming reacting particles, etc.”)<br/><b>Herwig++</b>: This is not used.<br/><b>Sherpa</b>: particle associated with the hard interaction, ie. matrix element | 
 <b>4</b>  | an incoming beam particle | <b>Pythia6</b>: undefined, but reserved for future standards (following older HEP standards).<br/><b>Herwig++</b>: This is used.<br/><b>Sherpa</b>: Used as defined. |
 <b>11 – 200</b> | an intermediate (decayed/branched/...) particle that does not fulfill the criteria of status code 2, with a generator-dependent classification of its nature | <b>Pythia6</b>: at the disposal of each model builder for constructs specific to his program, but equivalent to a null line in the context of any other program. <br><b>Herwig++</b>: Currently all particles that are not 1, 2 or 4 have status 11. This is not guaranteed in future.<br/><b>Sherpa</b>: status 11 for documentation particle (not necessarily physical), e.g. particles from the parton shower, intermediate states, helper particles, etc. |
 <b>201+</b>     | | <b>Pythia6</b>: at the disposal of users, in particular for event tracking in the detector. |

Kappa currently stores the status codes 0 – 3.
Further non-standard status codes can be saved as custom bits but they
differ for various generators and can therefore not be used in the
analysis in a unified way: 

- [Pythia 6](http://cepa.fnal.gov/psm/simulation/mcgen/lund/pythia_manual/pythia6.3/pythia6301/node39.html)
- [Pythia 8](http://home.thep.lu.se/~torbjorn/pythia81html/ParticleProperties.html),
- [Herwig 6](http://webber.home.cern.ch/webber/hw65_manual.html#htoc96),
- [Herwig++](https://herwig.hepforge.org/trac/wiki/FaQs#WhichHepMCstatuscodesareusedWhatdotheymean),
- Powheg ?
- [Sherpa](https://sherpa.hepforge.org/trac/ticket/262)
- Madgraph ?

*Whishlist*: Convert status codes from all generators to HepMC standard. We need: 0,1,2, ME level, incoming (4), 11, other


Generator Particles {#obj-genparticle}
--------------------------------------

### Generator Photon {#obj-genphoton}

### Generator Taus {#obj-gentau}

Particle Flow Candidate {#obj-pfcand}
-------------------------------------

Trigger Objects {#obj-triggerobjects}
-------------------------------------

General Infos and Event Summaries {#obj-summaries}
==============================================

Lumi Info {#obj-lumiinfo}
----------------------------

### Generator lumi info {#obj-genlumiinfo}

Event Info {#obj-eventinfo}
------------------------------

### Generator event info {#obj-geneventinfo}

### Data event info {#obj-dataeventinfo}

HCAL Noise Summary {#obj-noisesum}
----------------------------------

Filter Summary {#obj-filtersum}
-------------------------------

Track Summary {#obj-tracksum}
-----------------------------

Vertex Summary {#obj-verticesum}
--------------------------------



________________________________________________________________________________
This file is written in [Markdown].

[KIT]:      http://www.ekp.kit.edu "Institut für Experimentelle Kernphysik"
[code]:     https://ekptrac.physik.uni-karlsruhe.de/trac/Kappa "Trac on ekptrac"
[CMSSW]:    https://github.com/cms-sw/cmssw "CMSSW on github"
[CMS Wiki]: https://twiki.cern.ch/twiki/bin/viewauth/CMS/WebHome "CMS twiki"
[Workbook]: https://twiki.cern.ch/twiki/bin/viewauth/CMS/OnlineWB "CMS Workbook"
[Doxygen]:  http://www.stack.nl/~dimitri/doxygen/index.html "Doxygen"
[Markdown]: http://daringfireball.net/projects/markdown "Markdown"




