# Kappa test: CMSSW 5.3.22
# Kappa test: scram arch slc6_amd64_gcc472
# Kappa test: checkout script zjet/checkout.sh
# Kappa test: output kappaTuple.root

import os

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.datasetsHelper as datasetsHelper
import Kappa.Skimming.tools as tools
import Kappa.Skimming.kappaparser as kappaparser


def getBaseConfig(
		globaltag,
		testfile,
		maxevents,
		nickname,
		outputfilename,
		kappaverbosity,
		channel='mm'
	):

	############################################################################
	#  Config Info
	############################################################################
	# TODO is there a better way to do this?
	cmssw_version = os.environ["CMSSW_RELEASE_BASE"].split('/')[-1]
	cmssw_version_number = cmssw_version.split("CMSSW_")[1]
	## some infos
	print "\n--------CONFIGURATION----------"
	print "input:          ", testfile
	print "nickname:       ", nickname
	print "global tag:     ", globaltag
	print "max events:     ", maxevents
	print "output filename:", outputfilename
	print "cmssw version:  ", cmssw_version
	print "channel:        ", channel
	print "-------------------------------\n"


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
	if (cmssw_version_number.startswith("7_4_0") and cmssw_version_number.split("_")[3].startswith("pre") and (cmssw_version_number.split("_")[3][3:] >= 8)):
		# cmssw 7_4_0_pre8 or higher. see https://twiki.cern.ch/twiki/bin/view/Sandbox/MyRootMakerFrom72XTo74X#DDVectorGetter_vectors_are_empty
		print "Use condDBv2 and GeometryRecoDB"
		process.load("Configuration.Geometry.GeometryRecoDB_cff")
		process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
	else:
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
	process.kappaTuple.verbose	= cms.int32(kappaverbosity)				## verbosity level
	process.kappaTuple.profile	= cms.bool(False)
	process.kappaOut = cms.Sequence(process.kappaTuple)

	process.path = cms.Path()


	process.source.fileNames	  = testfile
	process.maxEvents.input		  = maxevents				## number of events to be processed (-1 = all in file)
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag = globaltag
	data = datasetsHelper.isData(nickname)
	centerOfMassEnergy = datasetsHelper.getCenterOfMassEnergy(nickname)
	process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )

	## ------------------------------------------------------------------------
	# Configure Metadata describing the file
	process.kappaTuple.active = cms.vstring('TreeInfo')
	process.kappaTuple.TreeInfo.parameters = cms.PSet(
		dataset						= cms.string(datasetsHelper.getDatasetName(nickname)),
		generator					= cms.string(datasetsHelper.getGenerator(nickname)),
		productionProcess			= cms.string(datasetsHelper.getProcess(nickname)),
		globalTag					= cms.string(globaltag),
		prodCampaignGlobalTag	= cms.string(datasetsHelper.getProductionCampaignGlobalTag(nickname, centerOfMassEnergy)),
		runPeriod					= cms.string(datasetsHelper.getRunPeriod(nickname)),
		jetMultiplicity			= cms.int32(datasetsHelper.getJetMultiplicity(nickname)),
		centerOfMassEnergy		= cms.int32(centerOfMassEnergy),
		puScenario					= cms.string(datasetsHelper.getPuScenario(nickname, centerOfMassEnergy)),
		isData						= cms.bool(data)
		)


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

	if channel == 'mm':
		process.kappaTuple.Info.hltWhitelist = cms.vstring(			## HLT selection
			# can be tested at http://regexpal.com
			# matches 'HLT_Mu17_Mu8_v7' etc.
			'^HLT_(Double)?Mu([0-9]+)_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$',
			# matches 'HLT_DoubleMu7_v8' etc.
			'^HLT_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$',
			)


	############################################################################
	#  PFCandidates
	############################################################################
	process.load('Kappa.Skimming.KPFCandidates_cff')
	if cmssw_version_number.startswith("7"):
		# Modifications for new particleFlow Pointers
		#process.pfPileUp.PFCandidates = cms.InputTag('particleFlowPtrs')
		#process.pfPileUpIso.PFCandidates = cms.InputTag('particleFlowPtrs')
		#process.pfNoPileUp.bottomCollection = cms.InputTag('particleFlowPtrs')
		#process.pfNoPileUpIso.bottomCollection = cms.InputTag('particleFlowPtrs')
		process.pfJetTracksAssociatorAtVertex.jets= cms.InputTag('ak5PFJets')

	process.path *= (
		process.goodOfflinePrimaryVertices
		* process.pfPileUp
		* process.pfNoPileUp
		#* process.makePFBRECO
		#* process.makeKappaPFCandidates
	)


	if channel == 'mm':
		############################################################################
		#  Muons
		############################################################################
		#process.load('Kappa.Skimming.KMuons_cff')
		process.kappaTuple.active += cms.vstring('Muons')					## produce/save KappaMuons
		process.kappaTuple.Muons.minPt = cms.double(8.0)

		process.goodMuons = cms.EDFilter('CandViewSelector',
			src = cms.InputTag('muons'),
			cut = cms.string("pt > 15.0 & abs(eta) < 8.0"),# & isGlobalMuon()"),
		)
		process.twoGoodMuons = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('goodMuons'),
			minNumber = cms.uint32(2),
		)
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

		process.path *= (process.goodMuons * process.twoGoodMuons * process.pfmuIsoDepositPFCandidates)

	############################################################################
	#  Jets
	############################################################################
	process.load('Kappa.Skimming.KJets{0}_cff'.format('_run2' if cmssw_version_number.startswith("7") else ''))

	process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')
	process.kappaTuple.Jets = cms.PSet(
		process.kappaNoCut,
		process.kappaNoRegEx,
		taggers = cms.vstring(
			'QGlikelihood',
			#'QGmlp',
			#'TrackCountingHighEffBJetTags',
			#'TrackCountingHighPurBJetTags',
			#'JetProbabilityBJetTags',
			#'JetBProbabilityBJetTags',
			#'SoftElectronBJetTags',
			#'SoftMuonBJetTags',
			#'SoftMuonByIP3dBJetTags',
			#'SoftMuonByPtBJetTags',
			#'SimpleSecondaryVertexBJetTags',
			'CombinedSecondaryVertexBJetTags',
			'CombinedSecondaryVertexMVABJetTags',
			#'puJetIDFullDiscriminant',
			#'puJetIDFullLoose',
			#'puJetIDFullMedium',
			#'puJetIDFullTight',
			#'puJetIDCutbasedDiscriminant',
			#'puJetIDCutbasedLoose',
			#'puJetIDCutbasedMedium',
			#'puJetIDCutbasedTight'
			),
		AK5PFTaggedJets = cms.PSet(
			src = cms.InputTag('ak5PFJets'),
			QGtagger = cms.InputTag('AK5PFJetsQGTagger'),
			Btagger  = cms.InputTag('ak5PF'),
			PUJetID  = cms.InputTag('ak5PFPuJetMva'),
			PUJetID_full = cms.InputTag('full'),
			),
		AK5PFTaggedJetsCHS = cms.PSet(
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
		process.makePFJets
		* process.makePFJetsCHS
		* process.kt6PFJets
		* process.makeQGTagging

		* process.ak5PFJetTracksAssociator
		* process.ak5PFJetBtaggingIP
		* process.ak5PFJetBtaggingSV
		* process.ak5PFCHSJetTracksAssociator
		* process.ak5PFCHSJetBtaggingIP
		* process.ak5PFCHSJetBtaggingSV
		
		
		#process.makeBTagging *
		#* process.makePUJetID
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
		KappaParser.setDefault('test', '53mc12')
		testdict = {
			'53data12': {
				'files': 'file:/storage/8/dhaitz/testfiles/data_AOD_2012A.root',
				'globalTag': 'FT53_V21A_AN6::All',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
			},
			'53mc12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball__Summer12_DR53X-PU_RD1_START53_V7N-v1__AODSIM.root',
				'globalTag': 'START53_V27::All',
				'nickName': 'DYJetsToLL_M_50_madgraph_8TeV',
			},
			'74data12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DoubleMuParked__CMSSW_7_4_0_pre9_ROOT6-GR_R_74_V8_1Apr_RelVal_dm2012D-v2__RECO.root',
				'globalTag': 'GR_R_74_V8::All',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
			},
		}
		KappaParser.parseArgumentsWithTestDict(testdict)

		process = getBaseConfig(
			globaltag=KappaParser.globalTag,
			testfile=cms.untracked.vstring(KappaParser.files),
			maxevents=KappaParser.maxEvents,
			nickname=KappaParser.nickName,
			outputfilename=KappaParser.output,
			kappaverbosity=KappaParser.kappaVerbosity,
			channel=KappaParser.channel,
		)
	## for grid-control:
	else:
		process = getBaseConfig(
			globaltag='@GLOBALTAG@',
			testfile=cms.untracked.vstring(""),
			maxevents=-1,
			nickname='@NICK@',
			outputfilename='kappatuple.root',
			kappaverbosity=0
		)
