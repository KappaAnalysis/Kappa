#!/bin/env python
# crab submission script
# usage: python crabConfig.py submit

from CRABClient.UserUtilities import getUsernameFromSiteDB
from httplib import HTTPException
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from multiprocessing import Process
from Kappa.Skimming.registerDatasetHelper import get_sample_by_nick
import sys
from glob import glob

def submit(config):
	try:
		crabCommand('submit', config = config)
	except HTTPException as hte:
		print "Failed submitting task: %s" % (hte.headers)
	except ClientException as cle:
		print "Failed submitting task: %s" % (cle)

def crab_command(command):
	for dir in glob('/nfs/dust/cms/user/%s/crab_kappa_skim-2/*'%(getUsernameFromSiteDB())):
		crabCommand(command, dir = dir)

def submission():
	from CRABClient.UserUtilities import config
	config = config()
	
	config.General.workArea = '/nfs/dust/cms/user/%s/crab_kappa_skim-2'%(getUsernameFromSiteDB())
	config.General.transferOutputs = True
	config.General.transferLogs = True
	
	config.JobType.pluginName = 'Analysis'
	config.JobType.psetName = 'kSkimming_run2_cfg.py'
	#config.JobType.inputFiles = ['Summer15_V5_MC.db']
	config.JobType.allowUndistributedCMSSW = True
	
	config.Data.inputDBS = 'global'
	config.Data.splitting = 'FileBased'
	config.Data.unitsPerJob = 1
	config.Data.outLFNDirBase = '/store/user/%s/higgs-kit-crab-2/'%(getUsernameFromSiteDB())
	config.Data.publication = False
	
	config.Site.storageSite = "T2_DE_DESY"
	
	nicknames = ['SUSYGluGluToHToTauTauM160_RunIISpring15DR74_Asympt25ns_13TeV_MINIAOD_pythia8']
	
	# loop over datasets and get repsective nicks
	for nickname in nicknames:
		config.General.requestName = nickname+'newEleId'
		config.JobType.pyCfgParams = ['globalTag=74X_mcRun2_asymptotic_v2','kappaTag=KAPPA_2_0_4','nickname=%s'%(nickname),'outputfilename=kappa_%s.root'%(nickname)]
		config.JobType.outputFiles = ['kappa_%s.root'%(nickname)]
		config.Data.inputDataset = get_sample_by_nick(nickname)
		p = Process(target=submit, args=(config,))
		p.start()
		p.join()

if __name__ == "__main__":
	if len(sys.argv) == 1: 
		print "no setting provided"
		sys.exit()
	if sys.argv[1] == "submit":
		submission()
	elif sys.argv[1] in ["status", "resubmit", "kill"]:
		crab_command(sys.argv[1])
	else:
		print "setting \"%s\" is not implemented"% sys.argv[1]
