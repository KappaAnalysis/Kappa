#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Stefan Wayand <stefan.wayand@gmail.com>
#-#   Thomas Mueller <tmuller@cern.ch>

# checkout script for cmssw53x for skimming
# todo: implement logger
# todo: make cmsenv/scramv work

import os
import sys
from optparse import OptionParser
from AddmissingclassesforoldCMSSW import fixes_classes

#################################################################################################################


def execCommands(commands):
	for command in commands:
		print ""
		print "command: " + command
		exitCode = 1
		nTrials = 0
		while exitCode != 0:
			if nTrials > 1:
				print "Last command could NOT be executed successfully! Stop program!"
				sys.exit(1)

				#logger.info("{CHECKOUT_COMMAND} (trial {N_TRIAL}):").formal(CHECKOUT_COMMAND = command, N_TRIAL = (nTrials+1))

			if command.startswith("cd"):
				os.chdir(os.path.expandvars(command.replace("cd ", "")))
				exitCode = int((os.path.expandvars(command.replace("cd ", "").strip("/")) != os.getcwd().strip("/")))
			else:
				exitCode = os.system(command)

			nTrials += 1

	return

#################################################################################################################


def getSysInformation():
	sysInformation = {
	"github_username": os.popen("git config user.name").readline().replace("\n", ""),
	"email": os.popen("git config user.email").readline().replace("\n", ""),
	"editor": os.popen("git config core.editor").readline().replace("\n", ""),
	"pwd": os.getcwd()
	}
	return sysInformation


#################################################################################################################


def checkoutPackages(args):
	cmsswsrc = os.popen("echo $CMSSW_BASE").readline().replace("\n", "") + '/src/'

	commands = [
		'cd ' + cmsswsrc,
		# do the git cms-addpkg before starting with checking out cvs repositories

		#Electrons
		"git cms-addpkg EgammaAnalysis/ElectronTools",
		"cd " + cmsswsrc + "EgammaAnalysis/ElectronTools/data/",
		"cat download.url | xargs wget",
		'cd ' + cmsswsrc,

		# https://twiki.cern.ch/twiki/bin/view/CMS/GluonTag
		"git clone git://github.com/amarini/QuarkGluonTagger.git -b v1-2-3",

		# PU Jet ID as used in TauTau and needed for MVA MET (does not work with git cms-cvs-history and does not compile with cvs co)
		# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet#CMSSW_5_3_22_patch1_requires_slc


		#PAT Recipe (https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X)
		"git cms-addpkg PhysicsTools/PatAlgos",
		"git cms-merge-topic -u cms-analysis-tools:5_3_16_patch1-testNewTau",

		#MET Recipe (https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMETRecipe53X)
		"git cms-merge-topic -u TaiSakuma:53X-met-140217-01",

		#MVA & No-PU MET Recipe
		"git-cms-merge-topic -u cms-met:53X-MVaNoPuMET-20140606-01",

		"git clone git://github.com/ajaykumar649/Jets_Short.git",
		"cp -r Jets_Short/* " + cmsswsrc,
		"rm -rf Jets_Short",
		
		# PF isolation
		"git-cms-addpkg CommonTools/ParticleFlow",

		# Tau Jets
		"git cms-addpkg PhysicsTools/JetMCAlgos",

		#Check out Kappa
		"git clone https://github.com/KappaAnalysis/Kappa.git",
		#"scram b -j 4"
	]
	execCommands(commands)
	return
#################################################################################################################


def fixes_forsl6():
	commands = [
		"cp Kappa/Skimming/higgsTauTau/kappa_sl6_fix/CMSDAS12ThreejetTestAnalyzer.cc  RecoJets/JetAnalyzers/src/CMSDAS12ThreejetTestAnalyzer.cc",
		"cp Kappa/Skimming/higgsTauTau/kappa_sl6_fix/JetSubstructurePlotsExample.cc  RecoJets/JetAnalyzers/src/JetSubstructurePlotsExample.cc",
		"cp Kappa/Skimming/higgsTauTau/kappa_sl6_fix/myFastSimVal.cc  RecoJets/JetAnalyzers/src/myFastSimVal.cc",
		"cp Kappa/Skimming/higgsTauTau/kappa_sl6_fix/myJetAna.cc  RecoJets/JetAnalyzers/src/myJetAna.cc",
		]
	execCommands(commands)
	return


#################################################################################################################

def main():
	parser = OptionParser()
	sysInformation = getSysInformation()

	parser.add_option("--github_username", help="your name as in github. Default: " + sysInformation["github_username"], default=sysInformation["github_username"], nargs='?')
	parser.add_option("--mail", help="your email. Default: " + sysInformation["email"], default=sysInformation["email"], nargs='?')
	parser.add_option("--editor", help="your favorite editor (ex. emacs). Default: " + sysInformation["editor"], default=sysInformation["editor"], nargs='?')
	parser.add_option("--cmssw_version", help="the CMSSW Version to checko out. Default: CMSSW_5_3_13_patch3", default="CMSSW_5_3_13_patch3", nargs='?')

	#args = parser.parse_args()
	(options, args) = parser.parse_args()
	checkoutPackages(args)
	fixes_forsl6()
	fixes_classes()

#################################################################################################################
if __name__ == "__main__":
	main()
