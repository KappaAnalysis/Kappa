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
	#process.kappaTuple.active += cms.vstring('VertexSummary')	## save VertexSummary,
	#process.kappaTuple.VertexSummary.whitelist = cms.vstring('goodOfflinePrimaryVertices')
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
