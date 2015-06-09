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
	process.path = cms.Path()

	## MessageLogger
	process.load("FWCore.MessageLogger.MessageLogger_cfi")
	process.MessageLogger.default = cms.untracked.PSet(
		ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5))
	)
	process.MessageLogger.cerr.FwkReport.reportEvery = 50

	# general options
	process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
	process.source = cms.Source("PoolSource",
		fileNames = cms.untracked.vstring()
	)
	data = datasetsHelper.isData(nickname)
	centerOfMassEnergy = datasetsHelper.getCenterOfMassEnergy(nickname)
	process.source.fileNames	= testfile
	process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(maxevents))
	process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )

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
	process.load("Configuration.StandardSequences.MagneticField_cff")

	if globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag = cms.string(autoCond['startup'])
		print "GT from autoCond:", process.GlobalTag.globaltag
	else:
		process.GlobalTag.globaltag = globaltag


	############################################################################
	#  KAPPA
	############################################################################
	process.load('Kappa.Producers.KTuple_cff')
	process.kappaTuple = cms.EDAnalyzer('KTuple',
		process.kappaTupleDefaultsBlock,
		outputFile = cms.string("kappaTuple.root"),
	)
	process.kappaTuple.active = cms.vstring()
	process.kappaTuple.outputFile = outputfilename
	process.kappaTuple.verbose	= cms.int32(kappaverbosity)
	process.kappaTuple.profile	= cms.bool(False)
	process.kappaOut = cms.Sequence(process.kappaTuple)

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
	process.kappaTuple.active += cms.vstring('VertexSummary')
	process.kappaTuple.VertexSummary.whitelist = cms.vstring('goodOfflinePrimaryVertices')
	#process.kappaTuple.active += cms.vstring('BeamSpot')
	#process.kappaTuple.active += cms.vstring('TriggerObjects')
	if data:
		process.kappaTuple.active+= cms.vstring('DataInfo')
	else:
		process.kappaTuple.active+= cms.vstring('GenInfo')
		process.kappaTuple.active+= cms.vstring('GenParticles')
		#process.kappaTuple.Info.hltSource = ""

	if cmssw_version_number.startswith("7_4_2") or cmssw_version_number.startswith("7_4_0"):
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)

	if channel == 'mm':
		process.kappaTuple.Info.hltWhitelist = cms.vstring(
			## HLT selection
			# can be tested at http://regexpal.com
			# matches 'HLT_Mu17_Mu8_v7' etc.
			'^HLT_(Double)?Mu([0-9]+)_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$',
			# matches 'HLT_DoubleMu7_v8' etc.
			'^HLT_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$',
			)


	############################################################################
	#  PFCandidates
	############################################################################
	## ------------------------------------------------------------------------
	## Good offline PV selection: 
	from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector

	process.goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
		src = cms.InputTag('offlinePrimaryVertices'),
		filterParams = pvSelector.clone( minNdof = 4.0, maxZ = 24.0 ),
	)

	process.goodOfflinePrimaryVertexEvents = cms.EDFilter("KVertexFilter",
		minNumber = cms.uint32(1),
		maxNumber = cms.uint32(999999),
		src = cms.InputTag("goodOfflinePrimaryVertices")
	)

	## ------------------------------------------------------------------------
	## TopProjections from CommonTools/ParticleFlow:
	process.load("CommonTools.ParticleFlow.pfNoPileUpIso_cff")
	process.load("CommonTools.ParticleFlow.pfNoPileUpIso_cff")
	process.load("CommonTools.ParticleFlow.pfParticleSelection_cff")


	## pf candidate configuration for everything but CHS jets
	process.pfPileUpIso.PFCandidates		= 'particleFlow'
	process.pfPileUpIso.Vertices			= 'goodOfflinePrimaryVertices'
	process.pfPileUpIso.checkClosestZVertex	= True
	process.pfNoPileUpIso.bottomCollection	= 'particleFlow'


	## pf candidate configuration for deltaBeta corrections for muons and electrons 
	process.pfNoPileUpChargedHadrons	= process.pfAllChargedHadrons.clone()
	process.pfNoPileUpNeutralHadrons	= process.pfAllNeutralHadrons.clone()
	process.pfNoPileUpPhotons			= process.pfAllPhotons.clone()
	process.pfPileUpChargedHadrons		= process.pfAllChargedHadrons.clone(src = 'pfPileUpIso')

	## pf candidate configuration for CHS jets
	process.pfPileUp.Vertices				= 'goodOfflinePrimaryVertices'
	process.pfPileUp.checkClosestZVertex	= False

	# Modifications for new particleFlow Pointers
	process.pfPileUp.PFCandidates = cms.InputTag("particleFlowPtrs")
	process.pfPileUpIso.PFCandidates = cms.InputTag("particleFlowPtrs")
	process.pfNoPileUp.bottomCollection = cms.InputTag("particleFlowPtrs")
	process.pfNoPileUpIso.bottomCollection = cms.InputTag("particleFlowPtrs")
	#process.pfJetTracksAssociatorAtVertex.jets= cms.InputTag("ak5PFJets")
	process.path *= (
		process.goodOfflinePrimaryVertices
		* process.goodOfflinePrimaryVertexEvents
		* process.pfParticleSelectionSequence
	)


	if channel == 'mm':
		############################################################################
		#  Muons
		############################################################################
		process.load('Kappa.Skimming.KMuons_run2_cff')

		process.kappaTuple.active += cms.vstring('Muons')
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


	############################################################################
	#  Jets
	############################################################################
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

	# GenJets
	if not data:
		process.load('RecoJets.Configuration.GenJetParticles_cff')
		process.load('RecoJets.Configuration.RecoGenJets_cff')
		process.load('RecoJets.JetProducers.ak5GenJets_cfi')
		process.path *= (
			process.genParticlesForJetsNoNu *
			process.ak5GenJetsNoNu
		)
		process.kappaTuple.active += cms.vstring('LV')
		process.kappaTuple.LV.rename = cms.vstring('ak => AK')
		process.kappaTuple.LV.whitelist = cms.vstring('ak5GenJetsNoNu')

	# add kt6PFJets for PileupDensity
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
	process.kappaTuple.MET.whitelist = cms.vstring('pfChMet', '_pfMet_', 'pfMETCHS')

	# MET correction ----------------------------------------------------------		
	process.load("JetMETCorrections.Type1MET.correctionTermsPfMetType0PFCandidate_cff")
	process.load("JetMETCorrections.Type1MET.correctedMet_cff")
	
	process.pfMETCHS = process.pfMetT0pc.clone()

	process.path *= (
		process.correctionTermsPfMetType0PFCandidate
		#* process.pfMETcorrType0
		* process.pfMETCHS
	)


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
				'globalTag': 'GR_R_74_V8',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
			},
			'742data12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DoubleMuParked__CMSSW_7_4_2-GR_R_74_V12_19May_RelVal_dm2012D-v1__RECO.root',
				'globalTag': 'GR_R_74_V12',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
			},
			'742mc15': {
				#'files': 'file:/storage/8/dhaitz/testfiles/DoubleMuParked__CMSSW_7_4_2-GR_R_74_V12_19May_RelVal_dm2012D-v1__RECO.root',
				'files': 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/StartupFlat10to50bx50Raw_MCRUN2_74_V8-v1/10000/04CA79E8-8201-E511-9D9C-0025905A60AA.root',
				'globalTag': 'MCRUN2_74_V8',
				'nickName': 'DYJetsToLL_M_50_madgraph_13TeV',
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
