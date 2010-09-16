filenames=['file:///tmp/tst.root']

# General parameters -----------------------------------------------------------
import FWCore.ParameterSet.Config as cms
process = cms.Process("kappaSkim")
process.load('Configuration/StandardSequences/Services_cff')
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Kappa.Producers.KTuple_cff")
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(filenames))
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.verbose = cms.int32(10)
process.kappatuple.active = cms.vstring('GenMetadata', 'Hits')
process.kappatuple.Metadata.l1Source = cms.InputTag("")
process.kappatuple.Metadata.hltSource = cms.InputTag("")
process.kappatuple.Metadata.noiseHCAL = cms.InputTag("")
process.kappatuple.Metadata.hlTrigger = cms.InputTag("")
process.kappatuple.Metadata.muonTriggerObjects = cms.vstring()
process.kappatuple.Metadata.noiseHCAL = cms.InputTag("")

process.pathDAT = cms.Path(process.kappatuple)

# The schedule -----------------------------------------------------------------
process.schedule = cms.Schedule(process.pathDAT)
#-------------------------------------------------------------------------------
