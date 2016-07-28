#! /usr/bin/env python
# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Raphael Friese <Raphael.Friese@cern.ch>

import optparse
import os
import string
from pprint import pprint
import json
import re
from Kappa.Skimming.registerDatasetHelper import *
import Kappa.Skimming.datasets2011 as datasets2011
import Kappa.Skimming.datasets2012 as datasets2012
import Kappa.Skimming.datasets2013 as datasets2013
import Kappa.Skimming.datasets2015_miniAODv2 as datasets2015_miniAODv2
import Kappa.Skimming.datasets2015_Fall15 as datasetsFall15
import Kappa.Skimming.datasets2016 as datasets2016
import Kappa.Skimming.datasets2016_Spring16 as datasetsSpring16


def writeFilelist(querytuple, dict, options):
	query = querytuple[1]
	query_result = []
	for sample, values in dict.iteritems():
		matches = True
		for name, attribute in values.iteritems():
			if not name in query: continue
			if not (re.match(str(query[name]), str(attribute)) != None):#query[name] != attribute: 
				matches = False
		if matches: 
			query_result.append("\t" + make_nickname(values) + " : " + sample)
	query_result.sort()
	query_result.insert(0,'\n[CMSSW_Advanced]\ndataset +=')
	for entry in query_result:
		print entry

	base_folder = options.output

	filename, file_extension = os.path.splitext("energy/query-name.conf")
	filename = os.path.basename( filename)
	dir_string = os.path.dirname("energy/query-name.conf").split('/')
	filename = replace_with_dict_values(filename, querytuple)
	filepath = ''
	for dir in dir_string:
		filepath = os.path.join(filepath, replace_with_dict_values(dir, querytuple))

	filepath = os.path.join(base_folder, filepath)
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	full_filename= os.path.join(filepath, filename + file_extension)

	outfile = open(full_filename, 'w')
	outfile.write("\n".join(query_result))
	outfile.close()
	print full_filename + " written"

def replace_with_dict_values(name, querytuple):
	returnvalue = ''
	if name == 'query-name':
		return querytuple[0]
	if name in querytuple[1]:
		returnvalue = querytuple[1][name]
		if name == "energy":
			returnvalue = returnvalue + "TeV"
		if name == "data":
			returnvalue = "data" if returnvalue else "mc"
	else:
		print "Statement " + name + " not replaced"
		returnvalue = name
	return returnvalue
 
def main():
	parser = optparse.OptionParser(usage="usage: %prog [options]",
	                               description="Script to extend datasets.json by another sample")

	parser.add_option("--output", help="output directory", default="../higgsTauTau/samples/")

	(options, args) = parser.parse_args()

	querielist = []
	#querielist.append( datasets2011.queries )
	#querielist.append( datasets2012.queries )
	#querielist.append( datasets2013.queries )
	#querielist.append( datasets2015_miniAODv2.queries )
	# querielist.append( datasetsFall15.queries )
	#querielist.append( datasets2016.queries )
	querielist.append( datasetsSpring16.queries )
		
	dict = database
	for queries in querielist:
		for query in queries.items():
			writeFilelist(query, dict, options)



if __name__ == "__main__": main()

