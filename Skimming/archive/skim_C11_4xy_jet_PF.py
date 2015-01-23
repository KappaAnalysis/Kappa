#-# Copyright (c) 2012 - All Rights Reserved
#-#   Fred Stober <stober@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>

import FWCore.ParameterSet.Config as cms

# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
	'file:///portal/ekpcms5/home/stober/TestFiles/2011A.PR6.root',
))
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
#-------------------------------------------------------------------------------

# Includes + Global Tag --------------------------------------------------------
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Geometry_cff')
process.load('Configuration.StandardSequences.GeometryPilot2_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.GlobalTag.globaltag = '@GLOBALTAG@'
#-------------------------------------------------------------------------------

# Produce jet collections with area and calculate rho distribution--------------
process.load('RecoJets.JetProducers.ak5PFJets_cfi')
process.load('RecoJets.JetProducers.kt4PFJets_cfi')

process.ak5PFJets.doAreaFastjet = cms.bool(True)
process.ak7PFJets = process.ak5PFJets.clone( rParam = 0.7, doAreaFastjet = True )

process.kt4PFJets.doAreaFastjet = cms.bool(True)
process.kt6PFJets = process.kt4PFJets.clone( rParam = 0.6, doAreaFastjet = True  )

process.kt6PFJetsRho = process.kt6PFJets.clone( doRhoFastjet = True )

process.pathJets = cms.Path(process.kt6PFJetsRho +
	process.ak5PFJets + process.ak7PFJets + process.kt4PFJets + process.kt6PFJets
)
#-------------------------------------------------------------------------------

# Produce CHS jet collections---------------------------------------------------
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter("PrimaryVertexObjectFilter",
	filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
	src = cms.InputTag('offlinePrimaryVertices')
)

process.load('CommonTools.ParticleFlow.pfNoPileUp_cff')
process.pfPileUp.Vertices = "goodOfflinePrimaryVertices"
process.pfPileUp.Enable = True
process.pathCHS = cms.Path( process.goodOfflinePrimaryVertices * process.pfNoPileUpSequence )

process.ak5PFJetsCHS = process.ak5PFJets.clone( src = cms.InputTag("pfNoPileUp") )
process.ak7PFJetsCHS = process.ak7PFJets.clone( src = cms.InputTag("pfNoPileUp") )
process.kt4PFJetsCHS = process.kt4PFJets.clone( src = cms.InputTag("pfNoPileUp") )
process.kt6PFJetsCHS = process.kt6PFJets.clone( src = cms.InputTag("pfNoPileUp") )

process.pathJetsCHS = cms.Path(
	process.ak5PFJetsCHS + process.ak7PFJetsCHS + process.kt4PFJetsCHS + process.kt6PFJetsCHS
)
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.PFJets.whitelist = cms.vstring("recoPFJets_.*Jet.*_kappaSkim")

process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(@ACTIVE@,
	'TriggerObjects2', 'TrackSummary', 'VertexSummary', 'PFMET', 'PFJets', 'JetArea', 'HCALNoiseSummary'
)

process.kappatuple.Metadata.hltWhitelist = cms.vstring(
	"^HLT_Jet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
	"^HLT_DiJetAve[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
	"^HLT_HT[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
)
process.kappatuple.Metadata.hltBlacklist = cms.vstring()
process.pathSkim = cms.Path(process.kappatuple)
#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
process.schedule = cms.Schedule(process.pathJets, process.pathCHS, process.pathJetsCHS, process.pathSkim)
process.options = cms.untracked.PSet(
	SkipEvent = cms.untracked.vstring('ProductNotFound')
)
#-------------------------------------------------------------------------------
