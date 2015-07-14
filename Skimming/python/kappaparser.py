# -*- coding: utf-8 -*-

"""
	Parser for CMSSW which provides some useful arguments for testing of Kappa skim configs
	'output', 'maxEvents' and 'files' keywords are already provided by the base class (VarParsing)
	Attention: by default, '_numEvent(%s)' % maxEvents is appended to the output filename

	Usage: cmsRun config.py maxEvents=10 globalTag=START53_V27 ...

	VarParsing documentation:
	https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#Passing_Command_Line_Arguments_T
	https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCommandLineParsing
"""
import sys

from FWCore.ParameterSet.VarParsing import VarParsing

class KappaParser(VarParsing):
	def __init__(self,
			default_globalTag = None,
			default_nickName = None,
			default_kappaVerbosity = 0
		):
		super(KappaParser, self).__init__('standard')

		# set defaults for already existing arguments
		self.setDefault('output', 'kappatuple.root')
		self.setDefault('maxEvents', 100)

		# new arguments
		self.register('globalTag', default_globalTag, VarParsing.multiplicity.singleton,
			VarParsing.varType.string, 'globalTag to be used.')
		self.register('nickName', default_nickName, VarParsing.multiplicity.singleton,
			VarParsing.varType.string, 'nickName.')
		self.register('kappaVerbosity', default_kappaVerbosity, VarParsing.multiplicity.singleton,
			VarParsing.varType.int, 'kappaVerbosity')


class KappaParserZJet(KappaParser):
	def __init__(self):
		super(KappaParserZJet, self).__init__(
			default_globalTag = None,
			default_nickName = None,
		)
		self.register('test', None, VarParsing.multiplicity.singleton,
			VarParsing.varType.string, 'Test scenario to be used.')
		self.register('channel', 'mm', VarParsing.multiplicity.singleton,
			VarParsing.varType.string, 'Channel to be used (mm, ee, em).')

	def parseArgumentsWithTestDict(self, testDict):
		""" 
			If test is not None, use values from testDict for non-defaults
			Usage: cmsRun conf.py test=XX
			files, GT, nick are set according to entries in testdict
			structure of testdict: testdict = {'XX': {'files': ... } ...}
		"""
		try:
			self.parseArguments()
		except AttributeError:
			if not hasattr(sys, "argv"):
				raise RuntimeError("Cannot parse arguments from 'sys.argv' (is this a pre-compiled session?)")
			raise

		if self.test != None:
			if self.test not in testDict:
				print("FATAL ERROR: Unknown test case '{0}'".format(self.test))
				print("Expected test case out of '{0}'".format("', '".join(testDict.keys())))
				sys.exit(2)
			print "Using values from testcase {0} as default parameters".format(self.test)
			for key, value in testDict[self.test].iteritems():
				if hasattr(self, key) and getattr(self, key) in [None, '', []]:
					setattr(self, key, value)
