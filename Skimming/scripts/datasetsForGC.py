#! /usr/bin/env python
# -*- coding: utf-8 -*-


import optparse
import os
import string

import Kappa.Skimming.datasets as datasets


gcTemplate = string.Template("""
[CMSSW_Advanced]
dataset += $dataset
""")

gcConfigurations = {
	"DYJets" : datasets.DYJets,
	"TTJets" : datasets.TTJets,
	"Dibosons" : datasets.Dibosons,
	"WJets" : datasets.WJets,
}

def createGcConfigs(outputDir, gcConfigs, period):
	for key, value in gcConfigs.items():
		if type(value) == dict: createGcConfigs(os.path.join(outputDir, key), value, period)
		else:
			gcTemplateOptions = { "dataset" : "" }
			for nickName in value:
				datasetString = datasets.datasets.get(nickName, {}).get("dataset", {}).get(period, None)
				if datasetString: gcTemplateOptions["dataset"] += ("\n\t" + nickName + " : " + datasetString)
			
			if not os.path.exists(outputDir): os.makedirs(outputDir)
			gcConfigFileName = os.path.join(outputDir, key+".conf")
			with open(gcConfigFileName, "w") as gcConfigFile:
				gcConfigFile.write(gcTemplate.substitute(gcTemplateOptions))
				print "Created configuration \"%s\"." % gcConfigFileName

def main():
	parser = optparse.OptionParser(usage="usage: %prog [options]",
	                               description="Script to create GC configurations for the datasets")

	parser.add_option("-o", "--output-dir", help="Output directory where to put the configurations", default="$CMSSW_BASE/src/Kappa/Skimming/samples/")
	parser.add_option("-c", "--clear-dir", help="Delete first all contents of the output directory. [Default: False]", default=False, action="store_true")
	parser.add_option("-p", "--period", help="Running period (7 or 8TeV), multiple times possible. [Default: 8]", type=int, action="append")

	(options, args) = parser.parse_args()
	
	options.output_dir = os.path.expandvars(options.output_dir)
	if not options.period: options.period = [8]
	
	if options.clear_dir: os.system("rm -rv " + os.path.join(options.output_dir, "*"))
	
	for period in options.period: createGcConfigs(options.output_dir, { ("%dTeV" % period) : gcConfigurations }, period)
	
if __name__ == "__main__": main()

