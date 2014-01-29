import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## TopProjections from CommonTools/ParticleFlow only up to:
##  - pfNoPileUp (pfCandidates associated to PV of hard interaction) 
##  - pfPileUp (pfCandidates associated to PU)
##  - pfParticleSelection (categorization in charged, neutral, photon)
from CommonTools.ParticleFlow.pfParticleSelection_cff import *

pfPileUpIso.PFCandidates = 'particleFlow' 
pfNoPileUpIso.bottomCollection='particleFlow'

## ------------------------------------------------------------------------
## Definition of sequences
makeKappaPFCandidates = cms.Sequence(
    pfParticleSelectionSequence
    )
