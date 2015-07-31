# Kappa test: CMSSW 7.4.6.patch5
# Kappa test: scram arch slc6_amd64_gcc491
# Kappa test: checkout script zjet/checkout74.sh
# Kappa test: output skim74.root

import os

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.kappaparser as kappaparser
from Kappa.Skimming.gc_tools import gc_var_or_callable_parameter


def baseconfig(
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
		data = ('DoubleMu' in testfile[0]) or ('SingleMu' in testfile[0])
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

	#  Basic Process Setup  ############################################
	process = cms.Process("KAPPA")
	process.path = cms.Path()
	process.maxEvents = cms.untracked.PSet(
		input=cms.untracked.int32(maxevents)
	)
	process.options = cms.untracked.PSet(
		wantSummary=cms.untracked.bool(True)
	)
	process.source = cms.Source("PoolSource",
		fileNames=cms.untracked.vstring(testfile)
	)
	# message logger
	process.load("FWCore.MessageLogger.MessageLogger_cfi")
	process.MessageLogger.cerr.FwkReport.reportEvery = 50
	process.MessageLogger.default = cms.untracked.PSet(
		ERROR=cms.untracked.PSet(limit=cms.untracked.int32(5))
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
		filterParams = pvSelector.clone(maxZ = 24.0),  # ndof >= 4, rho <= 2
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
			cut = cms.string("pt >8.0"),
		)
		process.muPreselection2 = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('muPreselection1'),
			minNumber = cms.uint32(2),
		)
		process.kappaTuple.Muons.minPt = 8.0
		process.kappaTuple.active += cms.vstring('Muons')

		process.path *= (process.muPreselection1 * process.muPreselection2 * process.makeKappaMuons)

	# Electrons ########################################################
	# to be done
	if channel == 'ee':
		pass

	#  Jets  ###########################################################
	# Kappa jet processing
	process.kappaTuple.Jets.minPt = 5.0
	process.kappaTuple.Jets.taggers = cms.vstring()

	# containers of objects to process
	jet_resources = []
	cmssw_jets = {}  # algoname: cmssw module
	kappa_jets = {}  # algoname: kappa jet config

	# GenJets
	if not data:
		process.load('RecoJets.Configuration.GenJetParticles_cff')
		process.load('RecoJets.JetProducers.ak5GenJets_cfi')
		jet_resources.append(process.genParticlesForJetsNoNu)
		process.kappaTuple.active += cms.vstring('LV')
		process.kappaTuple.LV.whitelist = cms.vstring('ak5GenJetsNoNu') #default?
		genbase_jet = process.ak5GenJets.clone(src=cms.InputTag("genParticlesForJetsNoNu"), doAreaFastjet=True)

	## PFBRECO?
	process.load("RecoJets.JetProducers.ak5PFJets_cfi")
	pfbase_jet = process.ak5PFJets.clone(srcPVs = 'goodOfflinePrimaryVertices', doAreaFastjet=True)

	## PUPPI
	# creates reweighted PFCandidates collection 'puppi'
	process.load('CommonTools.PileupAlgos.Puppi_cff')
	jet_resources.append(process.puppi)
	if miniaod:
		process.puppi.candName = cms.InputTag('packedPFCandidates')
		process.puppi.vertexName = cms.InputTag('offlineSlimmedPrimaryVertices')

	# create Jet variants
	for param in (4, 5, 8):
		# PFJets
		for algo, input_tag in (("", 'particleFlow'), ("CHS", 'pfNoPileUp'), ("Puppi", 'puppi')):
			variant_name = "ak%dPFJets%s" % (param, algo)
			variant_mod = pfbase_jet.clone(src=cms.InputTag(input_tag), rParam=param/10.0)
			cmssw_jets[variant_name] = variant_mod
			# Full Kappa jet definition
			kappa_jets["ak%dPFJets%s"%(param, algo)] = cms.PSet(
				src = cms.InputTag(variant_name),
				PUJetID = cms.InputTag("ak%dPF%sPuJetMva" % (param, algo)),
				PUJetID_full = cms.InputTag("full"),
				QGtagger = cms.InputTag("AK%dPFJets%sQGTagger" % (param, algo)),
				Btagger = cms.InputTag("ak%dPF%s" % (param, algo)),
			)
		# GenJets
		if not data:
			for collection in ("NoNu",): # TODO: add "NoMuNoNu", "" ?
				variant_name = "ak%sGenJets%s" % (param, collection)
				variant_mod = genbase_jet.clone(rParam=param/10.0)
				cmssw_jets[variant_name] = variant_mod
				# GenJets are just KLVs
				process.kappaTuple.LV.whitelist += cms.vstring(variant_name)
	# mount generated jets for processing
	for name, jet_module in cmssw_jets.iteritems():
		setattr(process, name, jet_module)
	for name, pset in kappa_jets.iteritems():
		setattr(process.kappaTuple.Jets, name, pset)
	process.path *= reduce(lambda a, b: a * b, jet_resources) * reduce(lambda a, b: a * b, sorted(cmssw_jets.values()))

	# Gluon tagging? - https://twiki.cern.ch/twiki/bin/viewauth/CMS/GluonTag

	# B-tagging (for ak5 jets)? - https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets

	# B-tagging for (ak5 CHS jets)? - https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets

	# PileupDensity ########################
	from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
	process.pileupDensitykt6PFJets = kt4PFJets.clone(rParam=0.6, doRhoFastjet=True, Rho_EtaMax=2.5)

	process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')
	process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")

	process.path *= (
		process.pileupDensitykt6PFJets
	)

	# MET correction ----------------------------------------------------------
	#TODO check type 0 corrections
	process.load("JetMETCorrections.Type1MET.correctionTermsPfMetType0PFCandidate_cff")
	process.load("JetMETCorrections.Type1MET.correctedMet_cff")

	process.pfMETCHS = process.pfMetT0pc.clone()
	# Puppi
	from RecoMET.METProducers.PFMET_cfi import pfMet
	process.pfMetPuppi = pfMet.clone(src=cms.InputTag('puppi'))

	process.kappaTuple.active += cms.vstring('MET')

	process.path *= (
		process.correctionTermsPfMetType0PFCandidate
		* process.pfMetPuppi
		* process.pfMETCHS
	)

	#  Kappa  Output ###########################################################
	process.path *= (
		process.kappaOut
	)
	# final information:
	print "------- CONFIGURATION 2 ---------"
	print "CMSSW producers:"
	for p in str(process.path).split('+'):
		print "  %s" % p
	print "Kappa producers:"
	for p in sorted(process.kappaTuple.active):
		print "  %s" % p
	print "---------------------------------"
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
				'channel': 'mm',
			},
			'53mc12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball__Summer12_DR53X-PU_RD1_START53_V7N-v1__AODSIM.root',
				'globalTag': 'START53_V27::All',
				'nickName': 'DYJetsToLL_M_50_madgraph_8TeV',
				'channel': 'mm',
			},
			'73mc15': {
				'files': 'file:/storage/8/dhaitz/testfiles/DYJetsToLL_M-50_13TeV-madgraph-pythia8__Phys14DR-PU20bx25_PHYS14_25_V1-v1__AODSIM.root',
				'globalTag': 'PHYS14_25_V1',
				'nickName': 'DYJetsToLL_M_50_madgraph_13TeV',
				'channel': 'mm',
			},
			'740data12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DoubleMuParked__CMSSW_7_4_0_pre9_ROOT6-GR_R_74_V8_1Apr_RelVal_dm2012D-v2__RECO.root',
				'globalTag': 'GR_R_74_V8',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
				'channel': 'mm',
			},
			'742data12': {
				'files': 'file:/storage/8/dhaitz/testfiles/DoubleMuParked__CMSSW_7_4_2-GR_R_74_V12_19May_RelVal_dm2012D-v1__RECO.root',
				'globalTag': 'GR_R_74_V12',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
				'channel': 'mm',
			},
			'742mc15': {
				'files': 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/StartupFlat10to50bx50Raw_MCRUN2_74_V8-v1/10000/04CA79E8-8201-E511-9D9C-0025905A60AA.root',
				'globalTag': 'MCRUN2_74_V8',
				'nickName': 'DYJetsToLL_M_50_madgraph_13TeV',
				'channel': 'mm',
			},
			'742data15': {
				'files': '/store/relval/CMSSW_7_4_2/DoubleMuParked/RECO/GR_R_74_V12_19May_RelVal_dm2012D-v1/00000/72D89F3B-63FE-E411-B920-0025905A612E.root',
				'globalTag': 'GR_R_74_V12',
				'nickName': 'DoubleMu_Run2012A_22Jan2013_8TeV',
				'channel': 'mm',
			},
		}
		KappaParser.parseArgumentsWithTestDict(testdict)

		process = baseconfig(
			globaltag=KappaParser.globalTag,
			testfile=KappaParser.files,
			maxevents=KappaParser.maxEvents,
			nickname=KappaParser.nickName,
			outputfilename="skim74.root",
			channel=KappaParser.channel,
		)
	## for grid-control:
	else:
		process = baseconfig(
			globaltag='@GLOBALTAG@',
			testfile=cms.untracked.vstring('@FILE_NAMES@'.strip('"').split('", "')),
			maxevents=-1,
			nickname='@NICK@',
			outputfilename='kappatuple.root',
			channel = gc_var_or_callable_parameter(gc_var_name='@CHANNEL@', callable=baseconfig),
			is_data = gc_var_or_callable_parameter(gc_var_name='@IS_DATA@', callable=baseconfig),
		)
