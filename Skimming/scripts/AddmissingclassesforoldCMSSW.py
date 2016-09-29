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




#################################################################################################################


def fixes_classes():
	commands = [
		"cp Kappa/Skimming/higgsTauTau/kappa_fixmissing_class/classes_def.xml Kappa/DataFormats/src/classes_def.xml"
		]
	execCommands(commands)
	return


#################################################################################################################

def main():
	fixes_classes()

#################################################################################################################
if __name__ == "__main__":
	main()
