import FWCore.ParameterSet.Config as cms

process = cms.Process("kappaSkim")

# Meta Config ------------------------------------------------------------------
filenames=['file:///home/piparo/testFiles/Spring10_MinBias_GENSIMRECO_MC_3XY_V25_S09_preproduction-v2.root']
max_evts=1000
root_filename = 'Ktuple_test.root'
active_KTuple_categories=['Metadata','Muons','Tracks','LV','Tower','MET','CaloJets']
#-------------------------------------------------------------------------------


process.load('Configuration/StandardSequences/Services_cff')
process.load("FWCore.MessageService.MessageLogger_cfi")

# Process source ---------------------------------------------------------------
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(max_evts) )
process.source = cms.Source("PoolSource",
                 fileNames = cms.untracked.vstring(filenames))
#-------------------------------------------------------------------------------

# Jet Extender -----------------------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")

process.load('RecoJets/Configuration/GenJetParticles_cff')

process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('RecoJets.JetAssociationProducers.ak5JTA_cff')
process.load('RecoJets.JetAssociationProducers.ak7JTA_cff') 
process.load('RecoJets.JetAssociationProducers.iterativeCone5JTA_cff') 
process.load('RecoJets.JetAssociationProducers.sisCone5JTA_cff') 
process.load('RecoJets.JetAssociationProducers.kt4JTA_cff') 
process.JetExtender = cms.Sequence(process.ak5JTA+
                                   process.ak7JTA+
                                   process.iterativeCone5JTA+
                                   process.sisCone5JTA+
                                   process.kt4JTA)
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string(root_filename),
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
		AK7CaloJets = cms.PSet(
			src = cms.InputTag("ak7CaloJets"),
			srcExtender = cms.InputTag("ak7JetExtender"),
			srcJetID = cms.InputTag("ak7JetID"),
		),
		IC5CaloJets = cms.PSet(
			src = cms.InputTag("iterativeCone5CaloJets"),
			srcExtender = cms.InputTag("iterativeCone5JetExtender"),
			srcJetID = cms.InputTag("ic5JetID"),
		),
		SC5CaloJets = cms.PSet(
			src = cms.InputTag("sisCone5CaloJets"),
			srcExtender = cms.InputTag("sisCone5JetExtender"),
			srcJetID = cms.InputTag("sc5JetID"),
		),
		KT4CaloJets = cms.PSet(
			src = cms.InputTag("kt4CaloJets"),
			srcExtender = cms.InputTag("kt4JetExtender"),
			srcJetID = cms.InputTag("kt4JetID")
		),
	
    )
)
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(active_KTuple_categories)

process.pathDAT = cms.Path(process.kappatuple)

# The schedule -----------------------------------------------------------------
process.schedule = cms.Schedule(process.pathDAT)
#-------------------------------------------------------------------------------
