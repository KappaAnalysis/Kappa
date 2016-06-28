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

def suggestion(dict, sample):
	# aus sample process extrahieren, schwerpunktsenergie
	query = { "energy" : get_energy(sample, "2016"), "process" : get_process(sample).replace("/", "") }
	print "searching for previously known cross-sections with following query: "
	pprint.pprint(query)
	query_result = []
	best_guess = 0
	for sample, values in dict.iteritems():
		matches = True
		for name, attribute in values.iteritems():
			if not name in query: continue
			if not (re.match(str(query[name]), str(attribute)) != None):#query[name] != attribute: 
				matches = False
		if matches and "xsec" in dict[sample]:
			query_result.append("\t" + make_nickname(values) + " : " + str(dict[sample]["xsec"]))
			if best_guess == 0:
				best_guess = dict[sample]["xsec"]
			else:
				if best_guess != dict[sample]["xsec"]:
					best_guess = -1 # differences, no recommendation found
	print "previously set: "
	pprint.pprint( query_result )
	return best_guess


def main():
	parser = optparse.OptionParser(usage="usage: %prog [options]",
	                               description="Script to extend datasets.json by another sample")
	# sample
	parser.add_option("-s", "--sample", help="official Sample Sting")
	# crosssection
	parser.add_option("-x", "--xsec", help="Sample cross section")


	(options, args) = parser.parse_args()
	sample = options.sample
	xsec = float(options.xsec)
	#xsec = eval_expr(xsec.replace('x', '*').replace(' ', ''))
	dict = load_database(dataset)
	if "xsec" in dict[sample]:
		print "sample already does have a cross-section of " + str(dict[sample]["xsec"]) + ". Stopping"
		sys.exit()
	best_guess = suggestion(dict, sample)
	if best_guess > 0 and xsec < 0:
		print "automatically fetching cross-section from previously known samples"
		xsec = best_guess
	if xsec <= 0.0:
		print "no proper cross-section defined. Stopping"
		sys.exit()
	dict[sample]["xsec"] = float(xsec)
	print "\n new datasets.json entry: "
	pprint.pprint( dict[sample])
	save_database(dict, dataset)

if __name__ == "__main__": main()

