# Kappa test: CMSSW 5.3.22
# Kappa test: scram arch slc6_amd64_gcc472
# Kappa test: checkout script zjet/checkout53.sh
# Kappa test: output skim53.root

import os

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.datasetsHelper as datasetsHelper
import Kappa.Skimming.tools as tools
import Kappa.Skimming.kappaparser as kappaparser

from Kappa.Skimming.gc_tools import gc_var_or_callable_parameter

""" channels:
		mm: add muons, require >=2 muons
		ee: add electrons, require >=2 electrons
		em: add muons and electrons, >=1 muon and >=1 electron require (for background studies with the e-mu-method)
		eemm: add muons and electrons, require >=2 muons and >=2 electrons

	#TODO e/mu filter for eemm and em channel

"""


def getBaseConfig(
		globaltag,
		testfile,
		maxevents,
		nickname,
		outputfilename,
		channel='mm',
		is_data=None,
	):

	#  Config parameters  ##############################################
	cmssw_version = os.environ["CMSSW_VERSION"].split('_')
	cmssw_version = tuple([int(i) for i in cmssw_version[1:4]] + cmssw_version[4:])
	autostr = ""
	if globaltag.lower() == 'auto':
		from Configuration.AlCa.autoCond import autoCond
		globaltag = autoCond['startup']
		autostr = " (from autoCond)"
	if is_data is None:
		data = any([name in testfile[0] for name in 'SingleMu', 'DoubleMu', 'DoubleElectron', 'MuEG'])
	else:
		data = is_data
	miniaod = False

	## print information
	print "\n------- CONFIGURATION 1 ---------"
	print "input:          ", testfile[0], "... (%d files)" % len(testfile) if len(testfile) > 1 else ""
	print "file type:      ", "miniAOD" if miniaod else "AOD"
	print "data:           ", data
	print "output:         ", outputfilename
	print "nickname:       ", nickname
	print "global tag:     ", globaltag + autostr
	print "max events:     ", maxevents
	print "cmssw version:  ", '.'.join([str(i) for i in cmssw_version])
	print "channel:        ", channel
	print "---------------------------------"
	print


	############################################################################
	#  Basic Process Setup
	############################################################################
	process = cms.Process("KAPPA")
	## MessageLogger
	process.load("FWCore.MessageLogger.MessageLogger_cfi")
	process.MessageLogger.default = cms.untracked.PSet(
		ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5))
		#suppressError = cms.untracked.vstring("electronIdMVAProducer")
	)
	process.MessageLogger.cerr.FwkReport.reportEvery = 50
	## Options and Output Report
	process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
	## Source
	process.source = cms.Source("PoolSource",
		fileNames = cms.untracked.vstring()
	)
	## Maximal number of Events
	process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )
	## Geometry and Detector Conditions (needed for a few patTuple production steps)
	import Kappa.Skimming.tools as tools
	cmssw_version_number = tools.get_cmssw_version_number()
	process.load("Configuration.Geometry.GeometryIdeal_cff")
	process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
	from Configuration.AlCa.autoCond import autoCond
	process.GlobalTag.globaltag = cms.string(autoCond['startup'])
	# print the global tag until it is clear whether this auto global tag is fine
	print "GT from autoCond:", process.GlobalTag.globaltag
	process.load("Configuration.StandardSequences.MagneticField_cff")


	############################################################################
	#  KAPPA
	############################################################################
	process.load('Kappa.Producers.KTuple_cff')
	process.kappaTuple = cms.EDAnalyzer('KTuple',
		process.kappaTupleDefaultsBlock,
		outputFile = cms.string("kappaTuple.root"),
	)
	process.kappaTuple.active = cms.vstring()
	process.kappaTuple.outputFile = outputfilename			## name of output file
	process.kappaTuple.verbose	= 0				## verbosity level
	process.kappaTuple.profile	= cms.bool(False)
	process.kappaOut = cms.Sequence(process.kappaTuple)

	process.path = cms.Path()


	process.source.fileNames	  = testfile
	process.maxEvents.input		  = maxevents				## number of events to be processed (-1 = all in file)
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag = globaltag
	data = datasetsHelper.isData(nickname)
	process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )


	############################################################################
	#  Basic Objects
	############################################################################
	process.kappaTuple.active += cms.vstring('VertexSummary')	## save VertexSummary,
	process.kappaTuple.VertexSummary.whitelist = cms.vstring('goodOfflinePrimaryVertices')
	#process.kappaTuple.active += cms.vstring('BeamSpot')		## save Beamspot,
	#process.kappaTuple.active += cms.vstring('TriggerObjects')
	if data:
		process.kappaTuple.active+= cms.vstring('DataInfo')		## produce Metadata for data,
	else:
		process.kappaTuple.active+= cms.vstring('GenInfo')		## produce Metadata for MC,
		process.kappaTuple.active+= cms.vstring('GenParticles')

	#Trigger 
	trigger_dict = {
		'mtrigger': ['^HLT_(Double)?Mu([0-9]+)_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$'],
		'etrigger': ['HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL.*'],
		'emtrigger': ["HLT_Mu17_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL.*", "HLT_Mu8_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL.*",]
	}
	channel_dict = {
		'ee': ['etrigger'],
		'mm': ['mtrigger'],
		'eemm': ['etrigger', 'mtrigger'],
		'em': ['emtrigger']
	}	
	process.kappaTuple.Info.hltWhitelist = cms.vstring("")
	for triggers in channel_dict[channel]:
		for trigger in trigger_dict[triggers]:
			process.kappaTuple.Info.hltWhitelist += cms.vstring(trigger)


	############################################################################
	#  PFCandidates
	############################################################################
	process.load('Kappa.Skimming.KPFCandidates_cff')
	process.path *= (
		process.goodOfflinePrimaryVertices
		* process.pfPileUp
		* process.pfNoPileUp
		#* process.makePFBRECO
		#* process.makeKappaPFCandidates
	)

	if 'm' in channel:
		############################################################################
		#  Muons
		############################################################################

		process.kappaTuple.active += cms.vstring('Muons')	## produce/save KappaMuons
		process.kappaTuple.Muons.minPt = cms.double(8.0)

		## Isodeposits for muons
		process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi')
		process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi')
		process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi')

		process.pfmuIsoDepositPFCandidates = cms.EDProducer(
			"CandIsoDepositProducer",
			src = cms.InputTag("muons"),
			MultipleDepositsFlag = cms.bool(False),
			trackType = cms.string('candidate'),
			ExtractorPSet = cms.PSet(
				Diff_z = cms.double(99999.99),
				ComponentName = cms.string('CandViewExtractor'),
				DR_Max = cms.double(1.0),
				Diff_r = cms.double(99999.99),
				inputCandView = cms.InputTag("particleFlow"),
				DR_Veto = cms.double(1e-05),
				DepositLabel = cms.untracked.string('')
			)
		)
		process.path *= (process.pfmuIsoDepositPFCandidates)
		process.goodMuons = cms.EDFilter('CandViewSelector',
			src = cms.InputTag('muons'),
			cut = cms.string("pt > 15.0"),
		)
		process.oneGoodMuon = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('goodMuons'),
			minNumber = cms.uint32(1),
		)
		process.twoGoodMuons = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('goodMuons'),
			minNumber = cms.uint32(2),
		)
		if 'mm' in channel:
			process.path *= (process.goodMuons * process.twoGoodMuons)

	if 'e' in channel:
		############################################################################
		#  Electrons
		############################################################################

		#TODO Add Electron
		process.load('EgammaAnalysis.ElectronTools.electronIdMVAProducer_cfi')
		process.load('TrackingTools.TransientTrack.TransientTrackBuilder_cfi')
		process.load('PhysicsTools.PatAlgos.producersLayer1.electronProducer_cfi')
		process.patElectrons.electronIDSources = cms.PSet(
			## default cut based Id
			eidRobustLoose      = cms.InputTag("eidRobustLoose"     ),
			eidRobustTight      = cms.InputTag("eidRobustTight"     ),
			eidLoose            = cms.InputTag("eidLoose"           ),
			eidTight            = cms.InputTag("eidTight"           ),
			eidRobustHighEnergy = cms.InputTag("eidRobustHighEnergy"),
			## MVA based Id
			idMvaTrigV0           = cms.InputTag("mvaTrigV0"          ),
			idMvaTrigNoIPV0       = cms.InputTag("mvaTrigNoIPV0"      ),
			idMvaNonTrigV0        = cms.InputTag("mvaNonTrigV0"       ),
		)
		process.patElectrons.genParticleMatch = ""
		process.patElectrons.addGenMatch = False
		process.patElectrons.embedGenMatch = False
		process.patElectrons.embedGsfElectronCore          = True
		process.patElectrons.embedGsfTrack                 = True
		process.patElectrons.embedSuperCluster             = True
		process.patElectrons.embedPflowSuperCluster        = True
		process.patElectrons.embedSeedCluster              = True
		process.patElectrons.embedBasicClusters            = True
		process.patElectrons.embedPreshowerClusters        = True
		process.patElectrons.embedPflowBasicClusters       = True
		process.patElectrons.embedPflowPreshowerClusters   = True
		process.patElectrons.embedPFCandidate              = True
		process.patElectrons.embedTrack                    = True
		process.patElectrons.embedRecHits                  = True

		process.patElectrons.embedHighLevelSelection.pvSrc = "goodOfflinePrimaryVertices"
		process.electronIdMVA = cms.Sequence(
			process.mvaTrigV0+
			process.mvaTrigNoIPV0+
			process.mvaNonTrigV0
		)
		process.makeKappaElectrons = cms.Sequence(
			process.electronIdMVA *
			process.patElectrons
		)
		process.path *= (process.makeKappaElectrons)


		## CALIBRATIONS
		# momentum corrections
		process.load('EgammaAnalysis.ElectronTools.electronRegressionEnergyProducer_cfi')
		process.eleRegressionEnergy.inputElectronsTag = cms.InputTag('patElectrons')
		process.eleRegressionEnergy.inputCollectionType = cms.uint32(1)

		process.load("Configuration.StandardSequences.Services_cff")
		process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
				calibratedPatElectrons = cms.PSet(
					initialSeed = cms.untracked.uint32(1),
					engineName = cms.untracked.string('TRandom3')
				),
		)

		# calibrate pat electrons
		process.load("EgammaAnalysis.ElectronTools.calibratedPatElectrons_cfi")
		if data:
			inputDataset =  "22Jan2013ReReco"
		else:
			#inputDataset =  "Summer12_DR53X_HCP2012"
			inputDataset =  "Summer12_LegacyPaper"
		print "Using electron calibration", inputDataset
		process.calibratedPatElectrons.inputDataset = cms.string(inputDataset)
		process.calibratedPatElectrons.isMC = cms.bool(not data)

		## for cutbased ID
		from CommonTools.ParticleFlow.Tools.pfIsolation import setupPFElectronIso, setupPFMuonIso
		process.calibeleIsoSequence = setupPFElectronIso(process, 'calibratedPatElectrons', "PFIsoCal")
		process.eleIsoSequence = setupPFElectronIso(process, 'patElectrons')
		process.pfiso = cms.Sequence(process.pfParticleSelectionSequence
			+ process.eleIsoSequence + process.calibeleIsoSequence 
		)

		# rho for e isolation
		from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
		process.kt6PFJetsForIsolation = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
		process.kt6PFJetsForIsolation.Rho_EtaMax = cms.double(2.5)

		process.path *= (
			process.eleRegressionEnergy *
			process.calibratedPatElectrons * 
			process.pfiso *
			process.kt6PFJetsForIsolation
		)


		#add to Kappa
		process.kappaTuple.active += cms.vstring('Electrons')
		process.kappaTuple.Electrons = cms.PSet(
			process.kappaNoCut, process.kappaNoRegEx,
			ids = cms.vstring(),
			srcIds = cms.string("pat"),
			electrons = cms.PSet(
				src = cms.InputTag("patElectrons"),
				allConversions = cms.InputTag("allConversions"),
				offlineBeamSpot = cms.InputTag("offlineBeamSpot"),
				vertexcollection = cms.InputTag("goodOfflinePrimaryVertices"),
				isoValInputTags = cms.VInputTag(
					cms.InputTag('elPFIsoValueChargedAll04PFIdPFIso'),
					cms.InputTag('elPFIsoValueGamma04PFIdPFIso'),
					cms.InputTag('elPFIsoValueNeutral04PFIdPFIso'),
					cms.InputTag('elPFIsoValuePU04PFIdPFIso')),
				rhoIsoInputTag = cms.InputTag("kt6PFJetsForIsolation", "rho"),
			),
		)
		process.kappaTuple.Electrons.correlectrons = process.kappaTuple.Electrons.electrons.clone(
				src = cms.InputTag("calibratedPatElectrons"),
				isoValInputTags = cms.VInputTag(
					cms.InputTag('elPFIsoValueChargedAll04PFIdPFIsoCal'),
					cms.InputTag('elPFIsoValueGamma04PFIdPFIsoCal'),
					cms.InputTag('elPFIsoValueNeutral04PFIdPFIsoCal'),
					cms.InputTag('elPFIsoValuePU04PFIdPFIsoCal')),
		)

		#process.kappaTuple.Electrons.ids = cms.VInputTag("mvaTrigV0", "mvaTrigNoIPV0", "mvaNonTrigV0")
		process.kappaTuple.Electrons.ids = cms.VInputTag('idMvaNonTrigV0', 'idMvaTrigNoIPV0', 'idMvaTrigV0')
		process.kappaTuple.Electrons.minPt = cms.double(8.0)


		### Filter
		process.goodElectrons = cms.EDFilter('CandViewSelector',
			src = cms.InputTag('calibratedPatElectrons'),
			cut = cms.string("pt > 15.0"),
		)
		process.oneGoodElectron = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('goodElectrons'),
			minNumber = cms.uint32(1),
		)
		process.twoGoodElectrons = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('goodElectrons'),
			minNumber = cms.uint32(2),
		)
		if 'ee' in channel:
			process.path *= (process.goodElectrons * process.twoGoodElectrons)

	if 'em' in channel:
		process.path *= (process.goodElectrons * process.oneGoodElectron
						* process.goodMuons * process.oneGoodMuon)


	############################################################################
	#  Jets
	############################################################################

	process.load('RecoJets.JetProducers.ak5PFJets_cfi')
	process.ak5PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
	process.ak5PFJetsCHS = process.ak5PFJets.clone( src = cms.InputTag('pfNoPileUp') )

	process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')
	process.kappaTuple.Jets = cms.PSet(
		process.kappaNoCut,
		process.kappaNoRegEx,
		taggers = cms.vstring(),
		ak5PFJets = cms.PSet(
			src = cms.InputTag('ak5PFJets'),
			QGtagger = cms.InputTag('AK5PFJetsQGTagger'),
			Btagger  = cms.InputTag('ak5PF'),
			PUJetID  = cms.InputTag('ak5PFPuJetMva'),
			PUJetID_full = cms.InputTag('full'),
			),
		ak5PFJetsCHS = cms.PSet(
			src = cms.InputTag('ak5PFJetsCHS'),
			QGtagger = cms.InputTag('AK5PFJetsCHSQGTagger'),
			Btagger  = cms.InputTag('ak5PFCHS'),
			PUJetID  = cms.InputTag('ak5PFCHSPuJetMva'),
			PUJetID_full = cms.InputTag('full'),
			),
		)
	process.kappaTuple.Jets.minPt = cms.double(5.0)

	if not data:
		process.load('RecoJets.JetProducers.ak5GenJets_cfi')
		process.path *= (
			process.genParticlesForJetsNoNu *
			process.ak5GenJetsNoNu
		)
		process.kappaTuple.active += cms.vstring('LV')
		process.kappaTuple.LV.rename = cms.vstring('ak => AK')
		process.kappaTuple.LV.whitelist = cms.vstring('ak5GenJetsNoNu')

	# add kt6PFJets, needed for the PileupDensity
	from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
	process.kt6PFJets = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
	process.kt6PFJets.Rho_EtaMax = cms.double(2.5)

	process.path *= (
		process.ak5PFJets
		* process.ak5PFJetsCHS
		* process.kt6PFJets
	)


	############################################################################
	#  MET
	############################################################################
	# MET correction ----------------------------------------------------------
	process.load('JetMETCorrections.Type1MET.pfMETCorrectionType0_cfi')
	process.path *= (
		process.type0PFMEtCorrection
	)
	#TODO check type 0 corrections
	process.kappaTuple.active += cms.vstring('MET')					   ## produce/save KappaPFMET
	process.kappaTuple.MET.whitelist = cms.vstring('pfChMet', '_pfMet_')

	if cmssw_version_number.startswith("5"):
		# MET correction ----------------------------------------------------------
		process.load("JetMETCorrections.Type1MET.pfMETCorrections_cff")
		process.pfchsMETcorr.src = cms.InputTag('goodOfflinePrimaryVertices')
		# Type-0
		process.pfMETCHS = process.pfType1CorrectedMet.clone(
			applyType1Corrections = cms.bool(False),
			applyType0Corrections = cms.bool(True)
		)
		# MET Path
		process.path *= (
			process.producePFMETCorrections * process.pfMETCHS
		)
		process.kappaTuple.MET.whitelist += cms.vstring("pfMETCHS")


	############################################################################
	#  Almost done ...
	############################################################################
	process.path *= (
		process.kappaOut
	)
	return process



if __name__ == '__main__':
	# run local skim by hand without replacements by grid-control
	if('@' in '@NICK@'):
		KappaParser = kappaparser.KappaParserZJet()
		KappaParser.setDefault('test', '53data12')
		testdict = {
			'53data12': {
				'files': 'file:/storage/8/dhaitz/testfiles/data_AOD_2012A.root',
				'globalTag': 'FT53_V21A_AN6::All',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
				'channel': 'mm',
			},
			'53mc12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball__Summer12_DR53X-PU_RD1_START53_V7N-v1__AODSIM.root',
				'globalTag': 'START53_V27::All',
				'nickName': 'DYJetsToLL_M_50_madgraph_8TeV',
				'channel': 'mm',
			},
			'53mc12ee': {
				'files': 'file:/storage/8/dhaitz/testfiles/mc_DYToEE-powheg.root',
				'globalTag': 'START53_V27::All',
				'nickName': 'DYJetsToEE_M_20_powheg_8TeV',
				'channel': 'ee',
			},
			'53mc12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball__Summer12_DR53X-PU_RD1_START53_V7N-v1__AODSIM.root',
				'globalTag': 'START53_V27::All',
				'nickName': 'DYJetsToLL_M_50_madgraph_8TeV',
				'channel': 'eemm',
			},
		}
		KappaParser.parseArgumentsWithTestDict(testdict)

		process = getBaseConfig(
			globaltag=KappaParser.globalTag,
			testfile=KappaParser.files,
			maxevents=KappaParser.maxEvents,
			nickname=KappaParser.nickName,
			outputfilename="skim53.root",
			channel=KappaParser.channel,
		)
	## for grid-control:
	else:
		process = getBaseConfig(
			globaltag='@GLOBALTAG@',
			testfile=cms.untracked.vstring('@FILE_NAMES@'.strip('"').split('", "')),
			maxevents=-1,
			nickname='@NICK@',
			outputfilename='kappatuple.root',
			channel = '@CHANNEL@',
			is_data = gc_var_or_callable_parameter(gc_var_name='@IS_DATA@', callable=getBaseConfig),
		)
