#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import os, shutil
from  Kappa.Skimming.datasetsHelperTwopz import datasetsHelperTwopz
import argparse
import datetime
import subprocess
import json
import ast
import gzip
import shutil
import re

from httplib import HTTPException
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException

class SkimManagerBase:


	def __init__(self, storage_for_output, workbase=".", workdir="TEST_SKIM", use_proxy_variable=False):
		self.storage_for_output = storage_for_output
		self.workdir = os.path.join(workbase,workdir)
		if not os.path.exists(self.workdir+"/gc_cfg"): 
			os.makedirs(self.workdir+"/gc_cfg")
		self.skimdataset = datasetsHelperTwopz(os.path.join(self.workdir,"skim_dataset.json"))
		self.skimdataset.keep_input_json = False ## will be updated very often
		self.configfile = 'kSkimming_run2_cfg.py'
		self.max_crab_jobs_per_nick = 8000 # 10k is the hard limit
		self.voms_proxy = None
		self.site_storage_access_dict = {
			"T2_DE_DESY" : "dcap://dcache-cms-dcap.desy.de//pnfs/desy.de/cms/tier2/",
			"T2_DE_RWTH" : "dcap://grid-dcap-extern.physik.rwth-aachen.de/pnfs/physik.rwth-aachen.de/cms/"
		}
		self.UsernameFromSiteDB = None
		try:
			self.voms_proxy=os.environ['X509_USER_PROXY']
		except:
			pass

	def crab_cmd(self, cmd, argument_dict=None):
		try:
			return crabCommand(cmd, **argument_dict)
		except HTTPException as hte:
			print "Failed",cmd,"of the task: %s" % (hte.headers)
		except ClientException as cle:
			print "Failed",cmd,"of the task: %s" % (cle)

	def save_dataset(self,filename=None):
		self.skimdataset.write_to_jsonfile(filename)  

	def add_new(self, nicks = None):
		if nicks is None:
			print "You must select something [see options --query,--nicks  or --tag (with --tagvalues)]"
		else:
			for new_nick in nicks:
				if new_nick in self.skimdataset.base_dict.keys():
					print new_nick," already in this skimming campain"
				else:
					self.skimdataset[new_nick] = self.inputdataset[new_nick]
					self.skimdataset[new_nick]["SKIM_STATUS"] = "INIT"
					self.skimdataset[new_nick]["GCSKIM_STATUS"] = "INIT"
		self.save_dataset()

	def getUsernameFromSiteDB_cache(self):
		if self.UsernameFromSiteDB:
			return self.UsernameFromSiteDB
		else:
			from CRABClient.UserUtilities import getUsernameFromSiteDB
			self.UsernameFromSiteDB = getUsernameFromSiteDB()
			return self.UsernameFromSiteDB

	def get_global_tag(self, akt_nick):
		return self.skimdataset[akt_nick].get("globalTag", '80X_dataRun2_2016SeptRepro_v7' if self.skimdataset.isData(akt_nick) else '80X_mcRun2_asymptotic_2016_TrancheIV_v8')

	def gc_default_cfg(self):
		cfg_dict = {}
		cfg_dict['global'] = {}
		cfg_dict['global']['task']  = 'CMSSW'
		cfg_dict['global']['backend']  = 'condor'
		#cfg_dict['global']['backend']  = 'local'
		#cfg_dict['global']['backend']  = 'cream'
		cfg_dict['global']["workdir create"] = 'True '

		cfg_dict['jobs'] = {}
		cfg_dict['jobs']['in flight'] = '50'
		cfg_dict['jobs']['wall time'] = '06:00:00'
		cfg_dict['jobs']['memory'] = '5000'
		cfg_dict['jobs']['max retry'] = '3'
		#cfg_dict['jobs']['jobs'] = '1'

		cfg_dict['CMSSW'] = {}
		cfg_dict['CMSSW']['project area'] = '$CMSSW_BASE/'
		cfg_dict['CMSSW']['config file'] = self.configfile

		cfg_dict['CMSSW']['dataset splitter'] = 'FileBoundarySplitter'
		cfg_dict['CMSSW']['files per job'] = '1'
		cfg_dict['CMSSW']['se runtime'] = 'True'
		cfg_dict['CMSSW'][';partition lfn modifier'] = '<srm:nrg>' ## comment out per default both can be changed during run, which can improve the succses rate 
		cfg_dict['CMSSW']['depends'] = 'glite'
		cfg_dict['CMSSW']['parameter factory'] = "ModularParameterFactory"
		cfg_dict['CMSSW']['partition lfn modifier dict'] = "\n   <xrootd>    => root://cms-xrd-global.cern.ch//\n   <xrootd:eu> => root://xrootd-cms.infn.it//\n   <xrootd:us> => root://cmsxrootd.fnal.gov//\n   <xrootd:desy> => root://dcache-cms-xrootd.desy.de:1094/\n   <srm:nrg> => srm://dgridsrm-fzk.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/dcms/disk-only/\n   <dcap:nrg> => dcap://dcnrgdcap.gridka.de:22125//pnfs/gridka.de/dcms/disk-only/\n   <xrootd:nrg> => root://cmsxrootd.gridka.de//pnfs/gridka.de/dcms/disk-only/\n   <dcap:gridka> => dcap://dccmsdcap.gridka.de:22125//pnfs/gridka.de/cms/disk-only/\n   <xrootd:gridka> => root://cmsxrootd.gridka.de//\n   <dcap:aachen> => dcap://grid-dcap-extern.physik.rwth-aachen.de/pnfs/physik.rwth-aachen.de/cms/\n"

		cfg_dict['storage'] = {}
		cfg_dict['storage']['se output files'] = 'kappaTuple.root'
		cfg_dict['storage']['se output pattern'] = "/@NICK@/@FOLDER@/kappa_@NICK@_@GC_JOB_ID@.@XEXT@"

		cfg_dict['condor'] = {}
		cfg_dict['condor']['JDLData'] = 'Requirements=(TARGET.CLOUDSITE=="BWFORCLUSTER") +REMOTEJOB=True'
		cfg_dict['condor']['proxy'] = "VomsProxy"

		cfg_dict['local'] = {}
		cfg_dict['local']['queue randomize'] = 'True'
		cfg_dict['local']['wms'] = 'OGE'
		cfg_dict['local']['proxy'] = 'VomsProxy'
		cfg_dict['local']['submit options'] = '-l os=sld6'

		cfg_dict['wms'] = {}
		cfg_dict['wms']['submit options'] = '-l distro=sld6'

		#cfg_dict['backend'] = {}
		#cfg_dict['backend']['ce'] = "cream-ge-2-kit.gridka.de:8443/cream-sge-sl6"
		
		cfg_dict['constants'] = {}
		cfg_dict['constants']['GC_GLITE_LOCATION'] = '/cvmfs/grid.cern.ch/emi3ui-latest/etc/profile.d/setup-ui-example.sh'
		#cfg_dict['constants']['X509_USER_PROXY'] = '$X509_USER_PROXY'

		cfg_dict['parameters'] = {}
		cfg_dict['parameters']['parameters'] = 'transform("FOLDER", "GC_JOB_ID % 100 + 1")'

		return cfg_dict

	def create_gc_config(self):
		shutil.copyfile(src=os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/higgsTauTau/",self.configfile),dst=os.path.join(self.workdir,'gc_cfg',self.configfile))
		gc_config = self.gc_default_cfg()
		for akt_nick in self.skimdataset.get_nicks_with_query(query={"GCSKIM_STATUS" : "INIT"}):
			print "Create a new config for",akt_nick
			gc_config = self.gc_default_cfg()
			self.individualized_gc_cfg(akt_nick, gc_config)
			out_file_name = os.path.join(self.workdir,'gc_cfg',akt_nick[:100]+'.conf')
			out_file = open(out_file_name,'w')
			gc_workdir = os.path.join(self.workdir,akt_nick[:100])
			if os.path.exists(gc_workdir):
				print "GC workdir for",akt_nick,"exists. Do you whish to remove? To be removed:"
				print gc_workdir
				if self.wait_for_user_confirmation(true_false=True):
					shutil.rmtree(gc_workdir)
			for akt_key in ['global','jobs','CMSSW','storage']:
				out_file.write('['+akt_key+']\n')
				for akt_item in gc_config[akt_key]:
					out_file.write(akt_item+' = '+gc_config[akt_key][akt_item]+'\n')
			for akt_key in (set(gc_config.keys()) - set(['global','jobs','CMSSW','storage'])):
				out_file.write('['+akt_key+']\n')
				for akt_item in gc_config[akt_key]:
					out_file.write(akt_item+' = '+gc_config[akt_key][akt_item]+'\n')
			out_file.close()

	def nick_list(self,in_dataset_file, tag_key = None, tag_values_str = None, query = None, nick_regex = None):
		
		self.inputdataset = datasetsHelperTwopz(in_dataset_file)
		tag_values = None
		if tag_key is None and query is None and nick_regex is None:
			return None
		if tag_values_str:
			tag_values = tag_values_str.strip('][').replace(' ','').split(',')
		
		return(self.inputdataset.get_nick_list(tag_key=tag_key, tag_values=tag_values, query=query, nick_regex=nick_regex)) 

	def prepare_resubmission_with_gc(self, nicks = None):
		
		datasets_to_resubmit = [dataset for dataset in self.skimdataset.nicks() if self.skimdataset[dataset]["SKIM_STATUS"] not in ["COMPLETED","LISTED"] and self.skimdataset[dataset]["GCSKIM_STATUS"] not in ["COMPLETED","LISTED"]]
		if nicks is not None:
			datasets_to_resubmit = [x for x in datasets_to_resubmit if x in nicks]
		self.write_while(datasets_to_submit=datasets_to_resubmit)

	def write_while(self,datasets_to_submit=None):
		if os.path.isfile(os.path.join(self.workdir,'while.sh')):
			out_file = open(os.path.join(self.workdir,'while.sh'),'r')
			print '\n\033[92m'+'GC submission script exists with following configs:'+'\033[0m'
			for line in out_file.readlines():
				if line[:5]=='go.py':
					print line.strip('go.py '+os.path.join(self.workdir,'gc_cfg'))
			out_file.close()
			print 'Overwrite? [Y/n]'
			if not self.wait_for_user_confirmation(true_false=True):
				print '\nScript will not be overwritten. To run with existing configs: '
				print os.path.join(self.workdir,'while.sh')
				return
			
		out_file = open(os.path.join(self.workdir,'while.sh'),'w')
		out_file.write('#!/bin/bash\n')
		out_file.write('\n')
		out_file.write('touch .lock\n')
		out_file.write('\n')
		out_file.write('while [ -f ".lock" ]\n')
		out_file.write('do\n')
		for dataset in datasets_to_submit:
			out_file.write('go.py '+os.path.join(self.workdir,'gc_cfg',dataset+'.conf -G\n'))
		out_file.write('echo "rm .lock"\n')
		out_file.write('sleep 2\n')
		out_file.write('done\n')
		out_file.close()
		
		os.system('chmod u+x '+os.path.join(self.workdir,'while.sh'))
		
		print '\033[92m'+'To run GC submission loop with '+str(len(datasets_to_submit))+' datasets (will run until .lock file is removed), run:'+'\033[0m'
		print os.path.join(self.workdir,'while.sh')
		print ''

	def status_gc(self):
		for dataset in self.skimdataset.nicks():
			if self.skimdataset[dataset]["GCSKIM_STATUS"] in ["SUBMITTED","INIT"]:
				gc_workdir = os.path.join(self.workdir,dataset[:100])
				if os.path.exists(gc_workdir):
					if self.skimdataset[dataset]["GCSKIM_STATUS"] == "INIT":
						print "GC task status set to SUBMITTED for:"
						print dataset
						self.skimdataset[dataset]["GCSKIM_STATUS"] = "SUBMITTED"
					gc_output_dir = os.path.join(gc_workdir,"output")
					n_gc_jobs = int(gzip.open(os.path.join(gc_workdir,"params.map.gz"), 'r').read())
					done_jobs = 0
					for i in range(n_gc_jobs):
						job_info_path = os.path.join(gc_output_dir,"job_"+str(i),"job.info")
						if os.path.exists(job_info_path):
							job_info = open(job_info_path).read().split("\n")
							for info_line in job_info:
								if info_line == "EXITCODE=0":
									done_jobs += 1
					if n_gc_jobs == done_jobs:
						print "GC task COMPLETED for",dataset
						self.skimdataset[dataset]["GCSKIM_STATUS"] = "COMPLETED"

	def individualized_gc_cfg(self, akt_nick ,gc_config):
		#se_path_base == srm://dgridsrm-fzk.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/dcms/disk-only/
		#se_path_base = 'srm://grid-srm.physik.rwth-aachen.de:8443/srm/managerv2\?SFN=/pnfs/physik.rwth-aachen.de/cms/'
		se_path_base = "srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/"
		gc_config['storage']['se path'] = se_path_base+"store/user/%s/higgs-kit/skimming/GC_SKIM/%s/"%(self.getUsernameFromSiteDB_cache(),datetime.datetime.today().strftime("%y%m%d_%H%M%S"))
		#gc_config['storage']['se output pattern'] = "FULLEMBEDDING_CMSSW_8_0_21/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
		gc_config['CMSSW']['dataset'] = akt_nick+" : "+self.skimdataset[akt_nick]['dbs']
		gc_config['CMSSW']['files per job'] = str(self.files_per_job(akt_nick))
		gc_config['global']["workdir"] = os.path.join(self.workdir,akt_nick[:100])
		
		gc_config['dataset'] = {}
		gc_config['dataset']['dbs instance'] = self.skimdataset[akt_nick].get("inputDBS",'global')
										   #URL=https://cmsdbsprod.cern.ch:8443/cms_dbs_prod_global_writer/servlet/DBSServlet
		gc_config['constants']['GLOBALTAG'] = self.get_global_tag(akt_nick)

	def submit_crab(self,filename=None):
		if len(self.skimdataset.get_nicks_with_query(query={"SKIM_STATUS" : "INIT"})) == 0:
			print "\nNo tasks will be submitted to the crab server. Set --init to add new tasks to submit.\n"
		else:
			print str(len(self.skimdataset.get_nicks_with_query(query={"SKIM_STATUS" : "INIT"})))+" tasks will be submitted to the crab server. Continue? [Y/n]"
			self.wait_for_user_confirmation()
		nerror=0
		for akt_nick in self.skimdataset.get_nicks_with_query(query={"SKIM_STATUS" : "INIT"}):
			config = self.crab_default_cfg() ## if there are parameters which should only be set for one dataset then its better to start from default again
			self.individualized_crab_cfg(akt_nick, config)
			if config.Data.inputDBS in ['list']:
				print akt_nick," needs to be run with gc sinc it is not in site db"
				continue 
			self.skimdataset[akt_nick]['outLFNDirBase'] = config.Data.outLFNDirBase
			self.skimdataset[akt_nick]['storageSite'] = config.Site.storageSite 
			self.skimdataset[akt_nick]["crab_name"] = "crab_"+config.General.requestName

			try:
				submit_dict = {"config" : config, "proxy" : self.voms_proxy}
				self.crab_cmd(cmd='submit',argument_dict=submit_dict)
				self.skimdataset[akt_nick]["SKIM_STATUS"] = "SUBMITTED"

			except exc:
				nerror+=1
				print exc
		if nerror>0:
			print nerror,'tasks raised an exception. Run again to try to resubmit.'
		self.save_dataset(filename)

	def crab_default_cfg(self):
		from CRABClient.UserUtilities import config
		config = config()
		config.General.workArea = self.workdir
		config.General.transferOutputs = True
		config.General.transferLogs = True
		config.User.voGroup = 'dcms'
		config.JobType.pluginName = 'Analysis'
		config.JobType.psetName = os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/higgsTauTau/",self.configfile)
		#config.JobType.inputFiles = ['Spring16_25nsV6_DATA.db', 'Spring16_25nsV6_MC.db']
		config.JobType.maxMemoryMB = 2500
		config.JobType.allowUndistributedCMSSW = True
		config.Site.blacklist = ["T3_FR_IPNL","T3_US_UCR","T2_BR_SPRACE","T1_RU_*","T2_RU_*","T3_US_UMiss"]
		config.Data.splitting = 'FileBased'
		config.Data.outLFNDirBase = '/store/user/%s/higgs-kit/skimming/%s'%(self.getUsernameFromSiteDB_cache(), os.path.basename(self.workdir))
		config.Data.publication = False
		config.Site.storageSite = self.storage_for_output
		return config

	def individualized_crab_cfg(self, akt_nick, config):
		config.General.requestName = akt_nick[:100]
		config.Data.inputDBS = self.skimdataset[akt_nick].get("inputDBS",'global')
		globalTag = self.get_global_tag(akt_nick)
		config.JobType.pyCfgParams = [str('globalTag=%s'%globalTag),'kappaTag=KAPPA_2_1_0',str('nickname=%s'%(akt_nick)),str('outputfilename=kappa_%s.root'%(akt_nick)),'testsuite=False']
		config.Data.unitsPerJob = self.files_per_job(akt_nick) 
		config.Data.inputDataset = self.skimdataset[akt_nick]['dbs']
		config.Data.ignoreLocality = self.skimdataset[akt_nick].get("ignoreLocality", True) ## i have very good experince with this option, but feel free to change it (maybe also add larger default black list for this, or start with a whitlist 
		config.Site.blacklist.extend(self.skimdataset[akt_nick].get("blacklist", []))
		config.JobType.outputFiles = [str('kappa_%s.root'%(akt_nick))]

	def files_per_job(self, akt_nick):
		job_submission_limit=10000
		if self.skimdataset[akt_nick].get("files_per_job", None):
			return int(self.skimdataset[akt_nick]["files_per_job"])
		elif self.skimdataset[akt_nick].get("n_files", None):
			nfiles = int(self.skimdataset[akt_nick]["n_files"])
			if nfiles > self.max_crab_jobs_per_nick:
				from math import ceil
				return int(ceil(float(nfiles)/float(job_submission_limit)))	
			else:
				return 1
		return 1

	def status_crab(self):
		self.get_status_crab()
		self.update_status_crab()

	def get_status_crab(self):
		for akt_nick in self.skimdataset.nicks():
			if self.skimdataset[akt_nick]["SKIM_STATUS"] not in ["LISTED","COMPLETED","INIT"] and self.skimdataset[akt_nick]["GCSKIM_STATUS"] not in ["LISTED","COMPLETED"]:
				crab_job_dir = os.path.join(self.workdir,self.skimdataset[akt_nick]["crab_name"])
				status_dict = {"proxy" : self.voms_proxy, "dir" : crab_job_dir}
				self.skimdataset[akt_nick]['last_status'] = self.crab_cmd(cmd='status', argument_dict = status_dict)
				if not self.skimdataset[akt_nick]['last_status']:
					self.skimdataset[akt_nick]["SKIM_STATUS"] = "EXCEPTION"

	def update_status_crab(self):
		for akt_nick in self.skimdataset.nicks():

			if self.skimdataset[akt_nick]["SKIM_STATUS"] not in ["LISTED","COMPLETED"]:
				all_jobs = 0
				done_jobs = 0
				try:
					self.skimdataset[akt_nick]["SKIM_STATUS"] = self.skimdataset[akt_nick]['last_status']['status']
					for job_per_status in self.skimdataset[akt_nick]['last_status'].get('jobsPerStatus',{}).keys():
						all_jobs += self.skimdataset[akt_nick]['last_status']['jobsPerStatus'][job_per_status]
						if job_per_status == 'finished':
							done_jobs += self.skimdataset[akt_nick]['last_status']['jobsPerStatus'][job_per_status]
				except:
					pass
				self.skimdataset[akt_nick]['crab_done'] = 0.0 if all_jobs == 0  else round(float(100.0*done_jobs)/float(all_jobs),2)
				self.skimdataset[akt_nick]['n_jobs'] = max(all_jobs,self.skimdataset[akt_nick].get('n_jobs',0))

	def print_skim(self,summary=False):
		print "---------------------------------------------------------"
		if summary:
			status_dict={}
			status_dict.setdefault('COMPLETED', [])
			status_dict.setdefault('EXCEPTION', [])
			status_dict.setdefault('FAILED', [])
			status_dict.setdefault('UNKNOWN', [])
			status_dict.setdefault('SUBMITTED', [])

		for akt_nick in self.skimdataset.nicks():
			print akt_nick," ",self.skimdataset[akt_nick]["SKIM_STATUS"],'\t Done: ',self.skimdataset[akt_nick].get('crab_done', 0.0),'% '
			
			if summary:
				if self.skimdataset[akt_nick]["SKIM_STATUS"] in ["COMPLETED","LISTED"] or self.skimdataset[akt_nick]["GCSKIM_STATUS"] in ["COMPLETED","LISTED"]:
					status_dict['COMPLETED'].append(akt_nick)
				elif self.skimdataset[akt_nick]["SKIM_STATUS"] in ["SUBMITTED","QUEUED","UNKNOWN","NEW"]:
					status_dict['SUBMITTED'].append(akt_nick)
				elif self.skimdataset[akt_nick]["SKIM_STATUS"] in ["FAILED","RESUBMITFAILED"]:
					status_dict['FAILED'].append(akt_nick)
				elif self.skimdataset[akt_nick]["SKIM_STATUS"] in ["EXCEPTION"]:
					status_dict['EXCEPTION'].append(akt_nick)

		if summary:
			print '\n'+'\033[92m'+'COMPLETED: '+str(len(status_dict['COMPLETED']))+' tasks'+'\033[0m'
			for nick in status_dict['COMPLETED']:
				print nick
			print '\n'+'\033[91m'+'FAILED: '+str(len(status_dict['FAILED']))+' tasks'+'\033[0m'
			for nick in status_dict['FAILED']:
				print nick
			print '\n'+'\033[93m'+'EXCEPTION: '+str(len(status_dict['EXCEPTION']))+' tasks'+'\033[0m'
			for nick in status_dict['EXCEPTION']:
				print nick
			print '\n'+'SUBMITTED: '+str(len(status_dict['SUBMITTED']))+' tasks'
			for nick in status_dict['SUBMITTED']:
				print nick
			print '\n'
			status_json = open(os.path.join(self.workdir,'skim_summary.json'), 'w')
			status_json.write(json.dumps(status_dict, sort_keys=True, indent=2))
			status_json.close()

	def get_crab_taskIDs(self):
		output = subprocess.check_output("crab tasks", shell=True)
		tasks=[]
		for line in output.splitlines():
			if len(line) > 0:
				if line[0].isdigit():
					tasks.append(line)
		return tasks

	def remake_all(self):
		tasks = self.get_crab_taskIDs()
		for task in tasks:
			os.system('crab remake --task='+task)

	def kill_all(self):
		for dirpath,dirnames,fielnames in os.walk(self.workdir):
			for dirname in dirnames:
				if "crab" in dirname:
					crab_dir = os.path.join(dirpath,dirname)
					os.system('crab kill -d '+crab_dir)

	def purge_all(self):
		for dirpath,dirnames,fielnames in os.walk(self.workdir):
			for dirname in dirnames:
				if "crab" in dirname:
					crab_dir = os.path.join(dirpath,dirname)
					os.system('crab purge -d '+crab_dir)

	def remake_task(self,inputfile):
		nicks_to_remake = [nick for nick in self.skimdataset.nicks() if self.skimdataset[nick]["SKIM_STATUS"] == "EXCEPTION"]
		all_subdirs = [os.path.join(self.workdir,self.skimdataset[akt_nick]["crab_name"]) for akt_nick in nicks_to_remake]
		print len(all_subdirs),'tasks that raised an exception will be remade. This will delete and recreate those folders in the workdir.'
		print 'Do you want to continue? [Y/n]'
		self.wait_for_user_confirmation()

		print '\033[94m'+'Getting crab tasks...'+'\033[0m'
		tasks = self.get_crab_taskIDs()
		idir=1
		for subdir,nick in zip(all_subdirs,nicks_to_remake):
			print '\033[94m'+'('+str(idir)+'/'+str(len(all_subdirs))+')	REMAKING '+os.path.basename(subdir)+'\033[0m'
			idir+=1
			task_exists = False
			for task in tasks:
				if os.path.basename(subdir) in task:
					task_exists=True
					if os.path.exists(subdir):
						shutil.rmtree(subdir)
					os.system('crab remake --task='+task)
					os.system('crab resubmit -d '+subdir)
					nicks_to_remake.remove(nick)
					break
			if not task_exists:
				print '\033[94m'+nick+' will be RESUBMITTED by hand'+'\033[0m'
				if os.path.exists(subdir):
					shutil.rmtree(subdir)
				self.skimdataset.base_dict.pop(nick)
		if len(nicks_to_remake) > 0:
			self.add_new(nicks_to_remake)
			self.submit_crab()

	def resubmit_failed(self,argument_dict):
		datasets_to_resubmit = []
		for dataset in self.skimdataset.nicks():
			if self.skimdataset[dataset]["SKIM_STATUS"] not in ["COMPLETED","LISTED"] and self.skimdataset[dataset]["GCSKIM_STATUS"] not in ["COMPLETED","LISTED"]:
				try:
					if "failed" in self.skimdataset[dataset]["last_status"]["jobsPerStatus"]:
						datasets_to_resubmit.append(self.skimdataset[dataset]["crab_name"])
				except:
					print "Failed to resubmit crab task",dataset,". Possibly a problem with the skim_dataset.json. Try to recover the status of the task properly."
					pass
		print "Try to resubmit",len(datasets_to_resubmit),"tasks"
		for dataset in datasets_to_resubmit:
			print "Resubmission for",dataset
			argument_dict["dir"] = os.path.join(self.workdir,str(dataset))
			self.crab_cmd(cmd="resubmit", argument_dict = argument_dict)
			print "--------------------------------------------"

	def create_filelist(self):
		filelist_folder_name = os.path.relpath(self.workdir,SkimManagerBase.get_workbase())
		skim_path = os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data",filelist_folder_name)
		if not os.path.exists(skim_path):
			 os.makedirs(skim_path)
		for dataset in self.skimdataset.nicks():
			storage_site = self.skimdataset[dataset]["storageSite"]
			# File list for GC first
			if self.skimdataset[dataset]["GCSKIM_STATUS"] == "COMPLETED":
				gc_output_dir = os.path.join(self.workdir,dataset[:100],"output")
				n_jobs_info = os.path.join(self.workdir,dataset[:100],"params.map.gz")
				if os.path.exists(n_jobs_info):
					print "Getting GC file list for",dataset
					filelist = open(skim_path+'/'+dataset+'.txt', 'w')
					n_gc_jobs = int(gzip.open(n_jobs_info, 'r').read())
					done_jobs = 0
					for i in range(n_gc_jobs):
						job_info_path = os.path.join(gc_output_dir,"job_"+str(i),"job.info")
						if os.path.exists(job_info_path):
							job_info = open(job_info_path).read().split("\n")
							for info_line in job_info:
								if info_line.startswith("FILE="):
									file_path_parts = info_line.strip('"').split("  ")[-2:]
									filelist.write(self.site_storage_access_dict[storage_site]+re.sub(r'.*(store)',r'/store',file_path_parts[1]+file_path_parts[0]+"\n"))
					filelist.close()
					self.skimdataset[dataset]["GCSKIM_STATUS"] = "LISTED"
					print "List creation successfull!"
					print "---------------------------------------------------------"
			# If GC task not completed, create a crab filelist
			elif self.skimdataset[dataset]["SKIM_STATUS"] == "COMPLETED" and self.skimdataset[dataset]["GCSKIM_STATUS"] != "LISTED":
				print "Getting CRAB file list for",dataset
				dataset_filelist = subprocess.check_output("crab getoutput --xrootd --dir {DATASET_TASK}".format(
					DATASET_TASK=os.path.join(self.workdir,self.skimdataset[dataset]["crab_name"])), shell=True)
				if "root" in dataset_filelist:
					filelist = open(skim_path+'/'+dataset+'.txt', 'w')
					filelist.write(dataset_filelist.replace("root://cms-xrd-global.cern.ch/",self.site_storage_access_dict[storage_site]))
					filelist.close()
					self.skimdataset[dataset]["SKIM_STATUS"] = "LISTED"
					print "List creation successfull!"
				print "---------------------------------------------------------"

		print "End of list creation."

	def reset_filelist(self):
		for dataset in self.skimdataset.nicks():
			if self.skimdataset[dataset]["SKIM_STATUS"] == "LISTED":
				self.skimdataset[dataset]["SKIM_STATUS"] = "COMPLETED"
			elif self.skimdataset[dataset]["GCSKIM_STATUS"] == "LISTED":
				self.skimdataset[dataset]["GCSKIM_STATUS"] = "COMPLETED"

	@classmethod
	def get_workbase(self):
		if os.environ.get('SKIM_WORK_BASE') is not None:
			return(os.environ['SKIM_WORK_BASE'])
		else:
			if 'ekpbms1' in os.environ["HOSTNAME"]:
				return("/portal/ekpbms1/home/%s/kappa_skim_workdir/" % os.environ["USER"])
			elif 'ekpbms2' in os.environ["HOSTNAME"]:
				return("/portal/ekpbms2/home/%s/kappa_skim_workdir/" % os.environ["USER"])
			elif 'naf' in os.environ["HOSTNAME"]:
				return("/nfs/dust/cms/user/%s/kappa_skim_workdir/" % os.environ["USER"])
			elif 'aachen' in os.environ["HOSTNAME"]:
				return("/net/scratch_cms/institut_3b/%s/kappa_skim_workdir/" % os.environ["USER"])
			else:
				log.critical("Default workbase could not be found. Please specify working dir as absolute path.")
				sys.exit()

	@classmethod
	def get_latest_subdir(self,work_base):
		all_subdirs = [work_base+d for d in os.listdir(work_base) if os.path.isdir(work_base+d)]
		return(max(all_subdirs, key=os.path.getmtime))

	@classmethod
	def wait_for_user_confirmation(self,true_false=False):
		choice = raw_input().lower()
		if choice in set(['yes','y','ye', '']):
			if true_false:
				return True
			pass
		elif choice in set(['no','n']):
			if true_false:
				return False
			exit()
		else:
			print "Please respond with yes or no"
			exit()

if __name__ == "__main__":

	work_base = SkimManagerBase.get_workbase()
	latest_subdir = SkimManagerBase.get_latest_subdir(work_base=work_base)
	def_input = os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/datasets.json")

	parser = argparse.ArgumentParser(prog='./DatasetManager.py', usage='%(prog)s [options]', description="Tools for modify the dataset data base (aka datasets.json)")

	parser.add_argument("-i", "--input", dest="inputfile", default=def_input, help="input data base (Default: %s)"%def_input)
	parser.add_argument("-w", "--workdir", dest="workdir", help="Set work directory  (Default: Latest modified subdir, i.e. %s) in workbase %s.\nWorkbase can be set by export SKIM_WORK_BASE=workbase or by setting absolute path."%(latest_subdir,work_base), default=latest_subdir)
	parser.add_argument("-d", "--date", dest="date", action="store_true", default=False, help="Add current date to workdir folder (Default: %(default)s)")
	parser.add_argument("--query", dest="query", help="Query which each dataset has to fulfill. Works with regex e.g: --query '{\"campaign\" : \"RunIISpring16MiniAOD.*reHLT\"}' \n((!!! For some reasons the most outer question marks must be the \'))")
	parser.add_argument("--nicks", dest="nicks", help="Query which each dataset has to fulfill. Works with regex e.g: --nicks \".*_Run2016(B|C|D).*\"")
	parser.add_argument("--tag", dest="tag", help="Ask for a specific tag of a dataset. Optional arguments are --TagValues")
	parser.add_argument("--tagvalues", dest="tagvalues", help="The tag values, must be a comma separated string (e.g. --TagValues \"Skim_Base',Skim_Exetend\" ")
	parser.add_argument("--storage-for-output",dest="storage_for_output",default="T2_DE_DESY",help="Specifies the storage element you want to write your outputs to. Default: %(default)s")

	parser.add_argument("--init", dest="init", help="Init or Update the dataset", action='store_true')

	parser.add_argument("--status-gc", action='store_true', default=False, dest="statusgc",help="")
	parser.add_argument("--summary", action='store_true', default=False, dest="summary", help="Prints summary and writes skim_summary.json in workdir with quick status overview of crab tasks.")

	parser.add_argument("--resubmit-with-options", default=None, dest="resubmit", help="Resubmit failed tasks. Options for crab resubmit can be specified via a python dict, e.g: --resubmit '{\"maxmemory\" : \"3000\", \"maxruntime\" : \"1440\"}'. To avoid options use '{}' Default: %(default)s")
	parser.add_argument("--resubmit-with-gc", action='store_true', default=False, dest="resubmit_with_gc", help="Resubmits non-completed tasks with Grid Control.")
	parser.add_argument("--remake", action='store_true', default=False, dest="remake", help="Remakes tasks where exception occured. (Run after --crab-status). Default: %(default)s")
	parser.add_argument("--remake-all", action='store_true', default=False, dest="remake_all", help="Remakes all tasks. (Remakes .requestcache file). Default: %(default)s")
	parser.add_argument("--kill-all", action='store_true', default=False, dest="kill_all", help="kills all tasks. Default: %(default)s")
	parser.add_argument("--purge-all", action='store_true', default=False, dest="purge_all", help="purges all tasks. Default: %(default)s")
	
	parser.add_argument("--create-filelist", action='store_true', default=False, dest = "create_filelist", help="")
	parser.add_argument("--reset-filelist", action='store_true', default=False, dest = "reset_filelist", help="")

	args = parser.parse_args()
	if args.workdir == latest_subdir:
		print "\nWorkdir not specified. Latest subdir in workbase will be used: "+latest_subdir
		print "Continue? [Y/n]"
		SkimManagerBase.wait_for_user_confirmation()
	if not os.path.exists(args.inputfile):
		print 'No input file found'
		exit()
	if args.date:
		args.workdir+="_"+datetime.date.today().strftime("%Y-%m-%d")
	
	SKM = SkimManagerBase(storage_for_output=args.storage_for_output,workbase=work_base,workdir=args.workdir)
	nicks = SKM.nick_list(args.inputfile, tag_key=args.tag, tag_values_str=args.tagvalues, query=args.query, nick_regex=args.nicks)

	if args.init:
		SKM.add_new(nicks)
		SKM.create_gc_config()

	if args.remake_all:
		SKM.remake_all()

	if args.kill_all:
		SKM.kill_all()
		exit()

	if args.purge_all:
		SKM.purge_all()
		exit()

	if args.remake:
		SKM.remake_task(args.inputfile)
		exit()

	if args.resubmit:
		SKM.resubmit_failed(argument_dict=ast.literal_eval(args.resubmit))
		exit()

	if args.create_filelist:
		SKM.create_filelist()
		SKM.save_dataset()
		exit()

	if args.reset_filelist:
		SKM.reset_filelist()
		SKM.save_dataset()
		exit()

	if args.resubmit_with_gc:
		SKM.prepare_resubmission_with_gc(nicks = nicks)
		exit()

	if args.statusgc:
		SKM.status_gc()

	else:
		SKM.submit_crab()
		SKM.status_crab()
		SKM.print_skim(summary=args.summary)

	SKM.save_dataset()
