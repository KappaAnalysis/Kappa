#-# Copyright (c) 2014 - All Rights Reserved
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>
#-#   Stefan Wayand <stefan.wayand@gmail.com>
#-#   Thomas Mueller <tmuller@cern.ch>
#-#   Yasmin Anstruther <yasmin.anstruther@kit.edu>

## ------------------------------------------------------------------------
# Central cmsRun config file to be used with grid-control
# Settings are stored ordered on physics objects
# Object-related settings should be done in designated python configs
# if possible, run2 configs import the run1 configs and add some extra information
## ------------------------------------------------------------------------

# Kappa test: CMSSW 7.6.3, 8.0.20
# Kappa test: scram arch slc6_amd64_gcc493, slc6_amd64_gcc530
# Kappa test: checkout script scripts/checkoutCmssw76xPackagesForSkimming.py, scripts/checkoutCmssw80xPackagesForSkimming.py
# Kappa test: output kappaTuple.root
import sys
if not hasattr(sys, 'argv'):
	sys.argv = ["cmsRun", "runFrameworkMC.py"]

import os
import FWCore.ParameterSet.Config as cms
from  Kappa.Skimming.datasetsHelperTwopz import datasetsHelperTwopz
datasetsHelper = datasetsHelperTwopz(os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/datasets.json"))
import Kappa.Skimming.tools as tools

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('python')
options.register('globalTag', '76X_mcRun2_asymptotic_RunIIFall15DR76_v1', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'GlobalTag')
options.register('kappaTag', 'KAPPA_2_0_0', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'KappaTag')
options.register('nickname', 'SUSYGluGluToHToTauTauM160_RunIIFall15MiniAODv2_PU25nsData2015v1_13TeV_MINIAOD_pythia8', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Dataset Nickname')
options.register('testfile', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Path for a testfile')
options.register('maxevents', -1, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'maxevents. -1 for all events. Default: -1')
options.register('outputfilename', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Filename for the Outputfile')
options.register('testsuite', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'Run the Kappa test suite. Default: True')
options.register('preselect', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'apply preselection at CMSSW level on leptons. Never preselect on SM Higgs samples')
options.register('dumpPython', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'write cmsRun config to dumpPython.py')
options.parseArguments()

def getBaseConfig( globaltag= 'START70_V7::All',
	testfile=cms.untracked.vstring(""),
	maxevents=50,
	nickname = 'SUSYGluGluToHToTauTauM160_RunIIFall15MiniAODv2_PU25nsData2015v1_13TeV_MINIAOD_pythia8',
	kappaTag = 'Kappa_2_0_0',
	outputfilename = ''):

	from Kappa.Skimming.KSkimming_template_cfg import process
	## ------------------------------------------------------------------------

	# count number of events before doing anything else
	process.p *= process.nEventsTotal
	process.p *= process.nNegEventsTotal

	muons = "slimmedMuons"
	electrons = "slimmedElectrons"

	# new tau id only available for 8_0_20 (I believe) and above
	if tools.is_above_cmssw_version([8,0,20]):
		taus = "NewTauIDsEmbedded"
	else:
		taus = "slimmedTaus"
	isSignal = datasetsHelper.isSignal(nickname)

	# produce selected collections and filter events with not even one Lepton
	if options.preselect and not isSignal:
		from Kappa.Skimming.KSkimming_preselection import do_preselection

		do_preselection(process)
		process.p *= process.goodEventFilter

		process.selectedKappaTaus.cut = cms.string('pt > 15 && abs(eta) < 2.5')
		process.selectedKappaMuons.cut = cms.string('pt > 8 && abs(eta) < 2.6')
		process.selectedKappaElectrons.cut = cms.string('pt > 8 && abs(eta) < 2.7')
		muons = "selectedKappaMuons"
		electrons = "selectedKappaElectrons"
		taus = "selectedKappaTaus"
		process.goodEventFilter.minNumber = cms.uint32(2)

	## ------------------------------------------------------------------------

	# possibility to write out edmDump. Be careful when using unsceduled mode
	process.load("Kappa.Skimming.edmOut")
	process.ep = cms.EndPath()
	#process.ep *= process.edmOut

	## ------------------------------------------------------------------------

	# Configure Kappa
	if testfile:
		process.source.fileNames      = testfile
	else:
		process.source 			  = cms.Source('PoolSource', fileNames=cms.untracked.vstring())
	process.maxEvents.input	      = maxevents
	process.kappaTuple.verbose    = cms.int32(0)
	# uncomment the following option to select only running on certain luminosity blocks. Use only for debugging
	# in this example 1 - is run and after semicolon - the LumiSection
	# process.source.lumisToProcess  = cms.untracked.VLuminosityBlockRange("1:62090-1:63091")
	#process.source.eventsToProcess = cms.untracked.VEventRange('1:917:1719279', '1:1022:1915188')
	#process.source.skipEvents = cms.untracked.uint32(539)

	process.kappaTuple.profile    = cms.bool(True)
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag   = globaltag
		print "GT (overwritten):", process.GlobalTag.globaltag
	## ------------------------------------------------------------------------

	# Configure Metadata describing the file
	# Important to be evaluated correctly for the following steps
	# data, isEmbedded, miniaod, process.kappaTuple.TreeInfo.parameters = datasetsHelper.getTreeInfo(nickname, globaltag, kappaTag)
	process.kappaTuple.active = cms.vstring('TreeInfo')

	data = datasetsHelper.isData(nickname)
	isEmbedded = datasetsHelper.isEmbedded(nickname)
	print "nicknane:", nickname

	#####miniaod = datasetsHelper.isMiniaod(nickname) not used anymore, since everything is MiniAOD now
	process.kappaTuple.TreeInfo.parameters= datasetsHelper.getTreeInfo(nickname, globaltag, kappaTag)

	## ------------------------------------------------------------------------

	# General configuration
	if tools.is_above_cmssw_version([7,4]):
		process.kappaTuple.Info.pileUpInfoSource = cms.InputTag("slimmedAddPileupInfo")

	# save primary vertex
	process.kappaTuple.active += cms.vstring('VertexSummary') # save VertexSummary

	process.load("Kappa.Skimming.KVertices_cff")
	process.goodOfflinePrimaryVertices.src = cms.InputTag('offlineSlimmedPrimaryVertices')
	process.p *= ( process.makeVertexes )

	process.kappaTuple.VertexSummary.whitelist = cms.vstring('offlineSlimmedPrimaryVertices')  # save VertexSummary
	process.kappaTuple.VertexSummary.rename = cms.vstring('offlineSlimmedPrimaryVertices => goodOfflinePrimaryVerticesSummary')

	if tools.is_above_cmssw_version([7,6]):
		process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("offlineSlimmedPrimaryVertices"))

	process.kappaTuple.active += cms.vstring('TriggerObjectStandalone')

	# setup BadPFMuonFilter and BadChargedCandidateFilter
	if tools.is_above_cmssw_version([8]) and not tools.is_above_cmssw_version([9]):
		process.load('RecoMET.METFilters.BadPFMuonFilter_cfi')
		process.BadPFMuonFilter.muons = cms.InputTag("slimmedMuons")
		process.BadPFMuonFilter.PFCandidates = cms.InputTag("packedPFCandidates")
		process.BadPFMuonFilter.taggingMode = cms.bool(True)

		process.load('RecoMET.METFilters.BadChargedCandidateFilter_cfi')
		process.BadChargedCandidateFilter.muons = cms.InputTag("slimmedMuons")
		process.BadChargedCandidateFilter.PFCandidates = cms.InputTag("packedPFCandidates")
		process.BadChargedCandidateFilter.taggingMode = cms.bool(True)

		# in reMiniAOD data these filters are already present; only need to run the dedicated module for MC and older data
		if not "03Feb2017" in str(process.kappaTuple.TreeInfo.parameters.scenario):
			process.load('RecoMET.METFilters.badGlobalMuonTaggersMiniAOD_cff')
			#switch on tagging mode:
			process.badGlobalMuonTaggerMAOD.taggingMode = cms.bool(True)
			process.cloneGlobalMuonTaggerMAOD.taggingMode = cms.bool(True)

			process.kappaTuple.TriggerObjectStandalone.metfilterbitslist = cms.vstring("BadChargedCandidateFilter", "BadPFMuonFilter", "badGlobalMuonTaggerMAOD", "cloneGlobalMuonTaggerMAOD")
		else:
			process.kappaTuple.TriggerObjectStandalone.metfilterbitslist = cms.vstring("BadChargedCandidateFilter","BadPFMuonFilter")

	process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")
	if isEmbedded:
		process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "SIMembedding")
		process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "SIMembedding")
	elif data:
		if tools.is_above_cmssw_version([9]):
			process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")
			#process.kappaTuple.TriggerObjectStandalone.bits = cms.InputTag("TriggerResults", "", "RECO")
		elif "03Feb2017" in str(process.kappaTuple.TreeInfo.parameters.scenario):
			process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "PAT")
		else:
			process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "RECO")
			process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "RECO")
	if not isEmbedded and "Spring16" in str(process.kappaTuple.TreeInfo.parameters.campaign):
		# adds for each HLT Trigger wich contains "Tau" or "tau" in the name a Filter object named "l1extratauccolltection"
		process.kappaTuple.TriggerObjectStandalone.l1extratauJetSource = cms.untracked.InputTag("l1extraParticles","IsoTau","RECO")

	# 80X doesn't have 'slimmedPatTrigger' -> use 'selectedPatTrigger' instead
	if tools.is_above_cmssw_version([8,0]):
		process.kappaTuple.TriggerObjectStandalone.triggerObjects = cms.PSet( src = cms.InputTag("selectedPatTrigger"))
		process.kappaTuple.TriggerObjectStandalone.bits = cms.InputTag("TriggerResults", "", "HLT")

	process.kappaTuple.active += cms.vstring('BeamSpot')
	if tools.is_above_cmssw_version([7,6]):
		process.kappaTuple.BeamSpot.offlineBeamSpot = cms.PSet(src = cms.InputTag("offlineBeamSpot"))

	if not isEmbedded and data:
		process.kappaTuple.active+= cms.vstring('DataInfo')          # produce Metadata for data,

	if not isEmbedded and not data:
		process.kappaTuple.active+= cms.vstring('GenInfo')           # produce Metadata for MC,
		process.kappaTuple.active+= cms.vstring('GenParticles')      # save GenParticles,
		process.kappaTuple.active+= cms.vstring('GenTaus')           # save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")
		process.kappaTuple.GenTaus.genTaus.src = cms.InputTag("prunedGenParticles")

		process.kappaTuple.Info.lheSource = cms.InputTag("externalLHEProducer")
		process.kappaTuple.Info.lheWeightNames = cms.vstring(".*")

		if any([pattern in nickname for pattern in ["HToTauTau", "H2JetsToTauTau", "DY", "LFV"]]):
			process.kappaTuple.active += cms.vstring("LHE")
			process.kappaTuple.LHE.whitelist = cms.vstring("source")
			process.kappaTuple.LHE.rename = cms.vstring("source => LHEafter")
			if tools.is_above_cmssw_version([7, 6]):
				process.kappaTuple.LHE.LHEafter = cms.PSet(src=cms.InputTag("externalLHEProducer"))

	# save Flag
	process.kappaTuple.Info.isEmbedded = cms.bool(isEmbedded)

	if isEmbedded:
		#process.load('RecoBTag/Configuration/RecoBTag_cff')
		#process.load('RecoJets/JetAssociationProducers/ak5JTA_cff')
		#process.ak5PFJetNewTracksAssociatorAtVertex.tracks = "tmfTracks"
		#process.ak5PFCHSNewJetTracksAssociatorAtVertex.tracks = "tmfTracks"
		#process.p *= process.btagging
		# disable overrideHLTCheck for embedded samples, since it triggers an Kappa error
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)
		process.kappaTuple.active += cms.vstring('GenInfo')
		process.kappaTuple.active += cms.vstring('GenParticles') # save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")
		process.kappaTuple.active += cms.vstring('GenTaus')
		process.kappaTuple.GenTaus.genTaus.src = cms.InputTag("prunedGenParticles")

		#process.kappaTuple.active += cms.vstring('GenTaus') # save GenParticles,
		#process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("genParticles","","EmbeddedRECO")

	## ------------------------------------------------------------------------

	# Trigger
	from Kappa.Skimming.hlt_run2 import hltBlacklist, hltWhitelist
	process.kappaTuple.Info.hltWhitelist = hltWhitelist
	process.kappaTuple.Info.hltBlacklist = hltBlacklist

	## ------------------------------------------------------------------------

	# should not be the default, it blows up the skim a lot
	#process.kappaTuple.active += cms.vstring('packedPFCandidates')
	#process.kappaTuple.packedPFCandidates.packedPFCandidates = cms.PSet(src = cms.InputTag("packedPFCandidates"))

	jetCollectionPuppi = "slimmedJetsPuppi"
	if tools.is_above_cmssw_version([9]):
		jetCollection = "slimmedJets"
	elif tools.is_above_cmssw_version([8]):
		from RecoMET.METPUSubtraction.jet_recorrections import recorrectJets
		#from RecoMET.METPUSubtraction.jet_recorrections import loadLocalSqlite
		#loadLocalSqlite(process, sqliteFilename = "Spring16_25nsV6_DATA.db" if data else "Spring16_25nsV6_MC.db",
		#                         tag = 'JetCorrectorParametersCollection_Spring16_25nsV6_DATA_AK4PF' if data else 'JetCorrectorParametersCollection_Spring16_25nsV6_MC_AK4PF')
		recorrectJets(process, isData=data)
		jetCollection = "patJetsReapplyJEC"
	else:
		from RecoMET.METPUSubtraction.localSqlite import recorrectJets
		recorrectJets(process, isData=data)
		jetCollection = "patJetsReapplyJEC"

	## ------------------------------------------------------------------------

	# Configure Muons
	process.load("Kappa.Skimming.KMuons_miniAOD_cff")
	process.kappaTuple.Muons.muons.src = cms.InputTag(muons)
	process.kappaTuple.Muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Muons.srcMuonIsolationPF = cms.InputTag("")
	process.kappaTuple.Muons.use03ConeForPfIso = cms.bool(True)
	process.kappaTuple.Muons.doPfIsolation = cms.bool(False)
	for src in [ "muPFIsoDepositCharged", "muPFIsoDepositChargedAll", "muPFIsoDepositNeutral", "muPFIsoDepositGamma", "muPFIsoDepositPU"]:
		setattr(getattr(process, src), "src", cms.InputTag(muons))

	process.kappaTuple.active += cms.vstring('Muons')
	process.kappaTuple.Muons.noPropagation = cms.bool(True)
	process.p *= ( process.makeKappaMuons )

	## ------------------------------------------------------------------------

	# Configure Electrons
	process.kappaTuple.active += cms.vstring('Electrons')
	process.load("Kappa.Skimming.KElectrons_miniAOD_cff")
	process.kappaTuple.Electrons.electrons.src = cms.InputTag("slimmedElectrons")
	process.kappaTuple.Electrons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Electrons.rhoIsoInputTag = cms.InputTag("slimmedJets", "rho")
	process.kappaTuple.Electrons.allConversions = cms.InputTag("reducedEgamma", "reducedConversions")
	from Kappa.Skimming.KElectrons_miniAOD_cff import setupElectrons
	process.kappaTuple.Electrons.srcIds = cms.string("standalone")

	if tools.is_above_cmssw_version([8]):
		process.kappaTuple.Electrons.ids = cms.vstring(
			"egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-veto",
			"egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-loose",
			"egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-medium",
			"egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-tight",
			"electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring16GeneralPurposeV1Values"
			)
	else:
		process.kappaTuple.Electrons.ids = cms.vstring(
			"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-veto",
			"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-loose",
			"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-medium",
			"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-tight",
			"electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values"
			)

	setupElectrons(process, electrons)
	process.p *= (process.makeKappaElectrons)

	## ------------------------------------------------------------------------

	# new tau id only available for 8_0_20 (I believe) and above
	if tools.is_above_cmssw_version([8,0,20]):
		process.load('RecoTauTag.Configuration.loadRecoTauTagMVAsFromPrepDB_cfi')
		process.load("Kappa.Skimming.KPatTaus_run2_cff")
		process.p *= ( process.makeKappaTaus )

		# embed new id's into new tau collection
		embedID = cms.EDProducer("PATTauIDEmbedder",
			src = cms.InputTag('slimmedTaus'),
			tauIDSources = cms.PSet(
				rerunDiscriminationByIsolationMVAOldDMrun2v1raw = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1raw'),
				rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose'),
				rerunDiscriminationByIsolationMVAOldDMrun2v1Loose = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1Loose'),
				rerunDiscriminationByIsolationMVAOldDMrun2v1Medium = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1Medium'),
				rerunDiscriminationByIsolationMVAOldDMrun2v1Tight = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1Tight'),
				rerunDiscriminationByIsolationMVAOldDMrun2v1VTight = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1VTight'),
				rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight'),
				rerunDiscriminationByIsolationMVANewDMrun2v1raw = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1raw'),
				rerunDiscriminationByIsolationMVANewDMrun2v1VLoose = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1VLoose'),
				rerunDiscriminationByIsolationMVANewDMrun2v1Loose = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1Loose'),
				rerunDiscriminationByIsolationMVANewDMrun2v1Medium = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1Medium'),
				rerunDiscriminationByIsolationMVANewDMrun2v1Tight = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1Tight'),
				rerunDiscriminationByIsolationMVANewDMrun2v1VTight = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1VTight'),
				rerunDiscriminationByIsolationMVANewDMrun2v1VVTight = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1VVTight')
			),
		)
		setattr(process, taus, embedID)
		process.p *= getattr(process, taus)

	process.kappaTuple.active += cms.vstring('PatTaus')
	process.kappaTuple.PatTaus.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.PatTaus.offlineBeamSpot = cms.InputTag("offlineBeamSpot")
	process.kappaTuple.PatTaus.taus.binaryDiscrBlacklist = cms.vstring()
	process.kappaTuple.PatTaus.taus.src = cms.InputTag(taus)
	process.kappaTuple.PatTaus.taus.floatDiscrBlacklist = cms.vstring()
	# just took everything from https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendation13TeV
	process.kappaTuple.PatTaus.taus.preselectOnDiscriminators = cms.vstring ()
	process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist = cms.vstring(
		"decayModeFinding",
		"decayModeFindingNewDMs",
		"byLooseCombinedIsolationDeltaBetaCorr3Hits",
		"byMediumCombinedIsolationDeltaBetaCorr3Hits",
		"byTightCombinedIsolationDeltaBetaCorr3Hits",
		"byCombinedIsolationDeltaBetaCorrRaw3Hits",
		"chargedIsoPtSum",
		"neutralIsoPtSum",
		"neutralIsoPtSumWeight",
		"puCorrPtSum",
		"footprintCorrection",
		"photonPtSumOutsideSignalCone",
		"byIsolationMVArun2v1DBoldDMwLTraw",
		"byVLooseIsolationMVArun2v1DBoldDMwLT",
		"byLooseIsolationMVArun2v1DBoldDMwLT",
		"byMediumIsolationMVArun2v1DBoldDMwLT",
		"byTightIsolationMVArun2v1DBoldDMwLT",
		"byVTightIsolationMVArun2v1DBoldDMwLT",
		"byVVTightIsolationMVArun2v1DBoldDMwLT",
		#"byIsolationMVArun2v1DBnewDMwLTraw",
		#"byVLooseIsolationMVArun2v1DBnewDMwLT",
		#"byLooseIsolationMVArun2v1DBnewDMwLT",
		#"byMediumIsolationMVArun2v1DBnewDMwLT",
		#"byTightIsolationMVArun2v1DBnewDMwLT",
		#"byVTightIsolationMVArun2v1DBnewDMwLT",
		#"byVVTightIsolationMVArun2v1DBnewDMwLT",
		"againstMuonLoose3",
		"againstMuonTight3",
		"againstElectronMVA6category",
		"againstElectronMVA6raw",
		"againstElectronVLooseMVA6",
		"againstElectronLooseMVA6",
		"againstElectronMediumMVA6",
		"againstElectronTightMVA6",
		"againstElectronVTightMVA6"#,
		#"chargedIsoPtSumdR03",
		#"neutralIsoPtSumdR03",
		#"neutralIsoPtSumWeightdR03",
		#"footprintCorrectiondR03",
		#"photonPtSumOutsideSignalConedR03",
		#"byLooseCombinedIsolationDeltaBetaCorr3HitsdR03",
		#"byMediumCombinedIsolationDeltaBetaCorr3HitsdR03",
		#"byTightCombinedIsolationDeltaBetaCorr3HitsdR03",
		#"byIsolationMVArun2v1DBdR03oldDMwLTraw",
		#"byVLooseIsolationMVArun2v1DBdR03oldDMwLT",
		#"byLooseIsolationMVArun2v1DBdR03oldDMwLT",
		#"byMediumIsolationMVArun2v1DBdR03oldDMwLT",
		#"byTightIsolationMVArun2v1DBdR03oldDMwLT",
		#"byVTightIsolationMVArun2v1DBdR03oldDMwLT",
		#"byVVTightIsolationMVArun2v1DBdR03oldDMwLT",
		)
	if tools.is_above_cmssw_version([8,0,20]):
		process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist += cms.vstring(
			"rerunDiscriminationByIsolationMVAOldDMrun2v1raw",
			"rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose",
			"rerunDiscriminationByIsolationMVAOldDMrun2v1Loose",
			"rerunDiscriminationByIsolationMVAOldDMrun2v1Medium",
			"rerunDiscriminationByIsolationMVAOldDMrun2v1Tight",
			"rerunDiscriminationByIsolationMVAOldDMrun2v1VTight",
			"rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight",
			"rerunDiscriminationByIsolationMVANewDMrun2v1raw",
			"rerunDiscriminationByIsolationMVANewDMrun2v1VLoose",
			"rerunDiscriminationByIsolationMVANewDMrun2v1Loose",
			"rerunDiscriminationByIsolationMVANewDMrun2v1Medium",
			"rerunDiscriminationByIsolationMVANewDMrun2v1Tight",
			"rerunDiscriminationByIsolationMVANewDMrun2v1VTight",
			"rerunDiscriminationByIsolationMVANewDMrun2v1VVTight"
			)
	## now also possible to save all MVA isolation inputs for taus # turn of per default

	process.kappaTuple.PatTaus.taus.extrafloatDiscrlist = cms.untracked.vstring(
		"decayDistX",
		"decayDistY",
		"decayDistZ",
		"decayDistM",
		"nPhoton",
		"ptWeightedDetaStrip",
		"ptWeightedDphiStrip",
		"ptWeightedDrSignal",
		"ptWeightedDrIsolation",
		"leadingTrackChi2",
		"eRatio"
		)

	process.kappaTuple.PatTaus.taus.floatDiscrWhitelist = process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist
	process.kappaTuple.PatTaus.verbose = cms.int32(1)

	## ------------------------------------------------------------------------

	## Configure Jets
	process.kappaTuple.active += cms.vstring('PileupDensity')
	process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
	process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")
	if tools.is_above_cmssw_version([7,6]):
		process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAll"))
	process.kappaTuple.active += cms.vstring('PatJets')
	if tools.is_above_cmssw_version([7,6]):
		process.kappaTuple.PatJets.ak4PF = cms.PSet(src=cms.InputTag(jetCollection))
		process.kappaTuple.PatJets.puppiJets = cms.PSet(src=cms.InputTag(jetCollectionPuppi))

	## Refitted Vertices collection
	if not tools.is_above_cmssw_version([9]):
		process.kappaTuple.active += cms.vstring('RefitVertex')
		process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
		process.load("VertexRefit.TauRefit.AdvancedRefitVertexProducer_cfi")

		if tools.is_above_cmssw_version([7,6]) and not tools.is_above_cmssw_version([9]):
			process.AdvancedRefitVertexBSProducer.srcElectrons = cms.InputTag(electrons)
			process.AdvancedRefitVertexBSProducer.srcMuons = cms.InputTag(muons)
			process.AdvancedRefitVertexBSProducer.srcTaus = cms.InputTag(taus)
			process.AdvancedRefitVertexBSProducer.srcLeptons = cms.VInputTag(electrons, muons, taus)
			process.p *= (process.AdvancedRefitVertexBS)

		process.AdvancedRefitVertexNoBSProducer.srcElectrons = cms.InputTag(electrons)
		process.AdvancedRefitVertexNoBSProducer.srcMuons = cms.InputTag(muons)
		process.AdvancedRefitVertexNoBSProducer.srcTaus = cms.InputTag(taus)
		process.AdvancedRefitVertexNoBSProducer.srcLeptons = cms.VInputTag(electrons, muons, taus)
		process.p *= (process.AdvancedRefitVertexNoBS)

		process.kappaTuple.RefitVertex.whitelist = cms.vstring('AdvancedRefitVertexBS', 'AdvancedRefitVertexNoBS')

		if tools.is_above_cmssw_version([7,6]) and not tools.is_above_cmssw_version([9]):
			process.kappaTuple.RefitVertex.AdvancedRefittedVerticesBS = cms.PSet(src=cms.InputTag("AdvancedRefitVertexBSProducer"))
			process.AdvancedRefitVertexBSProducer.srcElectrons = cms.InputTag(electrons)
			process.AdvancedRefitVertexBSProducer.srcMuons = cms.InputTag(muons)
			process.AdvancedRefitVertexBSProducer.srcTaus = cms.InputTag(taus)
			process.AdvancedRefitVertexBSProducer.srcLeptons = cms.VInputTag(electrons, muons, taus)

		if tools.is_above_cmssw_version([7,6]):
			process.kappaTuple.RefitVertex.AdvancedRefittedVerticesNoBS = cms.PSet(src=cms.InputTag("AdvancedRefitVertexNoBSProducer"))
			process.AdvancedRefitVertexNoBSProducer.srcElectrons = cms.InputTag(electrons)
			process.AdvancedRefitVertexNoBSProducer.srcMuons = cms.InputTag(muons)
			process.AdvancedRefitVertexNoBSProducer.srcTaus = cms.InputTag(taus)
			process.AdvancedRefitVertexNoBSProducer.srcLeptons = cms.VInputTag(electrons, muons, taus)

	## calculate IP info wrt refitted PV
	process.kappaTuple.Electrons.refitvertexcollection = cms.InputTag("AdvancedRefitVertexNoBSProducer")
	process.kappaTuple.Muons.refitvertexcollection = cms.InputTag("AdvancedRefitVertexNoBSProducer")
	process.kappaTuple.PatTaus.refitvertexcollection = cms.InputTag("AdvancedRefitVertexNoBSProducer")

	## Standard MET and GenMet from pat::MET
	process.kappaTuple.active += cms.vstring('PatMET')
	process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag("slimmedMETs"))
	if tools.is_above_cmssw_version([9]):
		pass
	elif tools.is_above_cmssw_version([8,0,14]):
		from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
		runMetCorAndUncFromMiniAOD(process, isData=data  )
		process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag("slimmedMETs", "", "KAPPA"))

	#process.kappaTuple.PatMET.pfmetT1 = cms.PSet(src=cms.InputTag("patpfMETT1"))
	process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"))

	if not tools.is_above_cmssw_version([9]):
		## Write MVA MET to KMETs
		process.kappaTuple.active += cms.vstring('PatMETs')
		# new MVA MET
		from RecoMET.METPUSubtraction.MVAMETConfiguration_cff import runMVAMET
		runMVAMET( process, jetCollectionPF = jetCollection)
		process.kappaTuple.PatMETs.MVAMET = cms.PSet(src=cms.InputTag("MVAMET", "MVAMET"))
		process.MVAMET.srcLeptons  = cms.VInputTag(muons, electrons, taus) # to produce all possible combinations
		process.MVAMET.requireOS = cms.bool(False)
		if tools.is_above_cmssw_version([8,0]) and isEmbedded:
			process.MVAMET.srcMETs = cms.VInputTag(
				cms.InputTag("slimmedMETs", "", "MERGE"),
				cms.InputTag("patpfTrackMET"),
				cms.InputTag("patpfNoPUMET"),
				cms.InputTag("patpfPUCorrectedMET"),
				cms.InputTag("patpfPUMET"),
				cms.InputTag("slimmedMETsPuppi", "", "MERGE")
				)

	## ------------------------------------------------------------------------

	## GenJets
	if not data or isEmbedded:
		process.load('PhysicsTools/JetMCAlgos/TauGenJets_cfi')
		process.load('PhysicsTools/JetMCAlgos/TauGenJetsDecayModeSelectorAllHadrons_cfi')
		process.tauGenJets.GenParticles = cms.InputTag("prunedGenParticles")
		process.p *= (
			process.tauGenJets +
			process.tauGenJetsSelectorAllHadrons
			)
		if isSignal:
			process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets", "slimmedGenJets")
		else:
			process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets")
		process.kappaTuple.active += cms.vstring('GenJets')
		if tools.is_above_cmssw_version([7,6]):
			if isSignal:
				process.kappaTuple.GenJets.genJets = cms.PSet(src=cms.InputTag("slimmedGenJets"))
			process.kappaTuple.GenJets.tauGenJets = cms.PSet(src=cms.InputTag("tauGenJets"))
			process.kappaTuple.GenJets.tauGenJetsSelectorAllHadrons = cms.PSet(src=cms.InputTag("tauGenJetsSelectorAllHadrons"))

	# add repository revisions to TreeInfo
	for repo, rev in tools.get_repository_revisions().iteritems():
		setattr(process.kappaTuple.TreeInfo.parameters, repo, cms.string(rev))

	## ------------------------------------------------------------------------

	## Count Events after running all filters
	if not data:
		process.nEventsTotal.isMC = cms.bool(True)
		process.nNegEventsTotal.isMC = cms.bool(True)
		process.nEventsFiltered.isMC = cms.bool(True)
		process.nNegEventsFiltered.isMC = cms.bool(True)

	process.p *= process.nEventsFiltered
	process.p *= process.nNegEventsFiltered
	process.kappaTuple.active += cms.vstring('FilterSummary')

	## ------------------------------------------------------------------------

	## if needed adapt output filename
	process.ep *= process.kappaOut
	if outputfilename != '':
		process.kappaTuple.outputFile = cms.string('%s'%outputfilename)

	## ------------------------------------------------------------------------

	## Further information saved to Kappa output
	if options.dumpPython:
		f = open("dumpPython.py", "w")
		f.write(process.dumpPython())
		f.close()

	# add python config to TreeInfo
	process.kappaTuple.TreeInfo.parameters.config = cms.string(process.dumpPython())

	return process

if __name__ == "__main__" or __name__ == "kSkimming_run2_cfg":

	# test with user-defined input file
	if options.testfile:
		print 'read from testfile '+str(options.testfile)
		process = getBaseConfig(
			globaltag=options.globalTag,
			nickname=options.nickname,
			kappaTag=options.kappaTag,
			testfile=cms.untracked.vstring("%s"%options.testfile),
			maxevents=options.maxevents,
			outputfilename=options.outputfilename
			)

	# CRAB job-submission
	elif options.outputfilename:
		process = getBaseConfig(
			globaltag=options.globalTag,
			nickname=options.nickname,
			kappaTag=options.kappaTag,
			maxevents=options.maxevents,
			outputfilename=options.outputfilename
			)

	# GC job-submission?
	elif  str("@NICK@")[0] != '@':
		process = getBaseConfig(
			globaltag="@GLOBALTAG@",
			nickname="@NICK@",
			outputfilename="kappaTuple.root"
			)

	# Kappa test suite (cmsRun with NO extra options)
	else:
		testPaths = ['/storage/b/fs6-mirror/fcolombo/kappatest/input', '/nfs/dust/cms/user/fcolombo/kappatest/input', '/home/short']
		testPath = [p for p in testPaths if os.path.exists(p)][0]
		if tools.is_above_cmssw_version([8]):
			process = getBaseConfig(
				globaltag="80X_mcRun2_asymptotic_2016_v3",
				testfile=cms.untracked.vstring("file:%s/"%testPath + (testPath == '/home/short')*"short_" + "SUSYGluGluToHToTauTau_M-160_spring16_miniAOD.root"),
				nickname='SUSYGluGluToHToTauTauM160_RunIISpring16MiniAODv1_PUSpring16_13TeV_MINIAOD_pythia8',
				outputfilename="kappaTuple.root"
				)
		else:
			process = getBaseConfig(
				globaltag=options.globalTag,
				testfile=cms.untracked.vstring("file:%s/"%testPath + (testPath == '/home/short')*"short_" + "SUSYGluGluToHToTauTau_M-160_fall15_miniAOD.root"),
				outputfilename="kappaTuple.root"
				)
