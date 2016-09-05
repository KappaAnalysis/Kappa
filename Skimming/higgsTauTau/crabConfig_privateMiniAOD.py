#!/bin/env python
# crab submission script
# usage: python crabConfig.py submit

from CRABClient.UserUtilities import getUsernameFromSiteDB
from httplib import HTTPException
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from multiprocessing import Process
from Kappa.Skimming.registerDatasetHelper import get_sample_by_nick
from Kappa.Skimming.datasetsHelper2015 import isData
import sys
from glob import glob
import os, shutil
from Kappa.Skimming.tools import read_grid_control_includes
import datetime
today=datetime.date.today().strftime("%Y-%m-%d")
date = today # feel free to change

def submit(config):
	try:
		crabCommand('submit', config = config)
	except HTTPException as hte:
		print "Failed submitting task: %s" % (hte.headers)
	except ClientException as cle:
		print "Failed submitting task: %s" % (cle)

def crab_command(command):
	for dir in glob('/net/scratch_cms/institut_3b/%s/kappa/crab_kappa_skim-%s/*'%(getUsernameFromSiteDB(), date)):
		try:
			crabCommand(command, dir = dir)
		except HTTPException as hte:
			print hte

def check_path(path):
	if os.path.exists(path):
		print(path + " already exists! Delete it now in order to re-initialize it by crab? [y/n]")
		yes = set(['yes','y', 'ye', ''])
		no = set(['no','n'])

		choice = raw_input().lower()
		if choice in yes:
			shutil.rmtree(path)
			return
		elif choice in no:
			return
		else:
			sys.stdout.write(path + " already exists! Delete it now in order to re-initialize it by crab?")

def submission():
	from CRABClient.UserUtilities import config, getUsernameFromSiteDB
	config = config()

	##-- Your name of the crab project
	config.General.requestName = 'KAPPA_FROM_AOD_SUSYGluGlu_Sync2015'
	#config.General.workArea = 'crab_projects'
	config.General.workArea = '/net/scratch_cms/institut_3b/%s/kappa/crab_kappa_skim-%s'%(getUsernameFromSiteDB(), date)

	##-- Transfer root files as well as log files "cmsRun -j FrameworkJobReport.xml" (log file = FrameworkJobReport.xml)
	check_path(config.General.workArea)	
	config.General.transferOutputs = True
	config.General.transferLogs = True

	##-- We want to have the special dcms role (better fair share at german grid sites). 
	config.User.voGroup = 'dcms'

	##-- the scripts (Analysis means with EDM input) which are executed. psetName is the cmsRun config and scriptExe is a shell config which should include "cmsRun -j FrameworkJobReport.xml -p PSet.py" (PSet.py is the renamed config.JobType.psetName)
	config.JobType.pluginName = 'Analysis'
	config.JobType.sendPythonFolder = True
	config.JobType.psetName = 'AODtoMiniAOD_cfg.py'
	config.JobType.scriptExe = 'kappaWorkflow_privateMiniAOD.sh'
	#config.JobType.maxJobRuntimeMin = 2750
	#config.JobType.maxMemoryMB = 6000

	##-- instead of taking the outputfile per hand use the result of pset.py and renamed it, which cheat on the test of is an EDM file test and allows to use publish the data 
	config.JobType.disableAutomaticOutputCollection = True
	config.JobType.outputFiles = ['kappaTuple.root']

	##-- The dataset you want to process:

	config.Data.inputDataset = '/SUSYGluGluToHToTauTau_M-160_TuneCUETP8M1_13TeV-pythia8/RunIIFall15DR76-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/AODSIM'
	#'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIIFall15DR76-PU25nsData2015v1_76X_mcRun2_asymptotic_v12_ext1-v1/AODSIM'
	config.Data.inputDBS = 'global'
	config.Data.splitting = 'FileBased'
	config.Data.unitsPerJob = 1
	##-- If you want to run test jobs set totalUnits to a small number and publication to false
	#config.Data.totalUnits = 10
	config.Data.publication = False
	
	##-- the output strorage element
	config.Site.storageSite = 'T2_DE_DESY'
	config.Data.outLFNDirBase = '/store/user/%s/higgs-kit/skimming/80X_%s'%(getUsernameFromSiteDB(), date)
	
	##-- Run in xrootd mode (which allows you to run the jobs on all possible sites) 
	#config.Data.ignoreLocality = True
	#config.Site.whitelist = ['T2_CH_CERN','T2_DE_DESY','T1_DE_KIT','T2_DE_RWTH','T2_UK_London_IC', 'T2_US_MIT']
	

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


	
	
