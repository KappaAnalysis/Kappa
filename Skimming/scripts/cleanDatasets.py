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
import sys
from Kappa.Skimming.registerDatasetHelper import *
#from Kappa.Skimming.equationparsing import eval_expr
cmssw_base = os.environ.get("CMSSW_BASE")
dataset = os.path.join(cmssw_base, "src/Kappa/Skimming/data/datasets.json")
import pprint

def remove_matching_entries(dict, query): 
	remove_samples = []
	for sample, values in dict.iteritems():
		matches = True
		for name, attribute in values.iteritems():
			if not name in query: continue
			if not (re.match(str(query[name]), str(attribute)) != None):#query[name] != attribute: 
				matches = False
		if matches:
			remove_samples.append(sample)
	print "removing the following samples: "
	pprint.pprint( remove_samples)
	for sample in remove_samples:
		del dict[sample]
	return dict


def main():
	parser = optparse.OptionParser(usage="usage: %prog [options]",
	                               description="Script to extend datasets.json by another sample")
	# sample
	parser.add_option("-s", "--sample", help="official Sample Sting")

	queue = { "campaign" : "RunIISpring15DR74.*" }

	(options, args) = parser.parse_args()
	sample = options.sample
	dict = database
	dict = remove_matching_entries(dict, queue)
	save_database(dict, dataset)

if __name__ == "__main__": main()

