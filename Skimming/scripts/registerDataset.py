#! /usr/bin/env python
# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Raphael Friese <Raphael.Friese@cern.ch>

import optparse
import os
import string
from pprint import pprint
import json

from Kappa.Skimming.registerDatasetHelper import *

cmssw_base = os.environ.get("CMSSW_BASE")
dataset = os.path.join(cmssw_base, "src/Kappa/Skimming/data/datasets.json")

def register_new_sample(dict, options):
	# split sample name
	pd_name, details, filetype = options.sample.strip("/").split("/")
	new_entry = {}
	sample = options.sample
	new_entry[sample] = {}
	new_entry[sample]["data"]      = is_data(details, options.data)
	new_entry[sample]["energy"]    = get_energy(pd_name, details, options.energy, data = new_entry[sample]["data"])
	new_entry[sample]["campaign"]  = get_campaign(details, options.campaign, energy=new_entry[sample]["energy"])
	new_entry[sample]["scenario"]  = get_scenario(details, options.scenario, energy=new_entry[sample]["energy"], data=new_entry[sample]["data"])
	new_entry[sample]["generator"] = get_generator(pd_name, options.generator, data=new_entry[sample]["data"])
	new_entry[sample]["process"]   = get_process(pd_name, options.process)
	new_entry[sample]["embedded"]  = is_embedded(filetype, options.embedded)
	pprint(new_entry)
	print make_nickname(new_entry[sample])
	dict[sample] = new_entry[sample]
	return dict

def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
    if prompt is None:
        prompt = 'Write to datasets.json?'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def main():
	parser = optparse.OptionParser(usage="usage: %prog [options]",
	                               description="Script to extend datasets.json by another sample")

	# sample
	parser.add_option("-s", "--sample", help="official Sample Sting")
	# campaign
	parser.add_option("-c", "--campaign", help="Production campaign", default=None)
	# scenario
	parser.add_option("--scenario", help="PU and BX scenario string", default=None)
	# energy
	parser.add_option("-e", "--energy", help="Center of Mass Energy", default=None)
	# embedded
	parser.add_option("--embedded", help="embedded flag", default=False, action="store_true")
	# generator
	parser.add_option("-g", "--generator", help="generator", default=None)
	# global tag
	parser.add_option("--global-tag", help="Global Tag", default=None)
	# data
	parser.add_option("-d", "--data", help="is data", default=None)
	# process
	parser.add_option("-p", "--process", help="process", default=None)
	
	parser.add_option("-i", "--interactive", help="run in interactive mode", action="store_true")


	(options, args) = parser.parse_args()

	dict = load_database(dataset)
	pprint(dict)
	newdict = register_new_sample(dict, options)
	if options.interactive:
		if(confirm()):
			save_database(dict, dataset)
	else:
		save_database(dict, dataset)
if __name__ == "__main__": main()

