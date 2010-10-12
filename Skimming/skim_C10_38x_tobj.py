import FWCore.ParameterSet.Config as cms

# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
	#'file:///home/piparo/testFiles/Spring10_MinBias_GENSIMRECO_MC_3XY_V25_S09_preproduction-v2.root',
	'file:///storage/6/zeise/temp/Mu_Run2010B-WZMu-v2_RAW-RECO_12C344DF-63CB-DF11-9C18-E0CB4E553640.root',
	#'file:///storage/6/zeise/temp/minbias_pr_v9_FE9B4520-7D5B-DF11-B4DA-0019DB2F3F9A.root'
))
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000) )
#-------------------------------------------------------------------------------

# Includes + Global Tag --------------------------------------------------------
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration/StandardSequences/Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
#process.load('RecoJets.Configuration.RecoJetAssociations_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = '@GLOBALTAG@' #'GR10_P_V10::All'
#-------------------------------------------------------------------------------

# Produce PF muon isolation ----------------------------------------------------
from PhysicsTools.PFCandProducer.Isolation.tools_cfi import *
process.pfmuIsoDepositPFCandidates = isoDepositReplace("muons", "particleFlow")
process.pfMuonIsolCandidates = cms.Path(process.pfmuIsoDepositPFCandidates)
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(
	'L1Muons', 'Muons', 'TrackSummary', 'TriggerObjects', 'Vertex', 'Metadata', 'BeamSpot', @ACTIVE@ #'Tracks'
)
process.kappatuple.Tracks.minPt = cms.double(5.)

#-------------------------------------------------------------------------------
triggerObjects = cms.vstring(
# HLT_Mu7
	"hltL1sL1SingleMu5",
	"hltL1SingleMu5L1Filtered0",
	"hltSingleMu7L2Filtered5",
	"hltSingleMu7L3Filtered7",
# HLT_Mu9
	"hltSingleMu9L3Filtered9",
# path HLT_Mu11
	"hltSingleMu11L3Filtered11",
# path HLT_Mu13_v1
	"hltSingleMu13L3Filtered13",
# HLT_Mu15_v1
	"hltSingleMu15L3Filtered15",
# HLT_IsoMu9
	"hltSingleMuIsoL3PreFiltered9",
	"hltSingleMuIsoL3IsoFiltered9",
# HLT_IsoMu11_v1
	"hltL1sL1SingleMu7",
	"hltL1SingleMu7L1Filtered0",
	"hltL2Mu7L2Filtered7",
	"hltSingleMuIsoL2IsoFiltered7",
	"hltSingleMuIsoL3PreFiltered11",
	"hltSingleMuIsoL3IsoFiltered11"
)

process.kappatuple.TriggerObjects.triggerObjects = triggerObjects
process.kappatuple.Metadata.muonTriggerObjects = triggerObjects

process.kappatuple.Metadata.hltWhitelist = cms.vstring(
			"^HLT_Jet*", "^HLT_LQuadJet*",
			"^HLT_Activity.*", ".*(Bias|BSC).*",
			"^HLT_L1Mu$",
			"^HLT_L2Mu[0-9]*",
			"^HLT_Mu[0-9]",
			"^HLT_IsoMu[0-9]$",
			"^HLT_DoubleMu[0-9]$"
)
#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
#process.pathDAT = cms.Path(process.recoJetAssociations+process.kappatuple)
process.pathDAT = cms.Path(process.kappatuple)
process.schedule = cms.Schedule(process.pfMuonIsolCandidates, process.pathDAT)
#-------------------------------------------------------------------------------
