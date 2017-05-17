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
	commands = [
		"cd " + os.path.expandvars("$CMSSW_BASE/src/"),
		#Electron cutBased Id and MVA Id
		#https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_8_0
		#https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recipes_for_regular_users_common
		"git cms-addpkg RecoMET/METPUSubtraction",
		"git cms-addpkg DataFormats/METReco",
		"git cms-addpkg PhysicsTools/PatUtils",
		"git cms-addpkg RecoEgamma/ElectronIdentification",
		#This needs to be checked out first since there are conflicts with MVA MET otherwise and then 63 packages are checked out...
		"git cms-merge-topic -u ikrav:egm_id_80X_v2",
		# additional metfilters
		"git cms-merge-topic -u cms-met:fromCMSSW_8_0_20_postICHEPfilter",
		"git cms-merge-topic cms-met:METRecipe_8020 -u",
		"git cms-merge-topic cms-met:METRecipe_80X_part2 -u",
		"sed -i '/produces<edm::PtrVector<reco::Muon>>/a \	  produces<bool>();' RecoMET/METFilters/plugins/BadGlobalMuonTagger.cc",
		"sed -i '/iEvent.put(std::move(out),/a \	iEvent.put(std::auto_ptr<bool>(new bool(found)));' RecoMET/METFilters/plugins/BadGlobalMuonTagger.cc",
		#packages needed to rerun tau id
		"git cms-merge-topic -u cms-tau-pog:CMSSW_8_0_X_tau-pog_miniAOD-backport-tauID",

		#correct jet corrections for mvamet
		"git cms-merge-topic -u cms-met:METRecipe_8020",
		#Mvamet package based on Summer16 Training
		"git cms-merge-topic -u macewindu009:mvamet8026",
		#copy training weightfile
		"mkdir " + os.path.expandvars("$CMSSW_BASE/src/RecoMET/METPUSubtraction/data"),
		"cd " + os.path.expandvars("$CMSSW_BASE/src/RecoMET/METPUSubtraction/data"),
		"wget https://github.com/macewindu009/MetTools/raw/nicobranch/MVAMET/weightfiles/weightfile.root",

		"cd " + os.path.expandvars("$CMSSW_BASE/src/"),
		"sed '/import\ switchJetCollection/a from\ RecoMET\.METProducers\.METSignificanceParams_cfi\ import\ METSignificanceParams_Data' PhysicsTools/PatUtils/python/tools/runMETCorrectionsAndUncertainties.py -i",
		"git clone https://github.com/artus-analysis/TauRefit.git VertexRefit/TauRefit",
		#fetch xml files for Egamma Id from private repository
		"git clone https://github.com/ikrav/RecoEgamma-ElectronIdentification.git tempData/RecoEgamma/ElectronIdentification/data",
		"cd " + os.path.expandvars("$CMSSW_BASE/src/tempData/RecoEgamma/ElectronIdentification/data"),
		"git checkout egm_id_80X_v1",
		"cd " + os.path.expandvars("$CMSSW_BASE/src/tempData/"),
		"cp -r * " + os.path.expandvars("$CMSSW_BASE/src/"),
		"cd " + os.path.expandvars("$CMSSW_BASE/src/"),
		"rm -rf tempData",

		#Remove the .git folder as it is not needed and contains a lot of useless data
		"rm -rf RecoEgamma/ElectronIdentification/data/.git",
		#Check out Kappa
		"git clone https://github.com/KappaAnalysis/Kappa.git"
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
