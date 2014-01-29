import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## POG recommended MVA based electron Id:
##  - aus electronPOC twiki. Zugriff siehe HTauTau2ElecAnalysis53x.cc, z1778.
##  - Arbeitet auf pat electron level, nicht auf gsfElectron
from EgammaAnalysis.ElectronTools.electronIdMVAProducer_cfi import *

electronIdMVA = cms.Sequence(
	mvaTrigV0+
	mvaTrigNoIPV0+
	mvaNonTrigV0
	)
makeKappaElectrons = cms.Sequence( electronIdMVA )

## ------------------------------------------------------------------------
## PAT electorn configuration
##  - electron Id sources
##  - switch generator matches off
from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import *
from PhysicsTools.PatAlgos.producersLayer1.electronProducer_cfi import *

patElectrons.electronIDSources = cms.PSet(
	## default cut based Id
	eidRobustLoose      = cms.InputTag("eidRobustLoose"     ),
	eidRobustTight      = cms.InputTag("eidRobustTight"     ),
	eidLoose            = cms.InputTag("eidLoose"           ),
	eidTight            = cms.InputTag("eidTight"           ),
	eidRobustHighEnergy = cms.InputTag("eidRobustHighEnergy"),
	## MVA based Id
	mvaTrigV0           = cms.InputTag("mvaTrigV0"          ),
	mvaTrigNoIPV0       = cms.InputTag("mvaTrigNoIPV0"      ),
	mvaNonTrigV0        = cms.InputTag("mvaNonTrigV0"       ),
)

patElectrons.addGenMatch      = False
patElectrons.embedGenMatch    = False
patElectrons.genParticleMatch = ""

makeKappaElectrons *= cms.Sequence( patElectrons )


## ------------------------------------------------------------------------
# create pfNoPileup and pfPileupIso collections for deltaBeta corrected isolation

from CommonTools.ParticleFlow.pfParticleSelection_cff import *

pfPileUpIso.PFCandidates = 'particleFlow'
pfNoPileUpIso.bottomCollection='particleFlow'

# import filters and name them with clear scheme
from CommonTools.ParticleFlow.ParticleSelectors.pfSortByType_cff import *

pfNoPileUpChargedHadrons	= pfAllChargedHadrons.clone()
pfNoPileUpNeutralHadrons	= pfAllNeutralHadrons.clone()
pfNoPileUpPhotons 			= pfAllPhotons.clone()
pfPileUpChargedHadrons		= pfAllChargedHadrons.clone(src = cms.InputTag("pfPileUpIso") )


SequenceForDeltaBeta = cms.Sequence(
	pfNoPileUpChargedHadrons *
	pfNoPileUpNeutralHadrons *
	pfNoPileUpPhotons *
	pfPileUpChargedHadrons
	)

makeKappaElectrons *= cms.Sequence( pfParticleSelectionSequence * SequenceForDeltaBeta )
