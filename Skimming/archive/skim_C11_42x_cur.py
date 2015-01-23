#-# Copyright (c) 2010 - All Rights Reserved
#-#   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
#-#   Fred Stober <stober@cern.ch>
#-#   Manuel Zeise <zeise@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>

import FWCore.ParameterSet.Config as cms

# Basic process setup ----------------------------------------------------------
process = cms.Process("kappaSkim")
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
	'file:///storage/4/stober/CMSSW_4_1_4/src/Kappa/Skimming/kostas_slimming_test.root',
))
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )
#-------------------------------------------------------------------------------

# Includes + Global Tag --------------------------------------------------------
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration/StandardSequences/Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Geometry_cff')
process.load('Configuration/StandardSequences/GeometryPilot2_cff')
#process.load('RecoJets.Configuration.RecoJetAssociations_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
if '@' in '@GLOBALTAG@':
	process.GlobalTag.globaltag = 'GR_R_42_V20::All'
else:
	process.GlobalTag.globaltag = '@GLOBALTAG@'
#-------------------------------------------------------------------------------

# Produce rho distribution------------------------------------------------------
process.load('RecoJets.JetProducers.kt4PFJets_cfi')
process.load('RecoJets.JetProducers.kt4CaloJets_cfi')
process.kt6PFJets = process.kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
process.kt6PFJets.doAreaFastjet = cms.bool(True)
process.kt6PFJets.doAreaFastjet = cms.bool(True)
process.JetArea = cms.Path(process.kt4PFJets, process.kt6PFJets, process.kt4CaloJets, process.kt6CaloJets)
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
	CaloJets = cms.PSet(
		process.kappaNoCut,
		process.kappaNoRegEx,
		# only with RECO: srcNoiseHCAL = cms.InputTag("hcalnoise"),
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

process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring(
	'TriggerObjects', 'DataMetadata'
)
process.kappatuple.Metadata.hltWhitelist = cms.vstring(
	"^HLT_(Jet|DiJetAve)[0-9]+(_v[[:digit:]]+)?$",
	"^HLT_(Jet|DiJetAve)[0-9]+U(_v[[:digit:]]+)?$",
)
process.kappatuple.TriggerObjects.triggerObjects = cms.vstring(
	# L1 objects
	"hltL1sL1SingleJet128",
	"hltL1sL1SingleJet16",
	"hltL1sL1SingleJet36",
	"hltL1sL1SingleJet52",
	"hltL1sL1SingleJet68",
	"hltL1sL1SingleJet92",

	# HLT jet collections
	"hltCaloJetCorrected",
	"hltCaloJetCorrectedRegional",
	"hltCaloJetCorrectedRegionalNoJetID",
	"hltJetIDPassedAK5Jets",
	"hltJetIDPassedCorrJets",
	"hltJetIDPassedJetsRegional",
	"hltL1MatchedJetsRegional",

	# Single jet objects
	"hltSingleJet30",
	"hltSingleJet60Regional",
	"hltSingleJet80Regional",
	"hltSingleJet110Regional",
	"hltSingleJet150Regional",
	"hltSingleJet190Regional",
	"hltSingleJet240Regional",
	"hltSingleJet300Regional",
	"hltSingleJet370Regional",
	"hltSingleJet370RegionalNoJetID",
	"hltSingleJet800Regional",

	# Dijet average objects
	"hltJetIDPassedAK5Jets",

	"hltDiJetAve15U",
	"hltDiJetAve30",
	"hltDiJetAve30U",
	"hltDiJetAve50U",
	"hltDiJetAve60",
	"hltDiJetAve70U",
	"hltDiJetAve80",
	"hltDiJetAve100U",
	"hltDiJetAve110",
	"hltDiJetAve140U",
	"hltDiJetAve150",
	"hltDiJetAve180U",
	"hltDiJetAve190",
	"hltDiJetAve240",
	"hltDiJetAve300",
	"hltDiJetAve300U",
	"hltDiJetAve370",
)

#-------------------------------------------------------------------------------

# Process schedule -------------------------------------------------------------
process.pathDAT = cms.Path(process.kappatuple)
process.schedule = cms.Schedule(process.pathDAT)
#-------------------------------------------------------------------------------
process.options = cms.untracked.PSet(
	SkipEvent = cms.untracked.vstring('ProductNotFound')
)
