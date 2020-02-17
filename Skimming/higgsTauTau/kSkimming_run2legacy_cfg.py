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
import pprint
pp = pprint.PrettyPrinter(indent=4)

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools
from  Kappa.Skimming.datasetsHelperTwopz import datasetsHelperTwopz
datasetsHelper = datasetsHelperTwopz(os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/datasets.json"))

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('python')
options.register('globalTag', '102X_mc2017_realistic_v7', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'GlobalTag')
options.register('kappaTag', 'KAPPA_2_0_0', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'KappaTag')
options.register('nickname', 'VBFHToTauTauM125_RunIIFall17MiniAODv2_PU2017newpmx_13TeV_MINIAOD_powheg-pythia8', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Dataset Nickname')
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
	nickname = 'VBFHToTauTauM125_RunIIFall17MiniAODv2_PU2017newpmx_13TeV_MINIAOD_powheg-pythia8',
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
	# if tools.is_above_cmssw_version([8,0,20]):
	# 	taus = "NewTauIDsEmbedded"
	# else:
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
		process.source            = cms.Source('PoolSource', fileNames=cms.untracked.vstring(testfile))
		# uncomment the following option to select only running on certain luminosity blocks. Use only for debugging
		# in this example 1 - is run and after semicolon - the LumiSection
		# process.source.lumisToProcess  = cms.untracked.VLuminosityBlockRange("1:62090-1:63091")
		#process.source.eventsToProcess = cms.untracked.VEventRange('1:917:1719279', '1:1022:1915188')
		#process.source.skipEvents = cms.untracked.uint32(539)
	else:
		process.source 			  = cms.Source('PoolSource', fileNames=cms.untracked.vstring())
	process.maxEvents.input	      = maxevents
	process.kappaTuple.verbose    = cms.int32(0)

	process.kappaTuple.profile    = cms.bool(True)
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag   = globaltag

		# Auto alternative
		#from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
		#process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

		print "GT (overwritten):", process.GlobalTag.globaltag
	## ------------------------------------------------------------------------

	# Configure Metadata describing the file
	# Important to be evaluated correctly for the following steps
	# data, isEmbedded, miniaod, process.kappaTuple.TreeInfo.parameters = datasetsHelper.getTreeInfo(nickname, globaltag, kappaTag)
	process.kappaTuple.active = cms.vstring('TreeInfo')

	data = datasetsHelper.isData(nickname)
	isEmbedded = datasetsHelper.isEmbedded(nickname)
	print "nickname:", nickname

	#####miniaod = datasetsHelper.isMiniaod(nickname) not used anymore, since everything is MiniAOD now
	process.kappaTuple.TreeInfo.parameters= datasetsHelper.getTreeInfo(nickname, globaltag, kappaTag)
	## ------------------------------------------------------------------------

	# General configuration
	if not data:
		process.kappaTuple.Info.pileUpInfoSource = cms.InputTag("slimmedAddPileupInfo")

	# save primary vertex
	process.kappaTuple.active += cms.vstring('VertexSummary') # save VertexSummary

	process.load("Kappa.Skimming.KVertices_cff")
	process.goodOfflinePrimaryVertices.src = cms.InputTag('offlineSlimmedPrimaryVertices')
	process.p *= ( process.makeVertexes )

	process.kappaTuple.VertexSummary.whitelist = cms.vstring('offlineSlimmedPrimaryVertices')  # save VertexSummary
	process.kappaTuple.VertexSummary.rename = cms.vstring('offlineSlimmedPrimaryVertices => goodOfflinePrimaryVerticesSummary')

	process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("offlineSlimmedPrimaryVertices"))

	process.kappaTuple.active += cms.vstring('TriggerObjectStandalone')

	process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")
	if isEmbedded:
		process.kappaTuple.TriggerObjectStandalone.bits = cms.InputTag("TriggerResults", "", "SIMembedding")
		process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "MERGE")
		process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "SIMembedding")
	elif data:
		process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "RECO") # take last process used in production for data
	else:
		process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "PAT") # take last process used in production for mc

	process.kappaTuple.TriggerObjectStandalone.triggerObjects = cms.PSet( src = cms.InputTag("slimmedPatTrigger"))

	if not isEmbedded:
		process.kappaTuple.TriggerObjectStandalone.bits = cms.InputTag("TriggerResults", "", "HLT")

	print "TriggerObjectStandalone: ", process.kappaTuple.TriggerObjectStandalone

	process.kappaTuple.active += cms.vstring('BeamSpot')
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
			if "jhugen" in nickname.lower():
				process.kappaTuple.LHE.LHEafter = cms.PSet(src=cms.InputTag("source"))
			else:
				process.kappaTuple.LHE.LHEafter = cms.PSet(src=cms.InputTag("externalLHEProducer"))

	# save Flag
	process.kappaTuple.Info.isEmbedded = cms.bool(isEmbedded)

	if isEmbedded:
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)
		process.kappaTuple.active += cms.vstring('GenInfo')
		process.kappaTuple.active += cms.vstring('GenParticles') # save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")
		process.kappaTuple.active += cms.vstring('GenTaus')
		process.kappaTuple.GenTaus.genTaus.src = cms.InputTag("prunedGenParticles")
	## ------------------------------------------------------------------------

	# Trigger
	from Kappa.Skimming.hlt_run2 import hltBlacklist, hltWhitelist
	process.kappaTuple.Info.hltWhitelist = hltWhitelist
	process.kappaTuple.Info.hltBlacklist = hltBlacklist
	## ------------------------------------------------------------------------

	# should not be the default, it blows up the skim a lot
	#process.kappaTuple.active += cms.vstring('packedPFCandidates')
	#process.kappaTuple.packedPFCandidates.packedPFCandidates = cms.PSet(src = cms.InputTag("packedPFCandidates"))
	print process.producerNames().split()

	jetCollection = "slimmedJets"
	jetCollectionPuppi = "slimmedJetsPuppi"
	newPatJetIds = []
	from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
	updateJetCollection(
		process,
		jetSource = cms.InputTag('slimmedJets'),
		labelName = 'UpdatedJEC',
		jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']), 'None'),  # NOTE: Safe to always add 'L2L3Residual' as MC contains dummy L2L3Residual corrections (always set to 1)
		btagDiscriminators = [ # NOTE: cannot do btagging and jet corrections at the same time in CMSSW
			"pfDeepFlavourJetTags:probb",
			"pfDeepFlavourJetTags:probbb",
			"pfDeepFlavourJetTags:problepb",
		],
	)
	jetCollection = "selectedUpdatedPatJetsUpdatedJEC"
	newPatJetIds = [
		'pfDeepCSVJetTags:probb',
		'pfDeepCSVJetTags:probbb',
		'pfDeepFlavourJetTags:probb',
		'pfDeepFlavourJetTags:probbb',
		'pfDeepFlavourJetTags:problep'
	]
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

	#https://twiki.cern.ch/twiki/bin/view/CMS/EgammaMiniAODV2
	#defult 2017 MiniAODv2
	runVID=False
	runEnergyCorrections=True
	era='2017-Nov17ReReco'
	if (nickname.find('Run2017')>-1 and nickname.find('17Nov2017')>-1) or (nickname.find('RunIIFall17MiniAOD')>-1 and nickname.find('MiniAODv2')<0): #2017 MiniAODv1
		runVID=True
	elif (nickname.find('Run2016')>-1 and nickname.find('17Jul2018')>-1) or nickname.find('RunIISummer16MiniAODv3')>-1 or nickname.find('Embedding2016')>-1: #2016 94X-legacy (MiniAODv3)
		runVID=True
		runEnergyCorrections=False
		era='2016-Legacy'
	elif nickname.find('Run2018')>-1 or nickname.find('RunIIAutumn18MiniAOD')>-1 or nickname.find('Embedding2018')>-1: #2018
		runVID=True
		runEnergyCorrections=True
		era='2018-Prompt'
	from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
	setupEgammaPostRecoSeq(
	process,
	runVID=True,
	eleIDModules=[
		'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff',
		'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V1_cff',
		'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V1_cff',
		'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V1_cff',

		'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff',
		'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V2_cff',
		'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V2_cff',
	],
	runEnergyCorrections=runEnergyCorrections,
	era=era
	)

	process.p *= process.egammaPostRecoSeq

	process.kappaTuple.active += cms.vstring('Electrons')
	process.load("Kappa.Skimming.KElectrons_miniAOD_cff")
	process.kappaTuple.Electrons.electrons.src = cms.InputTag("slimmedElectrons")
	process.kappaTuple.Electrons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Electrons.rhoIsoInputTag = cms.InputTag(jetCollection, "rho")
	process.kappaTuple.Electrons.allConversions = cms.InputTag("reducedEgamma", "reducedConversions")
	from Kappa.Skimming.KElectrons_miniAOD_cff import setupElectrons
	process.kappaTuple.Electrons.srcIds = cms.string("pat")

	process.kappaTuple.Electrons.ids = cms.VInputTag(
		cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-veto"),
		cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-loose"),
		cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-medium"),
		cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-tight"),

		cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-veto"),
		cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-loose"),
		cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-medium"),
		cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-tight"),

		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V1-wp90"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V1-wp80"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V1-wpLoose"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V1-wp90"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V1-wp80"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V1-wpLoose"),

		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wp90"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wp80"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wpLoose"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp90"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp80"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wpLoose"),
	)

	process.kappaTuple.Electrons.userFloats = cms.VInputTag(
		cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17NoIsoV1Values"),
		cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17IsoV1Values"),
		cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17NoIsoV2Values"),
		cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17IsoV2Values"),

		cms.InputTag("electronCorrection:ecalTrkEnergyPreCorr"),
		cms.InputTag("electronCorrection:ecalTrkEnergyPostCorr"),
		cms.InputTag("electronCorrection:ecalTrkEnergyErrPreCorr"),
		cms.InputTag("electronCorrection:ecalTrkEnergyErrPostCorr"),

		        cms.InputTag("electronCorrection:energyScaleUp"),
		cms.InputTag("electronCorrection:energyScaleDown"),
		cms.InputTag("electronCorrection:energyScaleStatUp"),
		cms.InputTag("electronCorrection:energyScaleStatDown"),
		cms.InputTag("electronCorrection:energyScaleSystUp"),
		cms.InputTag("electronCorrection:energyScaleSystDown"),
		cms.InputTag("electronCorrection:energyScaleGainUp"),
		cms.InputTag("electronCorrection:energyScaleGainDown"),
		cms.InputTag("electronCorrection:energySigmaUp"),
		cms.InputTag("electronCorrection:energySigmaDown"),
		cms.InputTag("electronCorrection:energySigmaPhiUp"),
		cms.InputTag("electronCorrection:energySigmaPhiDown"),
		cms.InputTag("electronCorrection:energySigmaRhoUp"),
		cms.InputTag("electronCorrection:energySigmaRhoDown"),
	)
	## ------------------------------------------------------------------------

	#Configure Tau Leptons
	#https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Rerunning_of_the_tau_ID_on_M_AN1
	toKeep = []
	era=""
	if tools.is_above_cmssw_version([10,2,15]):
		if (nickname.find('Run2016')>-1 and nickname.find('17Jul2018')>-1) or nickname.find('RunIISummer16MiniAODv3')>-1 or nickname.find('Embedding2016')>-1: #2016 94X-legacy (MiniAODv3)
			toKeep.extend(("MVADM_2016_v1","deepTau2016v2p1"))
			era="2016"
		elif (nickname.find('Run2017')>-1 and nickname.find('17Nov2017')>-1) or (nickname.find('RunIIFall17MiniAOD')>-1 and nickname.find('MiniAODv2')<0): #2017 MiniAODv1
			toKeep.extend(("MVADM_2017_v1","deepTau2017v2p1"))
			era="2017"
		elif nickname.find('Run2018')>-1 or nickname.find('RunIIAutumn18MiniAOD')>-1 or nickname.find('Embedding2018')>-1: #2018
			toKeep.extend(("MVADM_2018_v1","deepTau2018v2p1"))
			era="2018"

	tauCollection = cms.InputTag(taus) # to be used as input

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
		#"neutralIsoPtSumWeight",
		"puCorrPtSum",
		#"footprintCorrection",
		"photonPtSumOutsideSignalCone",
		"againstMuonLoose3",
		"againstMuonTight3",
		"againstElectronMVA6category",
		"againstElectronMVA6raw",
		"againstElectronVLooseMVA6",
		"againstElectronLooseMVA6",
		"againstElectronMediumMVA6",
		"againstElectronTightMVA6",
		"againstElectronVTightMVA6"
		)

	process.kappaTuple.active += cms.vstring('L1Taus')
	if isEmbedded:
		process.kappaTuple.L1Taus.l1taus.src = cms.InputTag("caloStage2Digis","Tau","SIMembedding")

	if "MVADM_" + era + "_v1" in toKeep:
		process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist += cms.vstring(
			"MVADM" + era + "v1", #MVADM=0,1,... and -1 for unknown
			# "MVADM" + era + "v1DM0raw", #MVA score for DM=0
			# "MVADM" + era + "v1DM1raw", #MVA score for DM=1
			# "MVADM" + era + "v1DM2raw", #MVA score for DM=2
			# "MVADM" + era + "v1DM10raw", #MVA score for DM=10
			# "MVADM" + era + "v1DM11raw", #MVA score for DM=11
			# "MVADM" + era + "v1DMotherraw" #MVA score for other DM (=-1)
		)
	if "deepTau" + era + "v2p1" in toKeep:
		# deepTauID 2017v2p1
		process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist += cms.vstring(#comment out WP as defined by a simple cut at raw value
			"bydeepTau" + era + "v2p1VSjetraw",
			"byVVVLoosedeepTau" + era + "v2p1VSjet",
			"byVVLoosedeepTau" + era + "v2p1VSjet",
			"byVLoosedeepTau" + era + "v2p1VSjet",
			"byLoosedeepTau" + era + "v2p1VSjet",
			"byMediumdeepTau" + era + "v2p1VSjet",
			"byTightdeepTau" + era + "v2p1VSjet",
			"byVTightdeepTau" + era + "v2p1VSjet",
			"byVVTightdeepTau" + era + "v2p1VSjet",
			"bydeepTau" + era + "v2p1VSeraw",
			"byVVVLoosedeepTau" + era + "v2p1VSe",
			"byVVLoosedeepTau" + era + "v2p1VSe",
			"byVLoosedeepTau" + era + "v2p1VSe",
			"byLoosedeepTau" + era + "v2p1VSe",
			"byMediumdeepTau" + era + "v2p1VSe",
			"byTightdeepTau" + era + "v2p1VSe",
			"byVTightdeepTau" + era + "v2p1VSe",
			"byVVTightdeepTau" + era + "v2p1VSe",
			"bydeepTau" + era + "v2p1VSmuraw",
			"byVLoosedeepTau" + era + "v2p1VSmu",
			"byLoosedeepTau" + era + "v2p1VSmu",
			"byMediumdeepTau" + era + "v2p1VSmu",
			"byTightdeepTau" + era + "v2p1VSmu"
			)

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
	process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAll"))
	process.kappaTuple.active += cms.vstring('PatJets')
	process.kappaTuple.PatJets.ak4PF = cms.PSet(src=cms.InputTag(jetCollection))
	process.kappaTuple.PatJets.ids.extend(newPatJetIds)
	process.kappaTuple.PatJets.puppiJets = cms.PSet(src=cms.InputTag(jetCollectionPuppi))

	## Adds the possibility to add the SV refitting
	process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

	## Refitted Vertices collection
	process.kappaTuple.active += cms.vstring('RefitVertex')
	process.load("VertexRefit.TauRefit.AdvancedRefitVertexProducer_cfi")

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

	process.kappaTuple.RefitVertex.AdvancedRefittedVerticesBS = cms.PSet(src=cms.InputTag("AdvancedRefitVertexBSProducer"))
	process.kappaTuple.RefitVertex.AdvancedRefittedVerticesNoBS = cms.PSet(src=cms.InputTag("AdvancedRefitVertexNoBSProducer"))

	## calculate IP info wrt refitted PV
	process.kappaTuple.Electrons.refitvertexcollection = cms.InputTag("AdvancedRefitVertexNoBSProducer")
	process.kappaTuple.Muons.refitvertexcollection = cms.InputTag("AdvancedRefitVertexNoBSProducer")
	process.kappaTuple.PatTaus.refitvertexcollection = cms.InputTag("AdvancedRefitVertexNoBSProducer")

	## Standard MET and GenMet from pat::MET
	process.kappaTuple.active += cms.vstring('PatMET')
	process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag("slimmedMETs"))
	process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"))

	fixEE2017=False
	if nickname.find('Run2017')>-1 or nickname.find('RunIIFall17')>-1 or nickname.find('Embedding2017')>-1:
		fixEE2017=True
	from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
	runMetCorAndUncFromMiniAOD (
		process,
		isData = (data or isEmbedded), # false for MC
		fixEE2017 = fixEE2017,
		fixEE2017Params = {'userawPt': True, 'ptThreshold':50.0, 'minEtaThreshold':2.65, 'maxEtaThreshold': 3.139},
		postfix = "ModifiedMET"
	)
	# prepare Puppi
	from PhysicsTools.PatAlgos.slimming.puppiForMET_cff import makePuppiesFromMiniAOD
	# backup photon modules to protect against changes by makePuppiesFromMiniAOD (FIXME: why it is needed??)
	egmPhotonIDsBackup = process.egmPhotonIDs.clone()
	slimmedPhotonsBackup = process.slimmedPhotons.clone()
	makePuppiesFromMiniAOD( process, True )
	process.egmPhotonIDs = egmPhotonIDsBackup
	process.slimmedPhotons = slimmedPhotonsBackup
	# (pf)MET with Puppi
	runMetCorAndUncFromMiniAOD (
		process,
		isData = (data or isEmbedded),
		metType = "Puppi",
		jetFlavor = "AK4PFPuppi",
		fixEE2017 = False, # no fixEE2017 used for PuppiMET
		fixEE2017Params = {'userawPt': True, 'ptThreshold':50.0, 'minEtaThreshold':2.65, 'maxEtaThreshold': 3.139},
		postfix = "PuppiModifiedMET"
	)
	#process.puppiNoLep.useExistingWeights = False #Not necessary with MiniAODv2
	#process.puppi.useExistingWeights = False #Not necessary with MiniAODv2
	process.kMetSequence = cms.Sequence(
		process.puppiMETSequence*
		process.fullPatMetSequencePuppiModifiedMET*
		process.fullPatMetSequenceModifiedMET
	)
	process.p *= process.kMetSequence
	process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag("slimmedMETsModifiedMET"))
	process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppiModifiedMET"))

	# jet sequence has to be after puppiMEt which reruns puppi
	process.jecSequence = cms.Sequence(
		process.patJetCorrFactorsUpdatedJEC*
		process.updatedPatJetsUpdatedJEC*
		process.pfImpactParameterTagInfosUpdatedJEC*
		process.pfInclusiveSecondaryVertexFinderTagInfosUpdatedJEC*
		process.pfDeepCSVTagInfosUpdatedJEC*
		process.pfDeepFlavourTagInfosUpdatedJEC*
		process.pfDeepFlavourJetTagsUpdatedJEC*
		process.patJetCorrFactorsTransientCorrectedUpdatedJEC*
		process.updatedPatJetsTransientCorrectedUpdatedJEC*
		process.selectedUpdatedPatJetsUpdatedJEC)
	process.p *= process.jecSequence
	## ------------------------------------------------------------------------

	## GenJets
	if not data:
		process.load('PhysicsTools/JetMCAlgos/TauGenJets_cfi')
		process.load('PhysicsTools/JetMCAlgos/TauGenJetsDecayModeSelectorAllHadrons_cfi')
		process.tauGenJets.GenParticles = cms.InputTag("prunedGenParticles")
		process.p *= (
			process.tauGenJets +
			process.tauGenJetsSelectorAllHadrons
			)
		process.kappaTuple.active += cms.vstring('GenJets')
		if isEmbedded:
			process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets")
		else:
			process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets", "slimmedGenJets")
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

	print "process.p:", process.p
	return process

if __name__ == "__main__" or __name__ == "kSkimming_run2legacy_cfg":

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
		# testPaths = ['/storage/b/fs6-mirror/fcolombo/kappatest/input', '/nfs/dust/cms/user/fcolombo/kappatest/input', '/home/short']
		# testPath = [p for p in testPaths if os.path.exists(p)][0]
		process = getBaseConfig(
			globaltag="102X_mc2017_realistic_v7",
			testfile=cms.untracked.vstring("root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/280000/FE202169-8B1C-E911-8DF5-0CC47A13CB02.root"),
			nickname='VBFHToTauTauM125_RunIIFall17MiniAODv2_PU2017newpmx_13TeV_MINIAOD_powheg-pythia8',
			outputfilename="kappaTuple.root"
			)
