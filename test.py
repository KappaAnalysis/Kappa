import FWCore.ParameterSet.Config as cms

process = cms.Process("kappaSkim")

process.load('Configuration/StandardSequences/Services_cff')
process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10) )
process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring('file:///work/ws/bd105/CMSSW_Samples/Summer09_Flat_TEST.root')
)

# Configure tuple generation
process.load("Kappa.Producers.KTuple_cff")

process.load('RecoJets/Configuration/GenJetParticles_cff')

process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('RecoJets.JetAssociationProducers.ak5JTA_cff')
process.load('RecoJets.JetAssociationProducers.ak7JTA_cff') 
process.load('RecoJets.JetAssociationProducers.iterativeCone5JTA_cff') 
process.load('RecoJets.JetAssociationProducers.sisCone5JTA_cff') 
process.load('RecoJets.JetAssociationProducers.kt4JTA_cff') 
process.JetExtender = cms.Sequence(process.ak5JTA+process.ak7JTA+process.iterativeCone5JTA+process.sisCone5JTA+process.kt4JTA)

process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string("skim.root"),
	CaloJets = cms.PSet(
		srcNoiseHCAL = cms.InputTag("hcalnoise"),
		maxN = cms.int32(-1),
		minPt = cms.double(-1),
		maxEta = cms.double(-1),
		AK5CaloJets = cms.PSet(
			src = cms.InputTag("ak5CaloJets"),
			srcExtender = cms.InputTag("ak5JetExtender"),
			srcJetID = cms.InputTag("ak5JetID"),
		),
	)
)
process.kappatuple.verbose = cms.int32(10)
process.kappatuple.active = cms.vstring("Metadata", "LVs", "MET", "Tracks", "Tower", "CaloJets")

process.pathDAT = cms.Path(process.kappatuple)
process.schedule = cms.Schedule(process.pathDAT)
