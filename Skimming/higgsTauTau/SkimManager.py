#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import os, shutil
from  Kappa.Skimming.datasetsHelperTwopz import datasetsHelperTwopz
import argparse
import datetime
import subprocess
import json 

def crab_cmd(cmd, config=None, proxy=None, crab_dir=None):
	from httplib import HTTPException
	from CRABAPI.RawCommand import crabCommand
	from CRABClient.ClientExceptions import ClientException
	try:
		if not config:
			return crabCommand(cmd, proxy=proxy, dir=crab_dir)
		else:
			return crabCommand(cmd, config = config,proxy=proxy)
	except HTTPException as hte:
		print "Failed submitting task: %s" % (hte.headers)
	except ClientException as cle:
		print "Failed submitting task: %s" % (cle)


class SkimManagerBase:
	def __init__(self, workbase=".", workdir="TEST_SKIM", use_proxy_variable=False):
		self.workdir = os.path.join(workbase,workdir)
		if not os.path.exists(self.workdir+"/gc_cfg"): 
			os.makedirs(self.workdir+"/gc_cfg")
		self.skimdataset = datasetsHelperTwopz(os.path.join(self.workdir,"skim_dataset.json"))
		self.skimdataset.keep_input_json = False ## will be updated very often
		self.configfile = 'kSkimming_run2_cfg_v2.py'
		self.max_crab_jobs_per_nick = 8000 # 10k is the hard limit
		self.voms_proxy = None
		self.UsernameFromSiteDB = None
		try:
			self.voms_proxy=os.environ['X509_USER_PROXY']
		except:
			pass
			
	#~ def  __del__(self): 
		#~ self.save_dataset()
		
	def save_dataset(self,filename=None):
		self.skimdataset.write_to_jsonfile(filename)  
		
	def add_new(self, in_dataset_file,  tag_key = None, tag_values_str = None, query = None, nick_regex = None):
		self.inputdataset = datasetsHelperTwopz(in_dataset_file)
		tag_values = None
		if tag_values_str:
			tag_values = tag_values_str.strip('][').replace(' ','').split(',')

		if not tag_key and not query and not nick_regex:
			print "You must select something [see options --query,--nicks  or --tag (with --tagvalues)]"
		else:
			for new_nick in self.inputdataset.get_nick_list(tag_key=tag_key, tag_values=tag_values, query=query, nick_regex=nick_regex):
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
		return self.skimdataset[akt_nick].get("globalTag", '80X_dataRun2_2016SeptRepro_v4' if self.skimdataset.isData(akt_nick) else '80X_mcRun2_asymptotic_2016_miniAODv2_v1')
		
	def gc_default_cfg(self):
		cfg_dict = {}
		cfg_dict['global'] = {}
		cfg_dict['global']['task']  = 'CMSSW'   
		cfg_dict['global']['backend']  = 'condor'
		#cfg_dict['global']['backend']  = 'local'
		#cfg_dict['global']['backend']  = 'cream'		
		cfg_dict['global']["workdir create"] = 'True '

		cfg_dict['jobs'] = {}
		cfg_dict['jobs']['in flight'] = '4000'
		cfg_dict['jobs']['wall time'] = '02:00:00'
		cfg_dict['jobs']['memory'] = '4000'
		#cfg_dict['jobs']['jobs'] = '5'
		
		
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
		cfg_dict['storage']['se output pattern'] = "SKIMMING_CMSSW_8_0_21_try2/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
	
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
			gc_config = self.gc_default_cfg()
			self.individualized_gc_cfg(akt_nick, gc_config)
			out_file_name = os.path.join(self.workdir,'gc_cfg',akt_nick[:100]+'.conf')
			out_file = open(out_file_name,'w')
			for akt_key in ['global','jobs','CMSSW','storage']:
				out_file.write('['+akt_key+']\n')
				for akt_item in gc_config[akt_key]:
					out_file.write(akt_item+' = '+gc_config[akt_key][akt_item]+'\n')
			for akt_key in (set(gc_config.keys()) - set(['global','jobs','CMSSW','storage'])):
				out_file.write('['+akt_key+']\n')
				for akt_item in gc_config[akt_key]:
					out_file.write(akt_item+' = '+gc_config[akt_key][akt_item]+'\n')
			#print 'go.py '+out_file_name+' -Gc -m 1'
			out_file.close()
			
	def submit_gc(self, in_dataset_file,  tag_key = None, tag_values_str = None, query = None, nick_regex = None):
		
		allconfigs = [c for c in os.listdir(os.path.join(self.workdir,'gc_cfg')) if c[-5:]=='.conf']
		
		self.inputdataset = datasetsHelperTwopz(in_dataset_file)
		tag_values = None
		if tag_values_str:
			tag_values = tag_values_str.strip('][').replace(' ','').split(',')
		
		configlist = []
		for new_nick in self.inputdataset.get_nick_list(tag_key=tag_key, tag_values=tag_values, query=query, nick_regex=nick_regex):
			for config in allconfigs:
				if new_nick in config:
					configlist.append(config)
					break
		if len(configlist)==0:
			print 'No Grid control configs for query could be found. Please run again with --init to create configs.'
		else:
			print str(len(configlist))+' Grid Control tasks will be submitted. Continue? [Y/n]'
		self.wait_for_user_confirmation()
		for c in configlist:
			os.system('go.py '+os.path.join(self.workdir,'gc_cfg',c)+' -m 5')
	
	def status_gc(self,check_completed=False):
		readfile = open(os.path.join(self.workdir,'completed_untilgc.txt'),'r')
		clist = readfile.read().splitlines()
		
		workdirlist = [d for d in os.listdir(os.path.join(self.workdir)) if (os.path.isdir(os.path.join(self.workdir,d)) and d not in clist)]
		n = len(workdirlist)
		completed=[]
		running=[]
		#readfile = open(os.path.join(self.workdir,'completed_untilgc.txt'),'r')
		if check_completed:
			f = open(os.path.join(self.workdir,'completed.txt'),'w')
			status_dict={}
			status_dict.setdefault('completed', []).extend(x for x in completed)
			status_json = open(os.path.join(self.workdir,'gc_status.json'), 'w')
		i=1
		for d in workdirlist:
			print str(i)+'/'+str(n)+' '+d
			i+=1
			if not check_completed:
				try:
					os.system('go.py '+os.path.join(self.workdir,d,'current.conf'))
				except:
					pass
			else:
				try:
					if 'Task successfully completed' in subprocess.check_output('go.py '+os.path.join(self.workdir,d,'current.conf'), shell=True):
						print '\033[92m'+os.path.basename(d)+' COMPLETED'+'\033[0m'
						completed.append(d)
						status_dict.setdefault('completed', []).extend(x for x in completed)
						status_json.write(json.dumps(status_dict, sort_keys=True, indent=2))
						f.write("%s\n" % d)
				except:
					pass
		if check_completed:
			f.close()
			status_json.close()
			
	
	def individualized_gc_cfg(self, akt_nick ,gc_config):
		
			#se_path_base == srm://dgridsrm-fzk.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/dcms/disk-only/
			#se_path_base = 'srm://grid-srm.physik.rwth-aachen.de:8443/srm/managerv2\?SFN=/pnfs/physik.rwth-aachen.de/cms/'
			se_path_base = "srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/"
			gc_config['storage']['se path'] = se_path_base+"store/user/%s/higgs-kit/skimming/GC_SKIM/%s/"%(self.getUsernameFromSiteDB_cache(), os.path.basename(self.workdir))
			#gc_config['storage']['se output pattern'] = "FULLEMBEDDING_CMSSW_8_0_21/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
			gc_config['CMSSW']['dataset'] = akt_nick+" : "+self.skimdataset[akt_nick]['dbs']
			gc_config['CMSSW']['files per job'] = str(self.files_per_job(akt_nick))
			gc_config['global']["workdir"] = os.path.join(self.workdir,akt_nick[:100])
			
			gc_config['dataset'] = {}
			gc_config['dataset']['dbs instance'] = self.skimdataset[akt_nick].get("inputDBS",'global')
											   #URL=https://cmsdbsprod.cern.ch:8443/cms_dbs_prod_global_writer/servlet/DBSServlet
			gc_config['constants']['GLOBALTAG'] = self.get_global_tag(akt_nick)

			
	def submit_crab(self,filename=None):
		from multiprocessing import Process
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
			#~ f = open('config_'+akt_nick+'.py','w')
			#~ f.write(str(config))
			#~ f.close
			#~ continue
			
			try:
				crab_cmd(cmd='submit',config=config,proxy=self.voms_proxy)
				self.skimdataset[akt_nick]["SKIM_STATUS"] = "SUBMITTED"

			except exc:
				nerror+=1
				print exc
			#~ p = Process(target=crab_cmd, args=('submit',config,self.voms_proxy))
			#~ p.start()
			#~ p.join()  ###make no sens for multiprocessing here, since python will wait until p is finished. Solution would be to save all p's and then join them in in a seperate loop. 
		if nerror>0:
			print str(nerror)+' tasks raised an exception. Run again to try to resubmit.'
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
		config.JobType.allowUndistributedCMSSW = True
		config.Site.blacklist = ["T2_BR_SPRACE","T1_RU_JINR"]
		config.Data.splitting = 'FileBased'
		config.Data.outLFNDirBase = '/store/user/%s/higgs-kit/skimming/%s'%(self.getUsernameFromSiteDB_cache(), os.path.basename(self.workdir))
		config.Data.publication = False
		config.Site.storageSite = "T2_DE_DESY"
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
			if self.skimdataset[akt_nick]["SKIM_STATUS"] in ["SUBMITTED",'SUBMIT',"RUNNING","NEW"]:
				crab_job_dir = os.path.join(self.workdir,self.skimdataset[akt_nick]["crab_name"])
				self.skimdataset[akt_nick]['last_status'] = crab_cmd('status',None,self.voms_proxy,crab_job_dir)
	
	def update_status_crab(self):
		for akt_nick in self.skimdataset.nicks():
			all_jobs = 0
			done_jobs = 0
			try:
				self.skimdataset[akt_nick]["SKIM_STATUS"] = self.skimdataset[akt_nick]['last_status']['status']
				for job_per_status in self.skimdataset[akt_nick]['last_status'].get('jobsPerStatus',{}).keys():
					all_jobs += self.skimdataset[akt_nick]['last_status']['jobsPerStatus'][job_per_status]
					if job_per_status in ['done','finished']:
						done_jobs = done_jobs+self.skimdataset[akt_nick]['last_status']['jobsPerStatus'][job_per_status]	
			except:
				pass
			self.skimdataset[akt_nick]['crab_done'] = 0.0 if all_jobs == 0  else round(float(100.0*done_jobs)/float(all_jobs),2)
			self.skimdataset[akt_nick]['n_jobs'] = max(all_jobs,self.skimdataset[akt_nick].get('n_jobs',0))

		
		
	def print_skim(self):
		print "---------------------------------------------------------"
	##  for akt_nick in self.skimdataset.get_nicks_with_query(query={"SKIM_STATUS" : "DONE"})
		for akt_nick in self.skimdataset.nicks():
			self.skimdataset[akt_nick]["GCSKIM_STATUS"] = "INIT"
			print akt_nick," ",self.skimdataset[akt_nick]["SKIM_STATUS"],'\t Done: ',self.skimdataset[akt_nick].get('crab_done', 0.0),'% '
	
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

	def remake_task(self,inputfile,resubmit=False):
		
		if os.path.exists(os.path.join(self.workdir,'crab_status.json')):
			check_json = json.load(open(os.path.join(self.workdir,'crab_status.json')))
			ntask = len(check_json['exception'])
			print str(ntask)+' tasks that raised an exception will be remade. This will delete and recreate those folders in the workdir.'
			print 'Do you want to continue? [Y/n]'
			self.wait_for_user_confirmation()
			all_subdirs = [os.path.join(self.workdir,d) for d in os.listdir(self.workdir) if d in check_json['exception'] and os.path.isdir(os.path.join(self.workdir,d))]
		else:
			all_subdirs = [os.path.join(self.workdir,d) for d in os.listdir(self.workdir) if os.path.isdir(os.path.join(self.workdir,d))]
			if os.path.join(self.workdir,'gc_cfg') in all_subdirs:
				all_subdirs.remove(os.path.join(self.workdir,'gc_cfg'))
			check_json = {}
			check_json['exception']=[]
			print 'crab_status.json could not be found. Please run with --crab-status to create and get list of all jobs that raise exception.'
			print 'Do you want to remake all '+str(len(all_subdirs))+' crab tasks in current workdir? This will delete and recreate those folders in the workdir. [Y/n]'
			self.wait_for_user_confirmation()
		print '\033[94m'+'Getting crab tasks...'+'\033[0m'
		tasks = self.get_crab_taskIDs()
		idir=1
		for subdir in all_subdirs:
			print '\033[94m'+'('+str(idir)+'/'+str(ntask)+')	REMAKING '+os.path.basename(subdir)+'\033[0m'
			idir+=1
			task_exists = False
			for task in tasks:
				if os.path.basename(subdir)[5:] in task:
					task_exists=True
					os.chdir(self.workdir)
					shutil.rmtree(os.path.join(self.workdir,os.path.basename(subdir)))
					os.system('crab remake --task='+task)
					os.system('crab resubmit -d '+os.path.join(self.workdir,os.path.basename(subdir)))
					break
			if not task_exists:
				#print '\033[91m'+os.path.basename(subdir)+' COULD NOT BE REMADE AS NO MATCHING TASK IS KNOWN TO CRAB.'+'\033[0m'
				if resubmit:
					print'\033[94m'+'RESUBMITTING...'+'\033[0m'		
					#os.chdir(self.workdir)
					shutil.rmtree(os.path.join(self.workdir,os.path.basename(subdir)))
					self.add_new(in_dataset_file=inputfile,nick_regex = os.path.basename(subdir)[5:])
					self.submit_crab()
	
	def write_crab_status(self,remake=False,in_dataset_file=None,resubmit=False):
		''''''
		all_subdirs = [os.path.join(self.workdir,d) for d in os.listdir(self.workdir) if os.path.isdir(os.path.join(self.workdir,d))]
		if os.path.join(self.workdir,'gc_cfg') in all_subdirs:
			all_subdirs.remove(os.path.join(self.workdir,'gc_cfg'))
		completed = []
		exception = []
		running = []
		failed = []
		ndirs = len(all_subdirs)
		if remake:
			tasks = self.show_crab_taskID()
		if os.path.exists(os.path.join(self.workdir,'crab_status.json')):
			check_json = json.load(open(os.path.join(self.workdir,'crab_status.json'), 'r'))
			ncomplete = len(check_json['completed'])
			for x in check_json['completed']:
				completed.append(x)
		else:
			ncomplete = 0
			check_json = {}
			check_json['completed']=[]
			check_json['running']=[]
			check_json['exception']=[]
			check_json['failed']=[]
		nrequest = ndirs - ncomplete

		print 'Getting status of '+str(nrequest)+' jobs. '+str(ncomplete)+' jobs in this campaign are already completed.'
		irequest = 1
		for subdir in all_subdirs:
			if os.path.basename(subdir) not in completed:
			#if True:
			#if os.path.basename(subdir) in check_json['exception']:
				print '\033[94m'+'('+str(irequest)+'/'+str(nrequest)+')'+'\033[0m'+'	Getting status of '+os.path.basename(subdir)+'...'
				irequest+=1
				try:
					output = subprocess.check_output('crab status -d '+subdir, shell=True)
					if 'COMPLETED' in output:
						print '\033[92m'+'COMPLETED'+'\033[0m'
						completed.append(os.path.basename(subdir))
					else:
						if 'FAILED' in output:
							print '\033[91m'+'FAILED'+'\033[0m'
							print output
							if resubmit:
								print'\033[94m'+'RESUBMITTING...'+'\033[0m'
								os.system('crab resubmit -d '+subdir)
								running.append(os.path.basename(subdir))
							else:
								failed.append(os.path.basename(subdir))

						else:
							running.append(os.path.basename(subdir))
							print output
							if resubmit:
								if 'failed' in output:
									print '\033[94m'+'RESUBMITTING...'+'\033[0m'
									os.system('crab resubmit -d '+subdir)

				except Exception as exc:
					print '\033[93m'+'EXCEPTION OCCURED WHILE GETTING STATUS:'+'\033[0m'
					print exc
					exception.append(os.path.basename(subdir))
					if remake:
						print '\033[93m'+'REMAKING...'+'\033[0m'
														
		print '\033[92m'+'COMPLETED:	'+str(round(100*(float(len(completed)))/float(ndirs),2))+'% ('+str(len(completed))+'/'+str(ndirs)+')'+'\033[0m'
		print 'IDLE/RUNNING:	'+str(round(100*float(len(running))/float(ndirs),2))+'% ('+str(len(running))+'/'+str(ndirs)+')'
		if len(exception)>0:
			print '\033[93m'+'EXCEPTION:	'+str(round(100*float(len(exception))/float(ndirs),2))+'% ('+str(len(exception))+'/'+str(ndirs)+')'+'\033[0m'
		if len(failed)>0:
			print '\033[91m'+'FAILED:		'+str(round(100*float(len(failed))/float(ndirs),2))+'% ('+str(len(failed))+'/'+str(ndirs)+')'+'\033[0m'+'\033[0m'
			print 'Run again with --resubmit to resubmit failed tasks.'
		print 'Check '+os.path.join(self.workdir,'crab_status.json')+' for details.'
		status_dict={}
		status_dict.setdefault('completed', []).extend(x for x in completed)
		status_dict.setdefault('running', []).extend(x for x in running)
		status_dict.setdefault('exception', []).extend(x for x in exception)
		status_dict.setdefault('failed', []).extend(x for x in failed)
		status_json = open(os.path.join(self.workdir,'crab_status.json'), 'w')
		status_json.write(json.dumps(status_dict, sort_keys=True, indent=2))
		status_json.close()
		
		
	def resubmit_failed(self,memory=None):
		all_subdirs = [os.path.join(self.workdir,d) for d in os.listdir(self.workdir) if os.path.isdir(os.path.join(self.workdir,d))]
		if os.path.exists(os.path.join(self.workdir,'crab_status.json')):
			check_json = json.load(open(os.path.join(self.workdir,'crab_status.json')))
		else:
			check_json = {}
			check_json['completed']=[]
			
		for subdir in all_subdirs:
			if os.path.basename(subdir) not in check_json['completed']:
				if memory is not None:
					os.system('crab resubmit -d '+subdir+' --maxmemory '+memory)
				else:
					os.system('crab resubmit -d '+subdir)
	
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
	def wait_for_user_confirmation(self):
		choice = raw_input().lower()
		if choice in set(['yes','y','ye', '']):
			pass
		elif choice in set(['no','n']):
		   exit()
		else:
		   sys.stdout.write("Please respond with 'yes' or 'no'") 

if __name__ == "__main__":
	
	work_base = SkimManagerBase.get_workbase()
	print work_base
	latest_subdir = SkimManagerBase.get_latest_subdir(work_base=work_base)
	def_input = os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/datasets_conv.json")

	parser = argparse.ArgumentParser(prog='./DatasetManager.py', usage='%(prog)s [options]', description="Tools for modify the dataset data base (aka datasets.json)") 
	parser.add_argument("-i", "--input", dest="inputfile", default=def_input, help="input data base (Default: %s)"%def_input)
	parser.add_argument("-w", "--workdir", dest="workdir", help="Set work directory  (Default: Latest modified subdir, i.e. %s) in workbase %s.\nWorkbase can be set by export SKIM_WORK_BASE=workbase or by setting absolute path."%(latest_subdir,work_base), default=latest_subdir)
	parser.add_argument("-d", "--date", dest="date", action="store_true", default=False, help="Add current date to workdir folder (Default: %(default)s)")
	parser.add_argument("--query", dest="query", help="Query which each dataset has to fulfill. Works with regex e.g: --query '{\"campaign\" : \"RunIISpring16MiniAOD.*reHLT\"}' \n((!!! For some reasons the most outer question marks must be the \'))")
	parser.add_argument("--nicks", dest="nicks", help="Query which each dataset has to fulfill. Works with regex e.g: --nicks \".*_Run2016(B|C|D).*\"")
	parser.add_argument("--tag", dest="tag", help="Ask for a specific tag of a dataset. Optional arguments are --TagValues")
	parser.add_argument("--tagvalues", dest="tagvalues", help="The tag values, must be a comma separated string (e.g. --TagValues \"Skim_Base',Skim_Exetend\" ")
	parser.add_argument("--init", dest="init", help="Init or Update the dataset", action='store_true')
	parser.add_argument("--print", dest="print_ds", help="Print ", action='store_true')

	parser.add_argument("--submit-gc", action='store_true', default=False, dest="submitgc",help="Submit the jobs with grid control. Default: False (Default is to submit via crab). If submit-gc is set, jobs will not be submitted via crab.")
	parser.add_argument("--gc-check-completed", action='store_true', default=False, dest="checkcompleted",help="Check completed.")

	parser.add_argument("--show-task-id", action='store_true', default=False, dest="showID",help="List all current crab task IDs. Default: %(default)s")
	parser.add_argument("--crab-status", action='store_true', default=False, dest="status", help="Show crab status of non-finished crab tasks in work base and write to file 'crab_status.json' in workdir. Setting this will not submit any tasks, unless --auto-resubmit is set. Default: %(default)s")
	parser.add_argument("--remake", action='store_true', default=False, dest="remake", help="Remakes tasks where exception occured. (Run after --crab-status). Default: %(default)s")
	parser.add_argument("--auto-remake", action='store_true', default=False, dest="auto_remake", help="Auto remake crab tasks where exception is raised. (Remakes .requestcache file). Must be used with --crab-status. Default: %(default)s")
	parser.add_argument("--resubmit", default=None, dest="resubmit", help="Resubmit failed tasks. New Maximum Memory can be specified. Default: %(default)s")
	parser.add_argument("--auto-resubmit", action='store_true', default=False, dest="auto_resubmit", help="Auto resubmit failed tasks. Must be used with --crab-status or --remake. Default: %(default)s")
	parser.add_argument("--remake-all", action='store_true', default=False, dest="remake_all", help="Remakes all tasks. (Remakes .requestcache file). Default: %(default)s")

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
	SKM = SkimManagerBase(workbase=work_base,workdir=args.workdir)
	
	if args.init:
		SKM.add_new(args.inputfile, tag_key=args.tag, tag_values_str=args.tagvalues, query=args.query, nick_regex=args.nicks)
	if args.remake_all:
		SKM.remake_all()
	if args.showID:
		print SKM.show_crab_taskID()
	if args.remake:
		SKM.remake_task(args.inputfile,resubmit=args.auto_resubmit)
	if args.resubmit:
		SKM.resubmit_failed(memory=args.resubmit)
	if args.status:
		if not os.path.exists(os.path.join(work_base,args.workdir)):
			print "Workdir does not exist. Please specify exising workdir to get status of jobs."
			exit()
		SKM.write_crab_status(in_dataset_file=args.inputfile,remake=args.remake,resubmit=args.auto_resubmit)

	if not (args.status or args.remake or args.resubmit):
		SKM.create_gc_config()
		if args.submitgc:
			SKM.submit_gc(args.inputfile, tag_key=args.tag, tag_values_str=args.tagvalues, query=args.query, nick_regex=args.nicks)
			#SKM.status_gc(check_completed=args.checkcompleted)
		else:	
			SKM.submit_crab()
			SKM.status_crab()
			SKM.print_skim()
	SKM.save_dataset()
