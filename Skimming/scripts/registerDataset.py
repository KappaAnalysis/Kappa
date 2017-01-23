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

def check_nickname_unique(nickname):
	if( len(get_sample_by_nick(nickname, expect_n_results = -1)) == 0):
		print "The nickname is a unique identifier."
	else:
		print "The new nickname would not be unique. Please adjust your settings. Was it mayby already in datasets.json?"

def register_new_sample(dict, options):
	# split sample name
	pd_name, details, filetype = options.sample.strip("/").split("/")
	new_entry = {}
	sample = options.sample
	if(sample in dict):
		new_entry = dict[sample]
	else:
		new_entry = {}
	if options.dbs:
		new_entry["inputDBS"]=options.dbs
	new_entry["data"]      = is_data(details,options.data)
        new_entry["embedded"]  = is_embedded(filetype)
	
	new_entry["energy"]    = get_energy(pd_name, details, data = new_entry["data"], isembedded=new_entry["embedded"])
	new_entry["campaign"]  = get_campaign(details, energy=new_entry["energy"])
	new_entry["scenario"]  = get_scenario(details, energy=new_entry["energy"], data=new_entry["data"])
	new_entry["generator"] = get_generator(pd_name, data=new_entry["data"])
	new_entry["process"]   = get_process(pd_name)
	new_entry["format"]    = get_format(filetype, default=None)
	new_entry["n_events_generated"]    = get_n_generated_events(sample, options.dbs)
	new_entry["n_files"]               = get_n_files(sample, options.dbs)
	new_entry["extension"] = get_extension(details)
	if options.xsec != "":
		new_entry["xsec"] = float(options.xsec)
	pprint.pprint(new_entry)
	print "The nickname will be: "
	print make_nickname(new_entry)
	check_nickname_unique(make_nickname(new_entry))
	dict[sample] = new_entry
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
	parser.add_option("-x", "--xsec", default="", help="crossection for this Sample")
	parser.add_option("-D", "--dbs", default=None, help="input DBS instance")
        parser.add_option("-d", "--data", help="force sample to be data", action="store_true")

	parser.add_option("-i", "--interactive", help="run in interactive mode", action="store_true")
	parser.add_option("-v", "--verbose", help="verbose output", action="store_true", default=False)

	(options, args) = parser.parse_args()

	dict = database
	if options.verbose:
		pprint(dict)
	newdict = register_new_sample(dict, options)
	if options.interactive:
		if(confirm()):
			save_database(dict, dataset)
	else:
		save_database(dict, dataset)
if __name__ == "__main__": main()

