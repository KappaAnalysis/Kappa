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

cmssw_base = os.environ.get("CMSSW_BASE")
dataset = os.path.join(cmssw_base, "src/Kappa/Skimming/data/datasets.json")

def update_dict(sample, entry):
	pd_name, details, filetype = sample.strip("/").split("/")
	# add new column here
	#entry["n_events_generated"]    = get_n_generated_events(sample)
	#entry["extension"]             = get_extension(details, entry["data"])
	entry["n_files"]             = get_n_files( sample)
	return entry


def main():
	parser = optparse.OptionParser(usage="usage: %prog [options]",
	                               description="Script to extend datasets.json by a new attribute")


	(options, args) = parser.parse_args()

	dict = database
	new_dict = {}
	for sample, entry in dict.iteritems():
		new_dict[sample] = update_dict(sample, entry)
	save_database(new_dict, dataset)

if __name__ == "__main__": main()

