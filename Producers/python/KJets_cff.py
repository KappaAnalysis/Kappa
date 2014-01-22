import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## Create good primary vertices to be used for PF association
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
from RecoJets.JetProducers.ak5PFJets_cfi import ak5PFJets
from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
from RecoHI.HiJetAlgos.HiRecoPFJets_cff import ak7PFJets, kt6PFJets

goodOfflinePrimaryVertices = cms.EDFilter("PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices')
)

ak5PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
ak7PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
kt4PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
kt6PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')


## Add Cambridge/Aachen algorithm
ca8PFJets = ak5PFJets.clone(
    jetAlgorithm = cms.string('CambridgeAachen'),
    rParam = cms.double(0.8)
)


## CHS Jets with the NoPU sequence
from CommonTools.ParticleFlow.PFBRECO_cff import *
pfPileUp.Vertices = cms.InputTag('goodOfflinePrimaryVertices')
pfPileUp.checkClosestZVertex = cms.bool(False)
ak5PFJetsCHS = ak5PFJets.clone( src = cms.InputTag('pfNoPileUp') )
ak7PFJetsCHS = ak7PFJets.clone( src = cms.InputTag('pfNoPileUp') )
kt4PFJetsCHS = kt4PFJets.clone( src = cms.InputTag('pfNoPileUp') )
kt6PFJetsCHS = kt6PFJets.clone( src = cms.InputTag('pfNoPileUp') )
ca8PFJetsCHS = ca8PFJets.clone( src = cms.InputTag('pfNoPileUp') )


## Gen Jets without neutrinos
from RecoJets.JetProducers.ak5GenJets_cfi import *
ca8GenJets     = ca4GenJets.clone( rParam = cms.double(0.8) )
ca8GenJetsNoNu = ca8GenJets.clone( src = cms.InputTag("genParticlesForJetsNoNu") )


## ------------------------------------------------------------------------
## Build basic sequences
makePfCHS = cms.Sequence(
    goodOfflinePrimaryVertices *
    PFBRECO
    )

makePFJets = cms.Sequence(
    ak5PFJets *
    ak7PFJets *
    kt4PFJets *
    kt6PFJets *
    ca8PFJets
    )

makePFJetsCHS = cms.Sequence(
    ak5PFJetsCHS *
    ak7PFJetsCHS *
    kt4PFJetsCHS *
    kt6PFJetsCHS *
    ca8PFJetsCHS
    )

makeNoNuGenJets = cms.Sequence(
    genParticlesForJetsNoNu *
    genParticlesForJets *
    ak5GenJetsNoNu *
    ak7GenJetsNoNu *
    kt4GenJetsNoNu *
    kt4GenJets *
    kt6GenJetsNoNu *
    kt6GenJets *
    ca8GenJetsNoNu *
    ca8GenJets
    )