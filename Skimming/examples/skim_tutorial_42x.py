# Copyright (c) 2012 - All Rights Reserved
#   Manuel Zeise <zeise@cern.ch>
#

import FWCore.ParameterSet.Config as cms

# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
	#'file:///home/piparo/testFiles/Spring10_MinBias_GENSIMRECO_MC_3XY_V25_S09_preproduction-v2.root',
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_823A80DA-307B-E011-833C-001E0BE922E2.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_08603AE6-3C7B-E011-9B6D-001E0B472C96.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_AEA1495E-377B-E011-A4BB-00237DA1DDE4.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_BC5B351E-377B-E011-98FB-001F296BE5FA.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_7A10D844-377B-E011-8F17-0017A4770420.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_3EA65A18-377B-E011-BB75-00237DA13C5A.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_44AF71CC-347B-E011-85BC-001E0B5FA4D8.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_0C61B312-3D7B-E011-B378-0017A4770C2C.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_06711488-3E7B-E011-B1C4-1CC1DE1CF1BA.root",
	"file:/storage/6/zeise/temp/SingleMu_Run2011A_AOD_May10ReReco-v1_6A4385DE-367B-E011-BE84-0017A4771028.root",
	#'file:///storage/6/zeise/temp/minbias_pr_v9_FE9B4520-7D5B-DF11-B4DA-0019DB2F3F9A.root'
))
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
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
process.kt6PFJetsRho = process.kt6PFJets.clone(rParam = 0.6, doAreaFastjet = True, doRhoFastjet = True )
process.JetArea = cms.Path(process.kt6PFJetsRho)
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(
#	'Muons', 'TrackSummary', 'PFMET', 'VertexSummary', 'BeamSpot', 'JetArea', 'DataMetadata'
	'Muons', 'TrackSummary', 'PFMET', 'VertexSummary', 'BeamSpot', 'JetArea', @ACTIVE@
)
process.kappatuple.Tracks.minPt = cms.double(5.)
process.kappatuple.JetArea.whitelist = cms.vstring("kt6PFJetsRho_rho")

process.kappatuple.Metadata.hltWhitelist = cms.vstring(
	"^HLT_(L[123])?(Iso|Double|Triple)?Mu([0-9]+)",
	"^HLT_DoubleMu([0-9]+)_Acoplanarity([0-9]+)(_v[[:digit:]]+)?$",
)

process.kappatuple.Metadata.hltBlacklist = cms.vstring(
	"Ele([0-9]+)",
	"Photon([0-9]+)",
	"Central(PF)?(PFNoPU)?Jet([0-9]+)",
	"HT([0-9]+)",
	"CaloId",
	"DiPFJet",
	"(PF)Tau",
	"Displaced",
	"L1ETM",
	"^HLT_Mu([0-9]+)(_eta2p1)?_R([0-9]+)_MR([0-9]+)(_v[[:digit:]]+)?$",
	"^HLT_Mu([0-9]+)(_eta2p1)?_L1Mu([0-9]+)erJetC12WdEtaPhi1DiJetsC.*$",
	"^HLT_L2DoubleMu([0-9]+)_NoVertex_2Cha_Angle2p5.*$",
	"^HLT_Mu([0-9]+)_RsqMR.*",
	"_NoVertex_NoBPTX3BX_NoHalo_",
	"^HLT_Mu([0-9]+)(_eta2p1)?_(Di|Tri)?Central_.*",
)

#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
#process.pathDAT = cms.Path(process.recoJetAssociations+process.kappatuple)
process.pathDAT = cms.Path(process.kappatuple)
process.schedule = cms.Schedule(process.JetArea, process.pfMuonIsolCandidates, process.pathDAT)
#-------------------------------------------------------------------------------
