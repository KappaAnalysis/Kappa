#!/bin/env python
# crab submission class

from CRABClient.UserUtilities import getUsernameFromSiteDB,config
from httplib import HTTPException
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from multiprocessing import Process
from glob import glob
import os, shutil




class single_crab_job():
    def __init__(self,name,workdir='crab_jobs/akt_test', dataset_name=None,cmsrun_cfg_file='test.py'):
        self.name = name ## needed for the crab_config 
        self.workdir = os.path.abspath(workdir) ## needed for the crab config 
        self.folder = os.path.join(self.workdir,"crab_"+self.name) ## Follow the crab naming convention. Is used for: crab command -d self.folder (e.g command could be status )  
	self.config = None ## THE crab config file. Only needed if it is new job. Is used for: crab submit self.config  
	self.issubmitted = True
	self.laststatus = {} ## catch of the last job status. Maybe usefull for furher implementations e.g. automatic resubmitting of jobs  
	if dataset_name: ## only new jobs need the information about the dataset. For submitted jobs the self.folder is enough
	  print self.name
	  self.issubmitted = False
	  self.init_config(dataset_name,cmsrun_cfg_file)
    def submit(self): ## submit the jobs (comand line would be: "crab submit config_name.py"
	try:
		crabCommand('submit', config = self.config , proxy=os.environ['X509_USER_PROXY'])
	except HTTPException as hte:
		print "Failed submitting task: %s" % (hte.headers)
	except ClientException as cle:
		print "Failed submitting task: %s" % (cle)
    def crab_command(self,command): ## run any crab command except submit. E.g. crab status full_path_to_directory
      	try:
		self.laststatus[command] = crabCommand(command, dir = self.folder, proxy=os.environ['X509_USER_PROXY'])
	except HTTPException as hte:
		print hte
    def init_config(self,inputDataset,cmsrun_cfg_file='test.py'):
        self.config = config() ## new empty crab config 
        self.fill_config_defaults()
	self.config.JobType.psetName = cmsrun_cfg_file  
        self.config.Data.inputDataset = inputDataset
      
    def fill_config_defaults(self): ## here are the default values for running crab. Feel free to test some options 
        self.config.General.requestName = self.name
	self.config.General.workArea = self.workdir
	self.config.General.transferOutputs = True
	self.config.General.transferLogs = True
	self.config.User.voGroup = 'dcms'
	
	self.config.JobType.pluginName = 'Analysis'

	
	self.config.Data.inputDBS = 'global'
	self.config.Data.splitting = 'FileBased'
	self.config.Data.unitsPerJob = 3 
	self.config.Data.totalUnits =  -1
        self.config.Data.publication = False
	
        self.config.Data.outLFNDirBase = '/store/user/%s/zjets/skimming/%s'%(getUsernameFromSiteDB(), self.name)
	self.config.Site.storageSite = "T2_DE_DESY"
#	self.config.Site.storageSite = "T1_DE_KIT"
	
	#self.config.JobType.disableAutomaticOutputCollection = True
	self.config.JobType.outputFiles = ['skim76.root']
        #self.config.JobType.sendPythonFolder = True

        self.config.Data.ignoreLocality = True  #switch of xrd acess for now
#	self.config.Site.whitelist = ['T2_CH_CERN','T2_DE_DESY','T1_DE_KIT','T2_DE_RWTH']
	self.config.Site.whitelist = ['T2_CH_CERN','T2_DE_DESY','T1_DE_KIT','T2_DE_RWTH','T2_US_*']
#	self.config.Site.whitelist = ['T2_*','T1_DE_KIT']
        
        #self.config.JobType.maxMemoryMB = 2500

class multi_crab_job(): ## class which handels multiple crab jobs of the same kind but different dataset inputs (and maybe different cmsrun_configs.py in future ) 
    def __init__(self,name,globalworkdir='crab_jobs',cmsrun_cfg_file='test.py'):
      self.name = name 
      self.workdir = os.path.abspath(os.path.join(globalworkdir,name)) # Store all jobs in one commone folder
      if not os.path.exists(self.workdir):
	os.makedirs(self.workdir)
      self.cmsrun_cfg_file = cmsrun_cfg_file 
      self.jobs = {} ## dict for all jobs
    def init_jobs_from_simple_file(self, file_name): ## simple input for datasets. Need one file with containing DataSet_Nich : Dataset/DAS/NAME.  Then new crab jobs will be created
      infile = open(file_name,'r')
      for akt_line in infile.readlines():
	  akt_line=akt_line.strip()
	  if not akt_line:
	    continue
	  if akt_line[0]=='#':
	    continue
	  if len(akt_line.split(':'))<2:
	    print "This line\n",akt_line,"\nhas not the right format= Nickname : Datasetname and will be skipped"
	    continue
	  job_name = akt_line.split(':')[0].strip()
	  job_dataset = akt_line.split(':')[1].strip()
	  if job_name in self.jobs:
	      print job_name," allready initialized. Skip this entry"
	  else:
	      print self.workdir
	      self.jobs[job_name] = single_crab_job(job_name,self.workdir,job_dataset,self.cmsrun_cfg_file)
    def submit_jobs(self):  ## Submit all new jobs
      for akt_job in self.jobs.itervalues():
	if not akt_job.issubmitted:
	  print "sumbitting job"
	  akt_job.submit()
    def get_jobs_from_workdir(self): ## Load already submitted jobs. Which means set the folder variable   
      for akt_job in os.listdir(self.workdir):
	self.jobs[akt_job[5:]] = single_crab_job(akt_job[5:],self.workdir) ## because the crab_ is automaticly added it must be removed here 
    def crab_command(self,command='status', veto_jobs=[]): ## run crab_command on all jobs
      for akt_job in self.jobs.itervalues() :
	if akt_job in veto_jobs:
	  continue
	akt_job.crab_command(command)


if __name__ == "__main__": ## one example how it can be implemented
	test_jobs = multi_crab_job('akt_test')
	print test_jobs.workdir
	test_jobs.get_jobs_from_workdir()
	test_jobs.init_jobs_from_simple_file('simple_list.txt')
	test_jobs.submit_jobs()
	test_jobs.crab_command()
	#print test_job.workdir
#	if len(sys.argv) == 1: 
#		print "no setting provided"
#		sys.exit()
#	if sys.argv[1] == "submit":
#		submission()
#	elif sys.argv[1] in ["status", "resubmit", "kill"]:
#		crab_command(sys.argv[1])
#	else:
#		print "setting \"%s\" is not implemented"% sys.argv[1]
