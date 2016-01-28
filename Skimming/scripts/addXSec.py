#! /usr/bin/env python
# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Raphael Friese <Raphael.Friese@cern.ch>
# script to update existing dataset.json when new columns are introduced
# currently adds number of generated events
import optparse
import os
import string
from pprint import pprint
import json

from Kappa.Skimming.registerDatasetHelper import *
from Kappa.Skimming.equationparsing import eval_expr
cmssw_base = os.environ.get("CMSSW_BASE")
dataset = os.path.join(cmssw_base, "src/Kappa/Skimming/data/datasets.json")



def main():
	parser = optparse.OptionParser(usage="usage: %prog [options]",
	                               description="Script to extend datasets.json by another sample")
	# sample
	parser.add_option("-s", "--sample", help="official Sample Sting")
	# crosssection
	parser.add_option("-x", "--xsec", help="Sample cross section")


	(options, args) = parser.parse_args()
	sample = options.sample
	xsec = options.xsec
	xsec = eval_expr(xsec.replace('x', '*').replace(' ', ''))
	dict = load_database(dataset)
	dict[sample]["xsec"] = float(xsec)
	import pprint
	pprint.pprint( dict[sample])
	save_database(dict, dataset)

if __name__ == "__main__": main()

