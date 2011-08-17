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
process.load('Configuration.StandardSequences.Geometry_cff')
process.load('Configuration/StandardSequences/GeometryPilot2_cff')
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi")
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi")
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi")
process.load("RecoMuon.DetLayers.muonDetLayerGeometry_cfi")
#process.load('RecoJets.Configuration.RecoJetAssociations_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.GlobalTag.globaltag = '@GLOBALTAG@' #'GR10_P_V10::All'
#-------------------------------------------------------------------------------

# Reduce amount of messages ----------------------------------------------------
process.MessageLogger.default = cms.untracked.PSet(ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5)))
process.MessageLogger.cerr.FwkReport.reportEvery = 42
#-------------------------------------------------------------------------------

# Produce PF muon isolation ----------------------------------------------------
from CommonTools.ParticleFlow.Isolation.tools_cfi import *
process.pfmuIsoDepositPFCandidates = isoDepositReplace("muons", "particleFlow")
process.pfMuonIsolCandidates = cms.Path(process.pfmuIsoDepositPFCandidates)
#-------------------------------------------------------------------------------

# Produce rho distribution------------------------------------------------------
process.load('RecoJets.JetProducers.kt4PFJets_cfi')
process.kt6PFJetsRho = process.kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
process.kt6PFJetsRho.Rho_EtaMax = cms.double(5.)
process.JetArea = cms.Path(process.kt6PFJetsRho)
#-------------------------------------------------------------------------------

# Require one good muon --------------------------------------------------------
process.goodMuons = cms.EDFilter("CandViewSelector",
        src = cms.InputTag("muons"),
        cut = cms.string("pt > 5 & abs( eta ) < 2.5 & isGlobalMuon() & isTrackerMuon()"),
)

process.oneGoodMuon = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("goodMuons"),
    minNumber = cms.uint32(@MINMUONS@),
)
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(
	'L1Muons', 'Muons', 'TrackSummary', 'TriggerObjects', 'VertexSummary', 'BeamSpot', 'JetArea', @ACTIVE@ #'Tracks'
)
process.kappatuple.Tracks.minPt = cms.double(5.)

process.kappatuple.Metadata.hltWhitelist = cms.vstring(
	"^HLT_(Jet)[0-9]+U(_v[[:digit:]]+)?$",
	"^HLT_(Jet)[0-9]+(_v[[:digit:]]+)?$",
	"^HLT_(L[123])?(Iso|Double|Triple)?Mu([0-9]+)",
	"^HLT_DoubleMu([0-9]+)_Acoplanarity([0-9]+)(_v[[:digit:]]+)?$",
)

process.kappatuple.Metadata.hltBlacklist = cms.vstring(
	"Ele([0-9]+)",
	"Photon([0-9]+)",
	"CentralJet([0-9]+)",
	"HT([0-9]+)",
	"CaloId",
)

#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
#process.pathDAT = cms.Path(process.recoJetAssociations+process.kappatuple)
process.pathDAT = cms.Path(process.goodMuons*process.oneGoodMuon*process.kappatuple)
process.schedule = cms.Schedule(process.JetArea, process.pfMuonIsolCandidates, process.pathDAT)
#-------------------------------------------------------------------------------
