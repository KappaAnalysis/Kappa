#-# Copyright (c) 2014 - All Rights Reserved
#-#   Raphael Friese <Raphael.Friese@cern.ch>

import FWCore.ParameterSet.Config as cms

from SimGeneral.HepPDTESSource.pythiapdt_cfi import *


prunedGenParticles = cms.EDProducer("GenParticlePruner",
	src = cms.InputTag("genParticles", "", "SIM"),
	select = cms.vstring(
		"drop  *",
		"keep status == 3",                                      # all status 3
		"keep++ abs(pdgId) == 23",                               # Z
		"keep++ abs(pdgId) == 24",                               # W
		"keep++ abs(pdgId) == 25",                               # H
		"keep abs(pdgId) == 11 || abs(pdgId) == 13",             # charged leptons
		"keep++ abs(pdgId) == 15"                                # keep full tau decay chain
	)
)

