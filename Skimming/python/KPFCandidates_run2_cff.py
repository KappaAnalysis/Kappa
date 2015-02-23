import FWCore.ParameterSet.Config as cms

from Kappa.Skimming.KPFCandidates_cff import *

# Modifications for new particleFlow Pointers

pfPileUp.PFCandidates = cms.InputTag("particleFlowPtrs")
pfPileUpIso.PFCandidates = cms.InputTag("particleFlowPtrs")
pfNoPileUp.bottomCollection = cms.InputTag("particleFlowPtrs")
pfNoPileUpIso.bottomCollection = cms.InputTag("particleFlowPtrs")
pfJetTracksAssociatorAtVertex.jets= cms.InputTag("ak5PFJets")

