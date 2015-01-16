import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## Good offline PV selection: 
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector

goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
    src = cms.InputTag('offlinePrimaryVertices'),
    filterParams = pvSelector.clone( minNdof = 4.0, maxZ = 24.0 ),
)

goodOfflinePrimaryVertexEvents = cms.EDFilter("KVertexFilter",
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(999999),
    src = cms.InputTag("goodOfflinePrimaryVertices")
)

## ------------------------------------------------------------------------
## TopProjections from CommonTools/ParticleFlow:
from CommonTools.ParticleFlow.PFBRECO_cff import *

## pf candidate configuration for everything but CHS jets
pfPileUpIso.PFCandidates        = 'particleFlow'
pfPileUpIso.Vertices            = 'goodOfflinePrimaryVertices'
pfPileUpIso.checkClosestZVertex = True
pfNoPileUpIso.bottomCollection  = 'particleFlow'

## pf candidate configuration for deltaBeta corrections for muons and electrons 
pfNoPileUpChargedHadrons        = pfAllChargedHadrons.clone()
pfNoPileUpNeutralHadrons        = pfAllNeutralHadrons.clone()
pfNoPileUpPhotons 	        = pfAllPhotons.clone()
pfPileUpChargedHadrons	        = pfAllChargedHadrons.clone(src = 'pfPileUpIso')

## pf candidate configuration for CHS jets
pfPileUp.Vertices               = 'goodOfflinePrimaryVertices'
pfPileUp.checkClosestZVertex    = False

## ------------------------------------------------------------------------
## Definition of sequences

## run this to produce only those pf candidate collections that should go
## into the KappaTuple and nothing more
makeKappaPFCandidates = cms.Sequence(
    goodOfflinePrimaryVertices *
    goodOfflinePrimaryVertexEvents *
    pfParticleSelectionSequence
    )

## run this to run the full PFBRECO sequence, which is needed e.g. for CHS
## jets ()
makePFBRECO = cms.Sequence(
    goodOfflinePrimaryVertices *
    goodOfflinePrimaryVertexEvents *
    PFBRECO
    )

## run this to produce the particle flow collections that are expected to
## be present for deltaBeta corrections for muons and electrons. This needs
## at least makeKappaPFCandidates to be run beforehand
makePFCandidatesForDeltaBeta = cms.Sequence(
	pfNoPileUpChargedHadrons *
	pfNoPileUpNeutralHadrons *
	pfNoPileUpPhotons *
	pfPileUpChargedHadrons
	)
