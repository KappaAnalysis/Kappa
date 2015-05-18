# Kappa test: CMSSW 5.3.22
# Kappa test: scram arch slc6_amd64_gcc472

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
	if True or (cmssw_version_number.startswith("7_4_0") and cmssw_version_number.split("_")[3].startswith("pre") and (cmssw_version_number.split("_")[3][3:] >= 8)):
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
		#generator					= cms.string(datasetsHelper.getGenerator(nickname)),
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
		#process.kappaTuple.Info.hltSource = ""

	if cmssw_version_number.startswith("7_4_2"):
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)

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
	process.load("CommonTools.ParticleFlow.pfNoPileUpIso_cff")
	process.load("Kappa.Skimming.KPFCandidates_run2_cff")
	"""process.kappaTuple.active += cms.vstring('PFCandidates') # save PFCandidates for deltaBeta corrected
	process.kappaTuple.PFCandidates.whitelist = cms.vstring( # isolation used for electrons and muons.
	##	"pfNoPileUpChargedHadrons",    ## switch to pfAllChargedParticles
		"pfAllChargedParticles",       ## same as pfNoPileUpChargedHadrons +pf_electrons + pf_muons
		"pfNoPileUpNeutralHadrons",
		"pfNoPileUpPhotons",
		"pfPileUpChargedHadrons",
		)"""
	#process.p *= ( process.makePFBRECO * process.makePFCandidatesForDeltaBeta )
	process.path *= ( process.makeKappaPFCandidates )


	if channel == 'mm':
		############################################################################
		#  Muons
		############################################################################
		process.load('Kappa.Skimming.KMuons_run2_cff')

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
		process.path *= (process.goodMuons * process.twoGoodMuons * process.makeKappaMuons)

		"""
		process.load("CommonTools.ParticleFlow.Isolation.pfMuonIsolation_cff")

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
		process.muPFIsoDepositCharged.src = cms.InputTag("muons")
		process.muPFIsoDepositChargedAll.src = cms.InputTag("muons")
		process.muPFIsoDepositNeutral.src = cms.InputTag("muons")
		process.muPFIsoDepositGamma.src = cms.InputTag("muons")
		process.muPFIsoDepositPU.src = cms.InputTag("muons")

		process.pfMuonIso = cms.Sequence( 
			process.muonPFIsolationDepositsSequence +
			process.muonPFIsolationValuesSequence
		)

		process.path *= (process.goodMuons * process.twoGoodMuons * process.pfMuonIso)
		"""

	############################################################################
	#  Jets
	############################################################################
	#process.load('Kappa.Skimming.KJets{0}_cff'.format('_run2' if cmssw_version_number.startswith("7") else ''))


	## ------------------------------------------------------------------------
	## Create ak5 jets from all pf candidates and from pfNoPileUp candidates
	##  - note that this requires that goodOfflinePrimaryVertices and PFBRECO
	##	has been run beforehand. e.g. using the sequence makePFBRECO from
	##	KPFCandidates_cff.py
	process.load("RecoJets.JetProducers.ak5PFJets_cfi")

	process.ak5PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
	process.ak5PFJetsCHS = process.ak5PFJets.clone(src = cms.InputTag('pfNoPileUp') )

	"""
	## ------------------------------------------------------------------------
	## Gluon tagging
	##  - https://twiki.cern.ch/twiki/bin/viewauth/CMS/GluonTag
	process.load("QuarkGluonTagger.EightTeV.QGTagger_RecoJets_cff")

	process.QGTagger.srcJets	 = cms.InputTag('ak5PFJets')
	process.AK5PFJetsQGTagger	= process.QGTagger.clone()
	process.AK5PFJetsCHSQGTagger = process.QGTagger.clone(
		srcJets = cms.InputTag('ak5PFJetsCHS'),
		useCHS = cms.untracked.bool(True)
	)
	## run this to create Quark-Gluon tag
	makeQGTagging = cms.Sequence(
		QuarkGluonTagger *
		AK5PFJetsQGTagger *
		AK5PFJetsCHSQGTagger
		)


	## ------------------------------------------------------------------------
	## B-tagging (for ak5 jets)
	##  - https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets
	process.load("RecoJets.JetAssociationProducers.ic5JetTracksAssociatorAtVertex_cfi")
	process.load("RecoBTag.Configuration.RecoBTag_cff")
	#from RecoBTag.SoftLepton.softPFElectronTagInfos_cfi import softPFElectronsTagInfos
	#from RecoBTag.SoftLepton.SoftLeptonByPt_cfi import softPFElectronByPtBJetTags
	#from RecoBTag.SoftLepton.softMuonTagInfos_cfi import softMuonTagInfos
	#from RecoBTag.SoftLepton.SoftLeptonByPt_cfi import softPFMuonByPtBJetTags
	#from RecoBTag.SoftLepton.SoftLeptonByIP3d_cfi import softPFMuonByIP3dBJetTags

	## create a ak5PF jets and tracks association
	process.ak5PFJetNewTracksAssociatorAtVertex		   = process.ic5JetTracksAssociatorAtVertex.clone()
	process.ak5PFJetNewTracksAssociatorAtVertex.jets	  = "ak5PFJets"
	process.ak5PFJetNewTracksAssociatorAtVertex.tracks	= "generalTracks"

	## impact parameter b-tag
	process.ak5PFImpactParameterTagInfos				= process.impactParameterTagInfos.clone()
	process.ak5PFImpactParameterTagInfos.jetTracks		= "ak5PFJetNewTracksAssociatorAtVertex"
	process.ak5PFTrackCountingHighEffBJetTags			= process.trackCountingHighEffBJetTags.clone()
	process.ak5PFTrackCountingHighEffBJetTags.tagInfos	= cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
	process.ak5PFTrackCountingHighPurBJetTags			= process.trackCountingHighPurBJetTags.clone()
	process.ak5PFTrackCountingHighPurBJetTags.tagInfos	= cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
	process.ak5PFJetProbabilityBJetTags					= process.jetProbabilityBJetTags.clone()
	process.ak5PFJetProbabilityBJetTags.tagInfos		= cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
	process.ak5PFJetBProbabilityBJetTags				= process.jetBProbabilityBJetTags.clone()
	process.ak5PFJetBProbabilityBJetTags.tagInfos		= cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))

	## secondary vertex b-tag
	process.ak5PFSecondaryVertexTagInfos					= process.secondaryVertexTagInfos.clone()
	process.ak5PFSecondaryVertexTagInfos.trackIPTagInfos	= "ak5PFImpactParameterTagInfos"
	process.ak5PFSimpleSecondaryVertexBJetTags				= process.simpleSecondaryVertexBJetTags.clone()
	process.ak5PFSimpleSecondaryVertexBJetTags.tagInfos		= cms.VInputTag(cms.InputTag("ak5PFSecondaryVertexTagInfos"))
	process.ak5PFCombinedSecondaryVertexBJetTags			= process.combinedSecondaryVertexBJetTags.clone()
	process.ak5PFCombinedSecondaryVertexBJetTags.tagInfos	= cms.VInputTag(
		cms.InputTag("ak5PFImpactParameterTagInfos"),
		cms.InputTag("ak5PFSecondaryVertexTagInfos")
		)
	process.ak5PFCombinedSecondaryVertexMVABJetTags	   = process.combinedSecondaryVertexMVABJetTags.clone()
	process.ak5PFCombinedSecondaryVertexMVABJetTags.tagInfos = cms.VInputTag(
		cms.InputTag("ak5PFImpactParameterTagInfos"),
		cms.InputTag("ak5PFSecondaryVertexTagInfos")
		)

	## ------------------------------------------------------------------------
	## Definition of sequences

	## run this to create track-jet associations needed for most b-taggers
	process.ak5PFJetTracksAssociator = cms.Sequence(
		process.ak5PFJetNewTracksAssociatorAtVertex
		)

	## run this to create all products needed for impact parameter based
	## b-taggers
	process.ak5PFJetBtaggingIP = cms.Sequence(
		process.ak5PFImpactParameterTagInfos * (
		process.ak5PFTrackCountingHighEffBJetTags +
		process.ak5PFTrackCountingHighPurBJetTags +
		process.ak5PFJetProbabilityBJetTags +
		process.ak5PFJetBProbabilityBJetTags
		))

	## run this to create all products needed for secondary vertex based
	## b-taggers
	process.ak5PFJetBtaggingSV = cms.Sequence(
		process.ak5PFImpactParameterTagInfos *
		process.ak5PFSecondaryVertexTagInfos * (
		process.ak5PFSimpleSecondaryVertexBJetTags +
		process.ak5PFCombinedSecondaryVertexBJetTags +
		process.ak5PFCombinedSecondaryVertexMVABJetTags
		))

	## ------------------------------------------------------------------------
	## B-tagging for (ak5 CHS jets)
	##  - https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets

	## create a ak5PF jets and tracks association
	process.ak5PFCHSNewJetTracksAssociatorAtVertex		= process.ic5JetTracksAssociatorAtVertex.clone()
	process.ak5PFCHSNewJetTracksAssociatorAtVertex.jets   = "ak5PFJetsCHS"
	process.ak5PFCHSNewJetTracksAssociatorAtVertex.tracks = "generalTracks"

	## impact parameter b-tag
	process.ak5PFCHSImpactParameterTagInfos			   = process.impactParameterTagInfos.clone()
	process.ak5PFCHSImpactParameterTagInfos.jetTracks	 = "ak5PFCHSNewJetTracksAssociatorAtVertex"
	process.ak5PFCHSTrackCountingHighEffBJetTags		  = process.trackCountingHighEffBJetTags.clone()
	process.ak5PFCHSTrackCountingHighEffBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
	process.ak5PFCHSTrackCountingHighPurBJetTags		  = process.trackCountingHighPurBJetTags.clone()
	process.ak5PFCHSTrackCountingHighPurBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
	process.ak5PFCHSJetProbabilityBJetTags				= process.jetProbabilityBJetTags.clone()
	process.ak5PFCHSJetProbabilityBJetTags.tagInfos	   = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
	process.ak5PFCHSJetBProbabilityBJetTags			   = process.jetBProbabilityBJetTags.clone()
	process.ak5PFCHSJetBProbabilityBJetTags.tagInfos	  = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))

	## secondary vertex b-tag
	process.ak5PFCHSSecondaryVertexTagInfos				  = process.secondaryVertexTagInfos.clone()
	process.ak5PFCHSSecondaryVertexTagInfos.trackIPTagInfos  = "ak5PFCHSImpactParameterTagInfos"
	process.ak5PFCHSSimpleSecondaryVertexBJetTags			= process.simpleSecondaryVertexBJetTags.clone()
	process.ak5PFCHSSimpleSecondaryVertexBJetTags.tagInfos   = cms.VInputTag(cms.InputTag("ak5PFCHSSecondaryVertexTagInfos"))
	process.ak5PFCHSCombinedSecondaryVertexBJetTags		  = process.combinedSecondaryVertexBJetTags.clone()
	process.ak5PFCHSCombinedSecondaryVertexBJetTags.tagInfos = cms.VInputTag(
		cms.InputTag("ak5PFCHSImpactParameterTagInfos"),
		cms.InputTag("ak5PFCHSSecondaryVertexTagInfos")
		)
	process.ak5PFCHSCombinedSecondaryVertexMVABJetTags	   = process.combinedSecondaryVertexMVABJetTags.clone()
	process.ak5PFCHSCombinedSecondaryVertexMVABJetTags.tagInfos = cms.VInputTag(
		cms.InputTag("ak5PFCHSImpactParameterTagInfos"),
		cms.InputTag("ak5PFCHSSecondaryVertexTagInfos")
		)

	## ------------------------------------------------------------------------
	## Definition of sequences

	## run this to create track-jet associations needed for most b-taggers
	process.ak5PFCHSJetTracksAssociator = cms.Sequence(
		process.ak5PFCHSNewJetTracksAssociatorAtVertex
		)

	## run this to create all products needed for impact parameter based
	## b-taggers
	process.ak5PFCHSJetBtaggingIP = cms.Sequence(
		process.ak5PFCHSImpactParameterTagInfos * (
		process.ak5PFCHSTrackCountingHighEffBJetTags +
		process.ak5PFCHSTrackCountingHighPurBJetTags +
		process.ak5PFCHSJetProbabilityBJetTags +
		process.ak5PFCHSJetBProbabilityBJetTags
		))

	## run this to create all products needed for secondary vertex based
	## b-taggers
	process.ak5PFCHSJetBtaggingSV = cms.Sequence(
		process.ak5PFCHSImpactParameterTagInfos * 
		process.ak5PFCHSSecondaryVertexTagInfos * (
		process.ak5PFCHSSimpleSecondaryVertexBJetTags +
		process.ak5PFCHSCombinedSecondaryVertexBJetTags +
		process.ak5PFCHSCombinedSecondaryVertexMVABJetTags
		))
	"""


	process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')
	process.kappaTuple.Jets = cms.PSet(
		process.kappaNoCut,
		process.kappaNoRegEx,
		taggers = cms.vstring(
			#'QGlikelihood',
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
			#'CombinedSecondaryVertexBJetTags',
			#'CombinedSecondaryVertexMVABJetTags',
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
	process.kappaTuple.PileupDensity.rename = cms.vstring("kt6PFJetsRho => KT6AreaRho", "kt6PFJets => KT6Area")

	process.path *= (
		process.ak5PFJets
		* process.ak5PFJetsCHS
		* process.kt6PFJets
		#* process.makeQGTagging

		#* process.ak5PFJetTracksAssociator
		#* process.ak5PFJetBtaggingIP
		#* process.ak5PFJetBtaggingSV
		#* process.ak5PFCHSJetTracksAssociator
		#* process.ak5PFCHSJetBtaggingIP
		#* process.ak5PFCHSJetBtaggingSV

		#* process.makePUJetID
	)


	############################################################################
	#  MET
	############################################################################

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
	elif cmssw_version_number.startswith("7"):
		# MET correction ----------------------------------------------------------
		#process.load('JetMETCorrections.Type1MET.pfMETCorrectionType0_cfi')
		
		process.load("JetMETCorrections.Type1MET.correctionTermsPfMetType0PFCandidate_cff")
		process.load("JetMETCorrections.Type1MET.correctedMet_cff")
		
		#process.pfchsMETcorr.src = cms.InputTag('goodOfflinePrimaryVertices')
		process.pfMETCHS = process.pfMetT0pc.clone()

		process.path *= (
			process.correctionTermsPfMetType0PFCandidate
			#* process.pfMETcorrType0
			* process.pfMETCHS
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
			'73mc15': {
				'files': 'file:/storage/8/dhaitz/testfiles/DYJetsToLL_M-50_13TeV-madgraph-pythia8__Phys14DR-PU20bx25_PHYS14_25_V1-v1__AODSIM.root',
				'globalTag': 'PHYS14_25_V1',
				'nickName': 'DYJetsToLL_M_50_madgraph_13TeV',
			},
			'740data12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DoubleMuParked__CMSSW_7_4_0_pre9_ROOT6-GR_R_74_V8_1Apr_RelVal_dm2012D-v2__RECO.root',
				'globalTag': 'GR_R_74_V8::All',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
			},
			'742data12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DoubleMuParked__CMSSW_7_4_2-GR_R_74_V12_19May_RelVal_dm2012D-v1__RECO.root',
				'globalTag': 'GR_R_74_V12',
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
