# Kappa test: CMSSW 5.3.22
# Kappa test: scram arch slc6_amd64_gcc472
# Kappa test: checkout script scripts/checkoutCmssw53xPackagesForSkimming.py

import os

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.datasetsHelper as datasetsHelper
import Kappa.Skimming.tools as tools
import Kappa.Skimming.kappaparser as kappaparser

#TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
# further remove unneeded Htt stuff
# download test file
# QG-tagging
# gen jets without neutrinos
# type 0 for met
#TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

def getBaseConfig(
		globaltag,
		testfile,
		maxevents,
		nickname,
		outputfilename,
		kappaverbosity,
		channel='mm'
	):
	from Kappa.Skimming.KSkimming_template_cfg import process
	process.source.fileNames	  = testfile
	process.maxEvents.input		  = maxevents				## number of events to be processed (-1 = all in file)
	process.kappaTuple.outputFile = outputfilename			## name of output file
	process.kappaTuple.verbose	= cms.int32(kappaverbosity)				## verbosity level
	process.kappaTuple.profile	= cms.bool(False)
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag = globaltag
	data = datasetsHelper.isData(nickname)
	centerOfMassEnergy = datasetsHelper.getCenterOfMassEnergy(nickname)
	process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )

	# TODO is there a better way to do this?
	cmssw_version = os.environ["CMSSW_RELEASE_BASE"].split('/')[-1]
	cmssw_version_number = cmssw_version.split("CMSSW_")[1]

	## some infos
	print "\n--------CONFIGURATION----------"
	print "input:          ", testfile
	print "nickname:       ", nickname
	print "global tag:     ", process.GlobalTag.globaltag
	print "max events:     ", maxevents
	print "output filename:", outputfilename
	print "cmssw version:  ", cmssw_version
	print "channel:        ", channel
	print "-------------------------------\n"

	process.p = cms.Path ( )
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

	## ------------------------------------------------------------------------
	# General configuration

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



	## ------------------------------------------------------------------------
	# Configure PFCandidates and offline PV
	# PFCandidates ------------------------------------------------------------
	#
	process.load('Kappa.Skimming.KPFCandidates_cff')
	if cmssw_version_number.startswith("7"):
		# Modifications for new particleFlow Pointers
		#process.pfPileUp.PFCandidates = cms.InputTag('particleFlowPtrs')
		#process.pfPileUpIso.PFCandidates = cms.InputTag('particleFlowPtrs')
		#process.pfNoPileUp.bottomCollection = cms.InputTag('particleFlowPtrs')
		#process.pfNoPileUpIso.bottomCollection = cms.InputTag('particleFlowPtrs')
		process.pfJetTracksAssociatorAtVertex.jets= cms.InputTag('ak5PFJets')


	#process.p *= (process.goodOfflinePrimaryVertices * process.pfPileUp * process.pfNoPileUp)
	process.p *= (process.goodOfflinePrimaryVertices * process.pfPileUp * process.pfNoPileUp * process.makePFBRECO * process.makeKappaPFCandidates)

	## ------------------------------------------------------------------------
	if channel == 'mm':
		# Configure Muons
		process.load('Kappa.Skimming.KMuons_cff')
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
		process.p *= (process.goodMuons * process.twoGoodMuons * process.makeKappaMuons)

		## for muon iso
		# https://github.com/ajgilbert/ICHiggsTauTau/blob/master/test/higgstautau_new_cfg.py#L430-L460
		process.load('CommonTools.ParticleFlow.Isolation.pfMuonIsolation_cff')
		process.muPFIsoValueCharged04PFIso = process.muPFIsoValueCharged04.clone()
		process.muPFIsoValueChargedAll04PFIso = process.muPFIsoValueChargedAll04.clone()
		process.muPFIsoValueGamma04PFIso = process.muPFIsoValueGamma04.clone()
		process.muPFIsoValueNeutral04PFIso = process.muPFIsoValueNeutral04.clone()
		process.muPFIsoValuePU04PFIso = process.muPFIsoValuePU04.clone()

		process.muonPFIsolationValuesSequence = cms.Sequence(
			process.muPFIsoValueCharged04PFIso+
			process.muPFIsoValueChargedAll04PFIso+
			process.muPFIsoValueGamma04PFIso+
			process.muPFIsoValueNeutral04PFIso+
			process.muPFIsoValuePU04PFIso
		)
		process.muPFIsoDepositCharged.src = cms.InputTag('muons')
		process.muPFIsoDepositChargedAll.src = cms.InputTag('muons')
		process.muPFIsoDepositNeutral.src = cms.InputTag('muons')
		process.muPFIsoDepositGamma.src = cms.InputTag('muons')
		process.muPFIsoDepositPU.src = cms.InputTag('muons')

	## ------------------------------------------------------------------------
	## KappaJets
	process.load('Kappa.Skimming.KJets{0}_cff'.format('_run2' if cmssw_version_number.startswith("7") else ''))
	process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')
	process.kappaTuple.Jets = cms.PSet(
		process.kappaNoCut,
		process.kappaNoRegEx,
		taggers = cms.vstring(
	#		'QGlikelihood',
	#		'QGmlp',
			'TrackCountingHighEffBJetTags',
			'TrackCountingHighPurBJetTags',
			'JetProbabilityBJetTags',
			'JetBProbabilityBJetTags',
			'SoftElectronBJetTags',
			'SoftMuonBJetTags',
			'SoftMuonByIP3dBJetTags',
			'SoftMuonByPtBJetTags',
			#'SimpleSecondaryVertexBJetTags',
			'CombinedSecondaryVertexBJetTags',
			#'CombinedSecondaryVertexMVABJetTags',
			'puJetIDFullDiscriminant',
			'puJetIDFullLoose',
			'puJetIDFullMedium',
			'puJetIDFullTight',
			#'puJetIDCutbasedDiscriminant',
			#'puJetIDCutbasedLoose',
			#'puJetIDCutbasedMedium',
			#'puJetIDCutbasedTight'
			),
		AK5PFTaggedJets = cms.PSet(
			src = cms.InputTag('ak5PFJets'),
			#QGtagger = cms.InputTag('AK5PFJetsQGTagger'),
			QGtagger = cms.InputTag(''),
			Btagger  = cms.InputTag('ak5PF'),
			PUJetID  = cms.InputTag('ak5PFPuJetMva'),
			PUJetID_full = cms.InputTag('full'),
			),
		AK5PFTaggedJetsCHS = cms.PSet(
			src = cms.InputTag('ak5PFJetsCHS'),
			#QGtagger = cms.InputTag('AK5PFJetsCHSQGTagger'),
			QGtagger = cms.InputTag(''),
			Btagger  = cms.InputTag('ak5PFCHS'),
			PUJetID  = cms.InputTag('ak5PFCHSPuJetMva'),
			PUJetID_full = cms.InputTag('full'),
			),
		)
	process.kappaTuple.Jets.minPt = cms.double(5.0)

	if not data:
		process.kappaTuple.active += cms.vstring('GenJets')
		process.kappaTuple.GenJets.whitelist = cms.vstring('ak5GenJets')
		process.kappaTuple.GenJets.rename = cms.vstring('ak => AK')


	# add kt6PFJets, needed for the PileupDensity
	from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
	process.kt6PFJets = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
	process.kt6PFJets.Rho_EtaMax = cms.double(2.5)

	process.p *= (
		process.makePFJets *
		process.makePFJetsCHS *
		process.kt6PFJets *
	#	process.makeQGTagging *
		process.makeBTagging *
		process.makePUJetID
	)

	## ------------------------------------------------------------------------
	## MET
	# MET correction ----------------------------------------------------------
	process.load('JetMETCorrections.Type1MET.pfMETCorrectionType0_cfi')
	process.p *= (
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
		process.p *= (
			process.producePFMETCorrections * process.pfMETCHS
		)
		process.kappaTuple.MET.whitelist += cms.vstring("pfMETCHS")

	## ------------------------------------------------------------------------
	## And let it run
	process.p *= (
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
