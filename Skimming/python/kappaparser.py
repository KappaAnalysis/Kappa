# -*- coding: utf-8 -*-

"""
	Parser for CMSSW which provides some useful arguments for testing of Kappa skim configs
	'output', 'maxEvents' and 'files' keywords are already provided by the base class (VarParsing)
	Attention: by default, '_numEvent(%s)' % maxEvents is appended to the output filename

	VarParsing documentation:
	https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#Passing_Command_Line_Arguments_T
	https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCommandLineParsing
"""

from FWCore.ParameterSet.VarParsing import VarParsing

class KappaParser(VarParsing):
	def __init__(self,
			default_globaltag = '',
			default_nickname = '',
			default_kappaverbosity = 0
		):
		super(KappaParser, self).__init__('standard')

		# set defaults for already existing arguments
		self.setDefault('output', 'kappatuple.root')
		self.setDefault('maxEvents', 100)

		# new arguments
		self.register ('globaltag', default_globaltag, VarParsing.multiplicity.singleton,
			VarParsing.varType.string, 'Global Tag to be used.')
		self.register ('nickname', default_nickname, VarParsing.multiplicity.singleton,
			VarParsing.varType.string, 'nickname.')
		self.register ('kappaverbosity', default_kappaverbosity, VarParsing.multiplicity.singleton,
			VarParsing.varType.int, 'kappa verbosity')


class KappaParserZJet(KappaParser):
	def __init__(self):
		super(KappaParserZJet, self).__init__(
			default_globaltag = 'FT53_V21A_AN6::All',
			default_nickname = 'DoubleMu_Run2012A_22Jan2013_8TeV',
		)
		self.setDefault('files', 'file:/storage/8/dhaitz/testfiles/data_AOD_2012A.root')
