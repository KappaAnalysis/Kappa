#-# Copyright (c) 2015 - All Rights Reserved
#-#   Fabio Colombo <fabio.colombo@cern.ch>

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools

from CommonTools.ParticleFlow.goodOfflinePrimaryVertices_cfi import goodOfflinePrimaryVertices
goodOfflinePrimaryVertices = goodOfflinePrimaryVertices.clone()

makeVertexes = cms.Sequence(
	goodOfflinePrimaryVertices
	)
