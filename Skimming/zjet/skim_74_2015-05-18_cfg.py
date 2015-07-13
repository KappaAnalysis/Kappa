# Kappa test: CMSSW 7.4.2
# Kappa test: scram arch slc6_amd64_gcc491
# Kappa test: checkout script zjet/checkout74.sh
# Kappa test: output skim74.root

import os

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.kappaparser as kappaparser
from Kappa.Skimming.gc_tools import gc_var_or_callable_parameter

try:
	from hashlib import sha1
except ImportError:
	class sha1(object):
		def __init__(self, *args, **kwargs):
			pass
		def hexdigest(self, *args, **kwargs):
			return "<missing :py:mod:`hashlib.sha1`>"

# concepts for simplifying:
# first set all paramenters (arguments), reduce them, version as tuple
# group by object: basic(HLT, npv, rho), muon, jet+genjet, met
# within group: 1. CMSSW load, 2. CMSSW settings, 3. Kappa settings. (kappa active?) 4. CMSSW path
# can there be better Kappa defaults?
# what is used in common?


def getBaseConfig(
		globaltag,
		testfile,
		maxevents,
		nickname,
		outputfilename,
		channel='mm',
		min_mu_count = 2,
		min_mu_pt = 8.0,
	):

	#  Config parameters  ##############################################
	# get information  ... get gt, etc. here, common?
	cmssw_version = os.environ["CMSSW_VERSION"].split('_')
	cmssw_version = tuple([int(i) for i in cmssw_version[1:4]] + cmssw_version[4:])
	from Configuration.AlCa.autoCond import autoCond
	autostr = ""
	if globaltag.lower() == 'auto':
		globaltag = autoCond['startup']
		autostr = " (from autoCond)"
	data = ('DoubleMu' in testfile[0]) # TODO: improve this!
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
	print "data:           ", data
	print "--------- Parameters ----------"
	print "Min Muon Count: ", min_mu_count
	print "Min Muon pT:    ", min_mu_pt
	# TODO: automatize this somehow?
	print "--------- Checksums ----------"
	print "Parameter SHA1: ", sha1("min_mu_count=%s, min_mu_pt=%s"%(min_mu_count, min_mu_pt)).hexdigest()
	print "---------------------------------"
	print


	#  Basic Process Setup  ############################################
	process = cms.Process("KAPPA")
	process.path = cms.Path()
	process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(maxevents))
	process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
	process.source = cms.Source("PoolSource",
		fileNames = cms.untracked.vstring(testfile)
	)
	# message logger
	process.load("FWCore.MessageLogger.MessageLogger_cfi")
	process.MessageLogger.cerr.FwkReport.reportEvery = 50
	process.MessageLogger.default = cms.untracked.PSet(
		ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5))
	)

	## Geometry and Detector Conditions (needed for a few patTuple production steps)
	if cmssw_version > (7, 4, 0, 'pre8'):
		# https://twiki.cern.ch/twiki/bin/view/Sandbox/MyRootMakerFrom72XTo74X#DDVectorGetter_vectors_are_empty
		print "Use condDBv2 and GeometryRecoDB:"
		process.load("Configuration.Geometry.GeometryRecoDB_cff")
		process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
	else:
		process.load("Configuration.Geometry.GeometryIdeal_cff")
		process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
	process.load("Configuration.StandardSequences.MagneticField_cff")
	process.GlobalTag.globaltag = cms.string(globaltag)


	#  Kappa  ##########################################################
	process.load('Kappa.Producers.KTuple_cff')
	process.kappaTuple = cms.EDAnalyzer('KTuple',
		process.kappaTupleDefaultsBlock,
		outputFile = cms.string(outputfilename),
	)
	process.kappaTuple.verbose = 0
	process.kappaOut = cms.Sequence(process.kappaTuple)
	process.kappaTuple.active = cms.vstring('VertexSummary', 'BeamSpot')
	if data:
		process.kappaTuple.active += cms.vstring('DataInfo')
	else:
		process.kappaTuple.active += cms.vstring('GenInfo', 'GenParticles')
		process.kappaTuple.Info.hltSource = ""
		process.kappaTuple.Info.l1Source = ""
		process.kappaTuple.Info.hlTrigger = ""
		process.kappaTuple.Info.noiseHCAL = ""

	if cmssw_version >= (7, 4, 0):
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)

	if channel == 'mm':
		process.kappaTuple.Info.hltWhitelist = cms.vstring(
			# HLT regex selection can be tested at https://regex101.com (with gm options)
			# single muon triggers, e.g. HLT_Mu50_v1
			"^HLT_(Iso)?(Tk)?Mu[0-9]+(_eta2p1|_TrkIsoVVL)?_v[0-9]+$",
			# double muon triggers, e.g. HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v1
			"^HLT_Mu[0-9]+(_TrkIsoVVL)?_(Tk)?Mu[0-9]+(_TrkIsoVVL)?(_DZ)?_v[0-9]+$",
		)


	#  PFCandidates  ###################################################
	## Good offline PV selection: 
	from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
	process.goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
		filterParams = pvSelector.clone(maxZ = 24.0), # ndof >= 4, rho <= 2
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
		#* process.goodOfflinePrimaryVertexEvents
		* process.pfParticleSelectionSequence
	)

	#  Muons  ##########################################################
	if channel == 'mm':
		process.load('Kappa.Skimming.KMuons_run2_cff')
		process.muPreselection1 = cms.EDFilter('CandViewSelector',
			src = cms.InputTag('muons'),
			cut = cms.string("pt > %.2f"%min_mu_pt),
		)
		process.muPreselection2 = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('muPreselection1'),
			minNumber = cms.uint32(min_mu_count),
		)
		process.kappaTuple.Muons.minPt = 8.0
		process.kappaTuple.active += cms.vstring('Muons')

		process.path *= (process.muPreselection1 * process.muPreselection2 * process.makeKappaMuons)
	
	# Electrons ########################################################
	# to be done
	if channel == 'ee':
		pass

	#  Jets  ###########################################################
	## PFBRECO?
	process.load("RecoJets.JetProducers.ak5PFJets_cfi")
	base_jet = process.ak5PFJets.clone(srcPVs = 'goodOfflinePrimaryVertices')

	## PUPPI
	# creates reweighted PFCandidates collection 'puppi'
	process.load('CommonTools.PileupAlgos.Puppi_cff')
	if miniaod:
		process.puppi.candName = cms.InputTag('packedPFCandidates')
		process.puppi.vertexName = cms.InputTag('offlineSlimmedPrimaryVertices')


	cmssw_jets = {}  # algo: cmssw module
	kappa_jets = {}  # algo: kappa jet config
	# create Jet variants
	for param in (4, 5, 8):
		for variant, input_tag in (("", 'particleFlow'), ("CHS", 'pfNoPileUp'), ("Puppi", 'puppi')):
			# CMSSW module
			variant_name = "ak%dPFJets%s" % (param, variant)
			variant_mod = base_jet.clone()
			variant_mod.rParam   = param / 10.0
			variant_mod.radiusPU = param / 10.0
			variant_mod.src = cms.InputTag(input_tag)
			variant_mod.doAreaFastjet = True
			setattr(process, variant_name, variant_mod)
			cmssw_jets[variant_name] = variant_mod
			# Kappa output object
			kappa_jets["ak%dPFJets%s"%(param, variant)] = cms.PSet(
				src = cms.InputTag(variant_name),
				PUJetID = cms.InputTag("ak%dPF%sPuJetMva" % (param, variant)),
				PUJetID_full = cms.InputTag("full"),
				QGtagger = cms.InputTag("AK%dPFJets%sQGTagger" % (param, variant)),
				Btagger = cms.InputTag("ak%dPF%s" % (param, variant)),
			)
			# add gen jets?

	process.path *= process.puppi * reduce(lambda a, b: a * b, sorted(cmssw_jets.values()))

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

	# add kt6PFJets for PileupDensity
	from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
	process.kt6PFJets = kt4PFJets.clone(rParam=0.6, doRhoFastjet=True, Rho_EtaMax=2.5)

	process.kappaTuple.Jets.taggers = cms.vstring(
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
			)
	process.kappaTuple.Jets.minPt = 5.0
	# load autogenerated jets
	for name, pset in kappa_jets.iteritems():
		setattr(process.kappaTuple.Jets, name, pset)
	process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')

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
		process.kappaTuple.LV.whitelist = cms.vstring('ak5GenJetsNoNu') #default?




	process.path *= (
        # AK jets currently auto-loaded on instantiation
		#process.ak5PFJets
		#* process.ak5PFJetsCHS
		process.kt6PFJets

		#* process.ak5PFJetTracksAssociator
		#* process.ak5PFJetBtaggingIP
		#* process.ak5PFJetBtaggingSV
		#* process.ak5PFCHSJetTracksAssociator
		#* process.ak5PFCHSJetBtaggingIP
		#* process.ak5PFCHSJetBtaggingSV

		#* process.makePUJetID
	)

	# MET ##############################################################

	#TODO check type 0 corrections
	# MET correction ----------------------------------------------------------		
	process.load("JetMETCorrections.Type1MET.correctionTermsPfMetType0PFCandidate_cff")
	process.load("JetMETCorrections.Type1MET.correctedMet_cff")
	
	process.pfMETCHS = process.pfMetT0pc.clone()

	process.kappaTuple.active += cms.vstring('MET')					   ## produce/save KappaPFMET
	process.kappaTuple.MET.whitelist = cms.vstring('pfChMet', '_pfMet_', 'pfMETCHS') # defaults!!

	process.path *= (
		process.correctionTermsPfMetType0PFCandidate
		#* process.pfMETcorrType0
		* process.pfMETCHS
	)


	#  Kappa  ##########################################################
	# process.kappaTuple.active = []
	process.path *= (
		process.kappaOut
	)
	# final information:
	print "------- CONFIGURATION 2 ---------"
	print "CMSSW producers:"
	for p in str(process.path).split('+'):
		print "  %s" % p
	print "Kappa producers:", ", ".join(sorted(process.kappaTuple.active))
	print "---------------------------------"
	#print process.selectedVerticesForPFMEtCorrType0.dumpPython()
	#print process.selectedPrimaryVertexHighestPtTrackSumForPFMEtCorrType0.dumpPython()
	#print process.goodOfflinePrimaryVertices.dumpPython()
	return process


if __name__ == '__main__':
	# run local skim by hand without replacements by grid-control
	if('@' in '@NICK@'):

		KappaParser = kappaparser.KappaParserZJet()
		KappaParser.setDefault('test', '742data12')
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
			'742data15': {
				'files': 'root://xrootd-cms.infn.it//store/data/Run2015A/DoubleMuon/AOD/PromptReco-v1/000/248/038/00000/E8F5583C-6914-E511-A613-02163E0140E8.root',
				'globalTag': 'GR_R_74_V12',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
			},
		}
		KappaParser.parseArgumentsWithTestDict(testdict)

		process = getBaseConfig(
			globaltag=KappaParser.globalTag,
			testfile=KappaParser.files,
			maxevents=KappaParser.maxEvents,
			nickname=KappaParser.nickName,
			outputfilename="skim74.root",
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
			channel = gc_var_or_callable_parameter(gc_var_name='@CHANNEL@',callable=getBaseConfig),
			min_mu_count = gc_var_or_callable_parameter(gc_var_name='@MIN_MU_COUNT@',callable=getBaseConfig),
			min_mu_pt = gc_var_or_callable_parameter(gc_var_name='@MIN_MU_PT@',callable=getBaseConfig),
		)
