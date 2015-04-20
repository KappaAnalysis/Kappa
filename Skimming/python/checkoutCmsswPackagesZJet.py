#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved

"""
	Checkout script for CMSSW packages.
	
	Gets CMSSW version from $CMSSW_RELEAS_PATH, checks out packages if the exact
	CMSSW version or the major release cycle ('X_Y') are available in the dict.
"""

import os
import sys
import argparse

import tools


class checkoutScript(object):
	def __init__(self):
		self.cmsswsrc = os.environ["CMSSW_BASE"] + '/src/'
		self.checkout_commands_dict = {}

		parser = argparse.ArgumentParser("")
		parser.add_argument("--cmssw-version", default=tools.get_cmssw_version_number(), nargs='?',
			help="the CMSSW Version to check out. Default: %(default)s")
		self.args = parser.parse_args()

		try:
			# exact match of version number:
			self.get_checkout_commands(self.args.cmssw_version)
		except KeyError:
			try:
				# major CMSSW cycle match:
				self.get_checkout_commands(self.args.cmssw_version[:3])
			except KeyError:
				print "\nWARNING: no commands for CMSSW_{0}".format(self.args.cmssw_version)
				print "No packages are checked out"
				self.commands = []


	def get_checkout_commands(self, version):
		self.commands = ['cd ' + self.cmsswsrc] + self.checkout_commands_dict[version]
		print "Checking out packages for CMSSW_" + version


	def run(self):
		for command in self.commands:
			print ""
			print "command: " + command
			exitCode = 1
			nTrials = 0
			while exitCode != 0:
				if nTrials > 1:
					print "Last command could NOT be executed successfully! Stop program!"
					sys.exit(1)

				if command.startswith("cd"):
					os.chdir(os.path.expandvars(command.replace("cd ", "")))
					exitCode = int((os.path.expandvars(command.replace("cd ", "").strip("/")) != os.getcwd().strip("/")))
				else:
					exitCode = os.system(command)

				nTrials += 1


class checkoutScriptZjet(checkoutScript):
	def __init__(self):
		super(checkoutScriptZjet, self).__init__()

		self.checkout_commands_dict = {
			#'5_3': [], TODO
			#'7_2': [], TODO
			'7_4':[
				"git-cms-addpkg CommonTools/ParticleFlow",
				"git clone https://github.com/KappaAnalysis/Kappa.git -b development",
			],
		}


if __name__ == "__main__":
	checkout = checkoutScriptZjet()
	checkout.run()

