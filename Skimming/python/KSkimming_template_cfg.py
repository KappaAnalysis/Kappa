#-# Copyright (c) 2014 - All Rights Reserved
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>

import FWCore.ParameterSet.Config as cms

process = cms.Process("KAPPA")

## MessageLogger
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.default = cms.untracked.PSet(
	ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5))
	#suppressError = cms.untracked.vstring("electronIdMVAProducer")
)

process.MessageLogger.cerr.FwkReport.reportEvery = 50

## Options and Output Report
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

## Source
process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring()
)
## Maximal number of Events
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

## Geometry and Detector Conditions (needed for a few patTuple production steps)
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")

from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = cms.string(autoCond['startup'])
# print the global tag until it is clear whether this auto global tag is fine
print "GT from autoCond:", process.GlobalTag.globaltag
process.load("Configuration.StandardSequences.MagneticField_cff")

## Kappa
process.load('Kappa.Producers.KTuple_cff')
process.kappaTuple = cms.EDAnalyzer('KTuple',
    process.kappaTupleDefaultsBlock,
    outputFile = cms.string("kappaTuple_template.root"),
)
process.kappaTuple.active = cms.vstring()
process.kappaOut = cms.Sequence(process.kappaTuple)
