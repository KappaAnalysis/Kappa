import FWCore.ParameterSet.Config as cms

# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
	'file:///storage/6/zeise/temp/DYToMuMu_M-20_TuneZ2_7TeV-pythia6_Spring11_E7TeV_FlatDist10_2011EarlyData_50ns_START311_V1G1-v1_AODSIM_FABE0348-5442-E011-AF4D-E41F13180D14.root',
))
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000) )
#-------------------------------------------------------------------------------

# Includes + Global Tag --------------------------------------------------------
process.load("FWCore/MessageService/MessageLogger_cfi")
process.load('Configuration/StandardSequences/Services_cff')
process.load('Configuration/StandardSequences/MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Geometry_cff')
process.load('Configuration/StandardSequences/GeometryPilot2_cff')
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi")
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi")
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi")
process.load("RecoMuon.DetLayers.muonDetLayerGeometry_cfi")
#process.load('RecoJets/Configuration/RecoJetAssociations_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.GlobalTag.globaltag = '@GLOBALTAG@'
#-------------------------------------------------------------------------------

# Reduce amount of messages ----------------------------------------------------
process.MessageLogger.default = cms.untracked.PSet(ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5)))
process.MessageLogger.cerr.FwkReport.reportEvery = 42
#-------------------------------------------------------------------------------

# Produce jets -----------------------------------------------------------------
process.load('Configuration/StandardSequences/Generator_cff')
process.load('Configuration/StandardSequences/GeometryPilot2_cff')
process.load('RecoJets.JetProducers.ak5GenJets_cfi')
process.ak7GenJets = process.ak5GenJets.clone( rParam = 0.7 )
process.MoreJets = cms.Path(process.genParticlesForJets * process.ak5GenJets * process.ak7GenJets)
#-------------------------------------------------------------------------------

# Produce PF muon isolation ----------------------------------------------------
from PhysicsTools.PFCandProducer.Isolation.tools_cfi import *
process.pfmuIsoDepositPFCandidates = isoDepositReplace("muons", "particleFlow")
process.pfMuonIsolCandidates = cms.Path(process.pfmuIsoDepositPFCandidates)
#-------------------------------------------------------------------------------

# Produce rho distribution------------------------------------------------------
process.load('RecoJets.JetProducers.kt4PFJets_cfi')
process.kt6PFJetsRho = process.kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
process.kt6PFJetsRho.Rho_EtaMax = cms.double(5.)
process.JetArea = cms.Path(process.kt6PFJetsRho)
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
			srcExtender = cms.InputTag("ak5JetExtender"),
			srcJetID = cms.InputTag("ak5JetID"),
		),
		AK7CaloJets = cms.PSet(
			src = cms.InputTag("ak7CaloJets"),
			srcExtender = cms.InputTag("ak7JetExtender"),
			srcJetID = cms.InputTag("ak7JetID"),
		),
		#IC5CaloJets = cms.PSet(
		#	src = cms.InputTag("iterativeCone5CaloJets"),
		#	srcExtender = cms.InputTag("iterativeCone5JetExtender"),
		#	srcJetID = cms.InputTag("ic5JetID"),
		#),
		KT4CaloJets = cms.PSet(
			src = cms.InputTag("kt4CaloJets"),
			srcExtender = cms.InputTag("kt4JetExtender"),
			srcJetID = cms.InputTag("kt4JetID")
		),
		KT6CaloJets = cms.PSet(
			src = cms.InputTag("kt6CaloJets"),
			srcExtender = cms.InputTag(""),
			srcJetID = cms.InputTag("kt6JetID")
		),
	)
)
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(
	'Muons', 'TrackSummary', 'LV', 'MET', 'PFMET', 'CaloJets', 'PFJets', 'Vertex', 'BeamSpot', 'GenMetadata', 'Partons', 'CaloTaus', 'PFTaus', 'GenTaus', 'JetArea', @ACTIVE@
)
#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
#process.pathDAT = cms.Path(process.recoJetAssociations+process.kappatuple)
process.pathDAT = cms.Path(process.kappatuple)
process.schedule = cms.Schedule(process.JetArea, process.MoreJets, process.pfMuonIsolCandidates, process.pathDAT)
#-------------------------------------------------------------------------------
