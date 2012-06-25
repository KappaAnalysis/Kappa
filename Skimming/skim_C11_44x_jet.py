import FWCore.ParameterSet.Config as cms

# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
	'file:///portal/ekpcms5/home/test.root',
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

# Produce rho distribution------------------------------------------------------
process.load('RecoJets.JetProducers.ak5PFJets_cfi')
process.load('RecoJets.JetProducers.ak5CaloJets_cfi')
process.load('RecoJets.JetProducers.kt4PFJets_cfi')
process.load('RecoJets.JetProducers.kt4CaloJets_cfi')

process.ak5PFJets.doAreaFastjet = cms.bool(True)
process.ak7PFJets = process.ak5PFJets.clone( rParam = 0.7, doAreaFastjet = True )

process.kt4PFJets.doAreaFastjet = cms.bool(True)
process.kt6PFJets = process.kt4PFJets.clone( rParam = 0.6, doAreaFastjet = True  )

process.kt6PFJetsRho = process.kt6PFJets.clone( doRhoFastjet = True )

process.JetArea = cms.Path(process.kt6PFJetsRho +
	process.ak5PFJets + process.ak7PFJets + process.kt4PFJets + process.kt6PFJets
)
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
	CaloJets = cms.PSet(
		process.kappaNoCut,
		process.kappaNoRegEx,
		srcNoiseHCAL = cms.InputTag(""),
		AK5CaloJets = cms.PSet(
			src = cms.InputTag("ak5CaloJets"),
			srcJetID = cms.InputTag("ak5JetID"),
		),
		AK7CaloJets = cms.PSet(
			src = cms.InputTag("ak7CaloJets"),
			srcJetID = cms.InputTag("ak7JetID"),
		),
		KT4CaloJets = cms.PSet(
			src = cms.InputTag("kt4CaloJets"),
			srcJetID = cms.InputTag("kt4JetID")
		),
		KT6CaloJets = cms.PSet(
			src = cms.InputTag("kt6CaloJets"),
			srcJetID = cms.InputTag("kt6JetID")
		),
	)
)

process.kappatuple.PFJets.whitelist = cms.vstring("recoPFJets_.*Jet.*_kappaSkim")

process.kappatuple.verbose = cms.int32(0)
# 'CaloJets', 'MET', 
process.kappatuple.active = cms.vstring('@METADATA@',
	'TriggerObjects2', 'TrackSummary', 'VertexSummary', 'PFMET', 'PFJets', 'JetArea'
)

process.kappatuple.Metadata.hltWhitelist = cms.vstring(
	"^HLT_Jet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
	"^HLT_DiJetAve[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
	"^HLT_HT[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
)
process.kappatuple.Metadata.hltBlacklist = cms.vstring()

#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
process.pathDAT = cms.Path(process.kappatuple)
process.schedule = cms.Schedule(process.JetArea, process.pathDAT)
#-------------------------------------------------------------------------------
process.options = cms.untracked.PSet(
	SkipEvent = cms.untracked.vstring('ProductNotFound')
)
