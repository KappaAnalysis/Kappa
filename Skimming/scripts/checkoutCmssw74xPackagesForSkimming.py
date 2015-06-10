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
		"cd " + cmsswsrc,
		# do the git cms-addpkg before starting with checking out cvs repositories

		#Electron cutBased Id package
		#https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_74X
		"git cms-merge-topic 9003",
		"rm -rf RecoEgamma/ElectronIdentification/data",
		"git clone https://github.com/cms-data/RecoEgamma-ElectronIdentification.git RecoEgamma/ElectronIdentification/data",
		"rm -rf RecoEgamma/PhotonIdentification/data",
		"git clone https://github.com/cms-data/RecoEgamma-PhotonIdentification.git RecoEgamma/PhotonIdentification/data",

		#Electron MVA Id package (no public recipe existing yet for 74X release)
		#https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
		#"git cms-merge-topic HuguesBrun:trigElecIdInCommonIsoSelection720",

		#MVA & No-PU MET Recipe
		#https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet#Instructions_for_7_4_X
		"git cms-addpkg RecoMET/METPUSubtraction/",
		"cd " + cmsswsrc + "RecoMET/METPUSubtraction/",
		"git clone https://github.com/rfriese/RecoMET-METPUSubtraction data -b 72X-13TeV-Phys14_25_V4-26Mar15",
		"cd " + cmsswsrc,

		#Check out Kappa
		"git clone https://github.com/KappaAnalysis/Kappa.git -b development",
		#"scram b -j 4"
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
	parser.add_option("--cmssw_version", help="the CMSSW Version to checko out. Default: CMSSW_7_2_2", default="CMSSW_7_2_2", nargs='?')

	#args = parser.parse_args()
	(options, args) = parser.parse_args()
	checkoutPackages(args)


#################################################################################################################


if __name__ == "__main__":
	main()
