#-# Copyright (c) 2014 - All Rights Reserved
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools
cmssw_version_number = tools.get_cmssw_version_number()

process = cms.Process("KAPPA")

## MessageLogger
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.default = cms.untracked.PSet(
	ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5))
	#suppressError = cms.untracked.vstring("electronIdMVAProducer")
)

process.MessageLogger.cerr.FwkReport.reportEvery = 50

## Options and Output Report
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) ,
	allowUnscheduled = cms.untracked.bool(True) )

if (cmssw_version_number.startswith("5_3")):
	process.options.allowUnscheduled = cms.untracked.bool(False)

## Source
process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring()
)
## Maximal number of Events
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

## Geometry and Detector Conditions (needed for a few patTuple production steps)
if (cmssw_version_number.startswith("7_4") or cmssw_version_number.startswith("7_6")):
	# see https://twiki.cern.ch/twiki/bin/view/Sandbox/MyRootMakerFrom72XTo74X#DDVectorGetter_vectors_are_empty
	print "Use GeometryRecoDB and condDBv2"
	process.load("Configuration.Geometry.GeometryRecoDB_cff")
	process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')

else:
	process.load("Configuration.Geometry.GeometryIdeal_cff")
	process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")

# print the global tag until it is clear whether this auto global tag is fine
print "GT from autoCond:", process.GlobalTag.globaltag
process.load("Configuration.StandardSequences.MagneticField_cff")

## Kappa
from Kappa.Producers.KTuple_cff import kappaTupleDefaultsBlock
process.kappaTuple = cms.EDAnalyzer('KTuple',
	kappaTupleDefaultsBlock,
	outputFile = cms.string("kappaTuple.root"),
)
process.kappaTuple.active = cms.vstring()
process.kappaOut = cms.Sequence(process.kappaTuple)

process.p = cms.Path ()
process.load("Kappa.Producers.EventWeightCountProducer_cff")

