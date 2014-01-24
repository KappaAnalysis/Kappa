import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## Create good primary vertices to be used for PF association
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
from RecoJets.JetProducers.ak5PFJets_cfi import ak5PFJets

goodOfflinePrimaryVertices = cms.EDFilter("PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices')
)

ak5PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')


## CHS Jets with the NoPU sequence
from CommonTools.ParticleFlow.PFBRECO_cff import *
pfPileUp.Vertices = cms.InputTag('goodOfflinePrimaryVertices')
pfPileUp.checkClosestZVertex = cms.bool(False)
ak5PFJetsCHS = ak5PFJets.clone( src = cms.InputTag('pfNoPileUp') )


## ------------------------------------------------------------------------
## Build basic sequences
makePfCHS = cms.Sequence(
    goodOfflinePrimaryVertices *
    PFBRECO
    )

makePFJets = cms.Sequence(
    ak5PFJets
    )

makePFJetsCHS = cms.Sequence(
    ak5PFJetsCHS
    )
