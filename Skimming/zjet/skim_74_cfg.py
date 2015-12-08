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
		input_files,
		maxevents,
		nickname,
		outputfilename,
		channel='mm',
		is_data=None,
	):
	"""
	Create the CMSSW/cmsRun config for the z+jet skim

	:param globaltag: CMS global tag for the data
	:param globaltag: str
	:param input_files: files to process
	:type input_files: list[str]
	:param maxevents: number of events to process; `-1` implies all events
	:type maxevents: int
	:param nickname: nickname of the skim
	:type nickname: str
	:param channel: decay channel of Z; either of `mm` , `em`, `ee`
	:type channel: str
	:param is_data: whether input is data or simulated; use `None` for autodetection
	:type is_data: bool or None
	"""

	#  Config parameters  ##############################################
	cmssw_version = os.environ["CMSSW_VERSION"].split('_')
	cmssw_version = tuple([int(i) for i in cmssw_version[1:4]] + cmssw_version[4:])
	autostr = ""
	if globaltag.lower() == 'auto':
		from Configuration.AlCa.autoCond import autoCond
		globaltag = autoCond['startup']
		autostr = " (from autoCond)"
	if is_data is None:
		data = ('Double' in input_files[0]) or ('Single' in input_files[0])
	else:
		data = is_data
	miniaod = False
	add_puppi = (channel == 'mm')

	## print information
	print "\n------- CONFIGURATION 1 ---------"
	print "input:          ", input_files[0], "... (%d files)" % len(input_files) if len(input_files) > 1 else ""
	print "file type:      ", "miniAOD" if miniaod else "AOD"
	print "data:           ", data
	print "output:         ", outputfilename
	print "nickname:       ", nickname
	print "global tag:     ", globaltag + autostr
	print "max events:     ", maxevents if maxevents >= 0 else "all"
	print "cmssw version:  ", '.'.join([str(i) for i in cmssw_version])
	print "channel:        ", channel
	print "add_puppi:      ", add_puppi
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
		fileNames=cms.untracked.vstring(input_files)
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
	elif channel == 'ee':
		process.kappaTuple.Info.hltWhitelist = cms.vstring(
			"^HLT_Ele[0-9]+_Ele[0-9]+(_CaloIdL)?(_TrackIdL)?(_IsoVL)?(_DZ)?_v[0-9]+$",
		)

	# Primary Input Collections ###################################################
	## miniAOD has NOT been tested, I'm just guessing names - MF@20150907
	if miniaod:
		input_PFCandidates = 'packedPFCandidates'
		input_PFCandidatePtrs = 'packedPFCandidatesPtrs'
		input_PrimaryVertices = 'offlineSlimmedPrimaryVertices'
	else:
		input_PFCandidates = 'particleFlow'
		input_PFCandidatePtrs = 'particleFlowPtrs'
		input_PrimaryVertices = 'goodOfflinePrimaryVertices'


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
	process.pfPileUpIso.PFCandidates		= cms.InputTag(input_PFCandidates)
	process.pfPileUpIso.Vertices			= cms.InputTag(input_PrimaryVertices)
	process.pfPileUpIso.checkClosestZVertex	= True
	process.pfNoPileUpIso.bottomCollection	= cms.InputTag(input_PFCandidates)


	## pf candidate configuration for deltaBeta corrections for muons and electrons 
	process.pfNoPileUpChargedHadrons	= process.pfAllChargedHadrons.clone()
	process.pfNoPileUpNeutralHadrons	= process.pfAllNeutralHadrons.clone()
	process.pfNoPileUpPhotons			= process.pfAllPhotons.clone()
	process.pfPileUpChargedHadrons		= process.pfAllChargedHadrons.clone(src = 'pfPileUpIso')

	## pf candidate configuration for CHS jets
	process.pfPileUp.Vertices				= cms.InputTag(input_PrimaryVertices)
	process.pfPileUp.checkClosestZVertex	= False

	# Modifications for new particleFlow Pointers
	process.pfPileUp.PFCandidates = cms.InputTag(input_PFCandidatePtrs)
	process.pfPileUpIso.PFCandidates = cms.InputTag(input_PFCandidatePtrs)
	process.pfNoPileUp.bottomCollection = cms.InputTag(input_PFCandidatePtrs)
	process.pfNoPileUpIso.bottomCollection = cms.InputTag(input_PFCandidatePtrs)
	process.path *= (
		process.goodOfflinePrimaryVertices
		* process.pfParticleSelectionSequence
	)

	if add_puppi:
		## PUPPI - https://twiki.cern.ch/twiki/bin/viewauth/CMS/PUPPI
		# creates filtered PFCandidates collection 'puppi'
		process.load('CommonTools.PileupAlgos.Puppi_cff')
		process.puppi.candName = cms.InputTag(input_PFCandidates)
		process.puppi.vertexName = cms.InputTag(input_PrimaryVertices)
		# PFCandidates w/o muons for PUPPI - avoid misidentification from high-PT muons
		process.PFCandidatesNoMu  = cms.EDFilter("CandPtrSelector",
			src = cms.InputTag(input_PFCandidates),
			cut = cms.string("abs(pdgId)!=13" )
		)
		process.PFCandidatesOnlyMu  = cms.EDFilter("CandPtrSelector",
			src = cms.InputTag(input_PFCandidates),
			cut = cms.string("abs(pdgId)==13" )
		)
		# veto without any muons
		process.puppinomutmp = process.puppi.clone(
			candName = cms.InputTag('PFCandidatesNoMu')
		)
		# nomu veto, muons merged back again for proper MET etc.
		process.puppinomu = cms.EDProducer("CandViewMerger",
			src = cms.VInputTag( "puppinomutmp", "PFCandidatesOnlyMu")
		)
		process.path *= (process.puppi * (process.PFCandidatesNoMu * process.PFCandidatesOnlyMu * process.puppinomutmp * process.puppinomu))

	#  Muons  ##########################################################
	if channel == 'mm':
		process.load('Kappa.Skimming.KMuons_run2_cff')
		process.muPreselection1 = cms.EDFilter('CandViewSelector',
			src = cms.InputTag('muons'),
			cut = cms.string("pt>8.0"),
		)
		process.muPreselection2 = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('muPreselection1'),
			minNumber = cms.uint32(2),
		)
		process.kappaTuple.Muons.minPt = 8.0
		process.kappaTuple.Muons.doPfIsolation = cms.bool(False)
		process.kappaTuple.active += cms.vstring('Muons')

		process.path *= (process.muPreselection1 * process.muPreselection2 * process.makeKappaMuons)

	# Electrons ########################################################
	elif channel == 'ee':
		process.load('Kappa.Skimming.KElectrons_run2_cff')
		process.ePreselection1 = cms.EDFilter('CandViewSelector',
			src = cms.InputTag('patElectrons'),
			cut = cms.string("pt>8.0"),
		)
		process.ePreselection2 = cms.EDFilter('CandViewCountFilter',
			src = cms.InputTag('ePreselection1'),
			minNumber = cms.uint32(2),
		)
		process.kappaTuple.Electrons.minPt = 8.0

		from Kappa.Skimming.KElectrons_run2_cff import setupElectrons
		process.kappaTuple.Electrons.ids = cms.vstring("cutBasedElectronID_Spring15_25ns_V1_standalone_loose",
								 	 "cutBasedElectronID_Spring15_25ns_V1_standalone_medium",
								 	 "cutBasedElectronID_Spring15_25ns_V1_standalone_tight",
								 	 "cutBasedElectronID_Spring15_25ns_V1_standalone_veto",
								 "ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values")
		setupElectrons(process)

		process.kappaTuple.active += cms.vstring('Electrons')
		process.path *= (process.makeKappaElectrons * process.ePreselection1 * process.ePreselection2)

	#  Jets  ###########################################################
	# Kappa jet processing
	process.kappaTuple.Jets.minPt = 5.0
	process.kappaTuple.Jets.taggers = cms.vstring()

	# containers for objects to process
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

	# create Jet variants
	for param in (4, 5, 8):
		# PFJets
		algos_and_tags = [("", input_PFCandidates), ("CHS", 'pfNoPileUp')]
		if add_puppi:
			algos_and_tags += [("Puppi", 'puppi'),("PuppiNoMu", 'puppinomu')]
		for algo, input_tag in algos_and_tags:
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
	process.path *= reduce(lambda a, b: a * b, jet_resources + sorted(cmssw_jets.values()))

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
	from RecoMET.METProducers.PFMET_cfi import pfMet
	process.pfMETCHS = pfMet.clone(src=cms.InputTag(input_PFCandidates))
	process.kappaTuple.active += cms.vstring('MET')

	# MET without forward region
	process.PFCandidatesNoHF  = cms.EDFilter("CandPtrSelector",
		src = cms.InputTag(input_PFCandidates),
		cut = cms.string("abs(eta) < 3" )
	)
	process.pfMETCHSNoHF = pfMet.clone(src=cms.InputTag('PFCandidatesNoHF'))
	process.path *= (process.pfMETCHS * process.PFCandidatesNoHF * process.pfMETCHSNoHF)

	if add_puppi:
		process.pfMetPuppi = pfMet.clone(src=cms.InputTag('puppi'))
		process.pfMetPuppiNoMu = pfMet.clone(src=cms.InputTag('puppinomu'))
		process.path *= (
			process.pfMetPuppi
			* process.pfMetPuppiNoMu
		)
		process.PuppiNoHF  = cms.EDFilter("CandPtrSelector",
			src = cms.InputTag('puppi'),
			cut = cms.string("abs(eta) < 3" )
		)
		process.PuppiNoMuNoHF  = cms.EDFilter("CandPtrSelector",
			src = cms.InputTag('puppinomu'),
			cut = cms.string("abs(eta) < 3" )
		)
		process.pfMetPuppiNoHF = pfMet.clone(src=cms.InputTag('PuppiNoHF'))
		process.pfMetPuppiNoMuNoHF = pfMet.clone(src=cms.InputTag('PuppiNoMuNoHF'))
		process.path *= (
			process.PuppiNoHF * process.pfMetPuppiNoHF
			* process.PuppiNoMuNoHF * process.pfMetPuppiNoMuNoHF
		)

		process.kappaTuple.MET.whitelist += cms.vstring('pfMetPuppiNoHF', 'pfMetPuppiNoMuNoHF')


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
	if '@' in '@NICK@':
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
			'742mc15ee': {
				#'files': 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/Asympt50ns_MCRUN2_74_V9A-v2/00000/0033A97B-8707-E511-9D3B-008CFA1980B8.root',
				'files': 'file:/storage/8/dhaitz/testfiles/mc15_ee.root',
				'globalTag': 'MCRUN2_74_V8',
				'nickName': 'DYJetsToLL_M_50_madgraph_13TeV',
				'channel': 'ee',
			},
		}
		KappaParser.parseArgumentsWithTestDict(testdict)

		process = baseconfig(
			globaltag=KappaParser.globalTag,
			input_files=KappaParser.files,
			maxevents=KappaParser.maxEvents,
			nickname=KappaParser.nickName,
			outputfilename="skim74.root",
			channel=KappaParser.channel,
		)
	## for grid-control:
	else:
		process = baseconfig(
			globaltag='@GLOBALTAG@',
			input_files=cms.untracked.vstring('@FILE_NAMES@'.strip('"').split('", "')),
			maxevents=-1,
			nickname='@NICK@',
			outputfilename='kappatuple.root',
			channel = gc_var_or_callable_parameter(gc_var_name='@CHANNEL@', callable=baseconfig),
			is_data = gc_var_or_callable_parameter(gc_var_name='@IS_DATA@', callable=baseconfig),
		)
