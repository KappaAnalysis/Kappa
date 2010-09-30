import FWCore.ParameterSet.Config as cms

# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration/StandardSequences/Services_cff')
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
	'file:///work/ws/bd105/CMSSW_Samples/PtJA/GEN-SIM-RECO/900_V8K_Z1_c85522a9-b01f-497d-b020-081566831f65.root',
))
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.verbose = cms.int32(10)
process.kappatuple.active = cms.vstring('GenMetadata', 'LV')
process.kappatuple.Metadata.l1Source = cms.InputTag("")
process.kappatuple.Metadata.hltSource = cms.InputTag("")
process.kappatuple.Metadata.noiseHCAL = cms.InputTag("")
process.kappatuple.Metadata.hlTrigger = cms.InputTag("")
process.kappatuple.Metadata.muonTriggerObjects = cms.vstring()
#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
process.pathDAT = cms.Path(process.kappatuple)
process.schedule = cms.Schedule(process.pathDAT)
#-------------------------------------------------------------------------------
