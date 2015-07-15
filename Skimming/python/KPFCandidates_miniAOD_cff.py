#-# Copyright (c) 2014 - All Rights Reserved
#-#   Fabio Colombo <fabio.colombo@cern.ch>

import FWCore.ParameterSet.Config as cms

# As done in:
# https://github.com/ajgilbert/ICHiggsTauTau/blob/master/test/miniaod_cfg_new_recipes.py#L171-L228
# The produced collections are needed as input for the computation of electron and muon iso

pfPileUp = cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("packedPFCandidates"),
	cut = cms.string("fromPV <= 1")
)
pfNoPileUp = cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("packedPFCandidates"),
	cut = cms.string("fromPV > 1")
)
pfAllNeutralHadrons = cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("pfNoPileUp"),
	cut = cms.string("abs(pdgId) = 111 | abs(pdgId) = 130 | " \
			 "abs(pdgId) = 310 | abs(pdgId) = 2112")
)
pfAllChargedHadrons= cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("pfNoPileUp"),
	cut = cms.string("abs(pdgId) = 211 | abs(pdgId) = 321 | " \
			 "abs(pdgId) = 999211 | abs(pdgId) = 2212")
)
pfAllPhotons= cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("pfNoPileUp"),
	cut = cms.string("abs(pdgId) = 22")
)
pfAllChargedParticles= cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("pfNoPileUp"),
	cut = cms.string("abs(pdgId) = 211 | abs(pdgId) = 321 | " \
			 "abs(pdgId) = 999211 | abs(pdgId) = 2212 | " \
			 "abs(pdgId) = 11 | abs(pdgId) = 13")
)
pfPileUpAllChargedParticles= cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("pfPileUp"),
	cut = cms.string("abs(pdgId) = 211 | abs(pdgId) = 321 | " \
			 "abs(pdgId) = 999211 | abs(pdgId) = 2212 | " \
			 "abs(pdgId) = 11 | abs(pdgId) = 13")
)


makeKappaPFCandidates = cms.Sequence(
	pfPileUp +
	pfNoPileUp +
	pfAllNeutralHadrons +
	pfAllChargedHadrons +
	pfAllPhotons +
	pfAllChargedParticles +
	pfPileUpAllChargedParticles
)
