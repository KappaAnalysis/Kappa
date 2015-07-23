#-# Copyright (c) 2015 - All Rights Reserved

import FWCore.ParameterSet.Config as cms

import CondCore.DBCommon.CondDBCommon_cfi
from CondCore.DBCommon.CondDBSetup_cfi import *
jec = cms.ESSource("PoolDBESSource",
      DBParameters = cms.PSet(
        messageLevel = cms.untracked.int32(0)
        ),
      timetype = cms.string('runnumber'),
      toGet = cms.VPSet(
      cms.PSet(
            record = cms.string('JetCorrectionsRecord'),
            tag    = cms.string('JetCorrectorParametersCollection_Summer15_V5_MC_AK4PF'),
            label  = cms.untracked.string('AK4PF')
            )
      ## here you add as many jet types as you need
      ## note that the tag name is specific for the particular sqlite file 
      ),
      connect = cms.string('sqlite:Summer15_V5_MC.db')
)
## add an es_prefer statement to resolve a possible conflict from simultaneous connection to a global tag
es_prefer_jec = cms.ESPrefer('PoolDBESSource','jec')
