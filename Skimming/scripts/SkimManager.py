#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import os, shutil
from  Kappa.Skimming.datasetsHelperTwopz import datasetsHelperTwopz
import argparse
import datetime
from time import gmtime, strftime
import subprocess
import json
import ast
import gzip
import shutil
import re
import hashlib
import sys
from multiprocessing import Process, Queue
import pprint
pp = pprint.PrettyPrinter(indent=4)

from httplib import HTTPException
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException

import Kappa.Skimming.tools as tools

class SkimManagerBase:


	def __init__(self, storage_for_output, workbase=".", workdir="TEST_SKIM", job_splitting="Automatic", units_per_job="", use_proxy_variable=False):
		self.storage_for_output = storage_for_output
		self.workdir = os.path.join(workbase, os.path.abspath(workdir))
		self.job_splitting = job_splitting
		self.units_per_job = int(units_per_job) if units_per_job else 1
		if not os.path.exists(self.workdir+"/gc_cfg"):
			os.makedirs(self.workdir+"/gc_cfg")
		self.skimdataset = datasetsHelperTwopz(os.path.join(self.workdir, "skim_dataset.json"))
		backup_dataset = self.skimdataset.json_file_name.replace(".json", "_backup.json")
		self.skimdataset.keep_input_json = False ## will be updated very often
		self.skimdataset.write_to_jsonfile(backup_dataset)
		if tools.is_above_cmssw_version([10]):
			self.configfile = 'kSkimming_run2legacy_cfg.py'
		elif tools.is_above_cmssw_version([9]):
			self.configfile = 'kSkimming_2017_cfg.py'
		else:
			self.configfile = 'kSkimming_run2_cfg.py'
		self.max_crab_jobs_per_nick = 8000 # 10k is the hard limit
		self.voms_proxy = None
		self.site_storage_access_dict = {
			"T2_DE_DESY" : {
				"dcap" : "dcap://dcache-cms-dcap.desy.de//pnfs/desy.de/cms/tier2/",
				"srm" : "srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/",
				"xrootd" : "root://dcache-cms-xrootd.desy.de:1094/",
			},
			"T2_DE_RWTH" : {
				"dcap" : "dcap://grid-dcap-extern.physik.rwth-aachen.de/pnfs/physik.rwth-aachen.de/cms/",
				"srm" : "srm://grid-srm.physik.rwth-aachen.de:8443/srm/managerv2\?SFN=/pnfs/physik.rwth-aachen.de/cms/",
				"xrootd" : "root://grid-cms-xrootd.physik.rwth-aachen.de:1094/",
			},
			"T2_PL_Swierk" : {
				#"dcap" : ""
				"srm" : "srm://se.cis.gov.pl:8446/srm/managerv2?SFN=/dpm/cis.gov.pl/home/cms/",
				"xrootd" : "root://se.cis.gov.pl:1094/",
			}
		}
		self.UsernameFromSiteDB = None
		try:
			self.voms_proxy=os.environ['X509_USER_PROXY']
		except:
			pass

	def crab_cmd(self, configuration, process_queue=None):
		try:
			output = crabCommand(configuration["cmd"], **configuration["args"])
			if process_queue:
				process_queue.put(output)
			return output
		except HTTPException as hte:
			print "Failed", configuration["cmd"], "of the task: %s" % (hte.headers)
		except ClientException as cle:
			print "Failed", configuration["cmd"], "of the task: %s" % (cle)
		except:
			print "Looks like crab has a bug - write to support"
			if configuration["cmd"] == "submit":
				print "The submission for this case is disabled. Bye"
				exit(1)

	def save_dataset(self, filename=None):
		self.skimdataset.write_to_jsonfile(filename)

	def add_new(self, nicks=None, force=False):
		if nicks is None:
			print "You must select something [see options --query, --nicks  or --tag (with --tagvalues)]"
		else:
			for new_nick in nicks:
				add_current_nick = False

				if (not new_nick in self.skimdataset.base_dict.keys()):
					add_current_nick = True
				elif (force and (self.skimdataset.base_dict[new_nick].get("SKIM_STATUS", "EXCEPTION") == "EXCEPTION")):
					add_current_nick = True
					self.skimdataset.base_dict.pop(new_nick)

				if add_current_nick:
					self.skimdataset[new_nick] = self.inputdataset[new_nick]
					self.skimdataset[new_nick]["SKIM_STATUS"] = "INIT"
					self.skimdataset[new_nick]["GCSKIM_STATUS"] = "INIT"
				else:
					print new_nick, "is already in this skimming campaign."

		self.save_dataset()

	def getUsernameFromSiteDB_cache(self):
		if self.UsernameFromSiteDB:
			return self.UsernameFromSiteDB
		else:
			from CRABClient.UserUtilities import getUsernameFromCRIC
			self.UsernameFromSiteDB = getUsernameFromCRIC()
			return self.UsernameFromSiteDB

	def get_global_tag(self, akt_nick):
		return self.skimdataset[akt_nick].get("globalTag", '80X_dataRun2_2016SeptRepro_v7' if self.skimdataset.isData(akt_nick) else '80X_mcRun2_asymptotic_2016_TrancheIV_v8')

	def limit_n_jobs(self, n_units, n_units_per_job, job_submission_limit=10000):
		if n_units/n_units_per_job > self.max_crab_jobs_per_nick:
			from math import ceil
			return int(ceil(float(n_units)/float(job_submission_limit)))
		else:
			return int(n_units_per_job)

	def files_per_job(self, akt_nick):
		files_per_job_default = 1
		if self.units_per_job and self.skimdataset[akt_nick].get("n_files", None):
			nfiles = int(self.skimdataset[akt_nick]["n_files"])
			return self.limit_n_jobs(nfiles, self.units_per_job)
		elif self.skimdataset[akt_nick].get("files_per_job", None):
			return int(self.skimdataset[akt_nick]["files_per_job"])
		elif self.skimdataset[akt_nick].get("n_files", None):
			nfiles = int(self.skimdataset[akt_nick]["n_files"])
			return self.limit_n_jobs(nfiles, files_per_job_default)
		return files_per_job_default

	def events_per_job(self, akt_nick):
		events_per_jobs_default = 30000
		if self.units_per_job and self.skimdataset[akt_nick].get("n_events_generated", None):
			nevents = int(self.skimdataset[akt_nick]["n_events_generated"])
			return self.limit_n_jobs(nevents, self.units_per_job)
		elif self.skimdataset[akt_nick].get("events_per_job", None):
			return int(self.skimdataset[akt_nick]["events_per_job"])
		elif self.skimdataset[akt_nick].get("n_events_generated", None):
			nevents = int(self.skimdataset[akt_nick]["n_events_generated"])
			return self.limit_n_jobs(nevents, events_per_jobs_default)
		return events_per_jobs_default

	def lumis_per_job(self, akt_nick):
		lumis_per_jobs_default = 100
		if self.units_per_job:
			nlumis = lumis_per_jobs_default
			if self.skimdataset[akt_nick].get("n_lumis", None):
				nlumis = int(self.skimdataset[akt_nick]["n_lumis"])
			else:
				url = 'https://cmsweb.cern.ch/dbs/prod/'+inputDBS+'/DBSReader'
				from Kappa.Skimming.getNumberGeneratedEventsFromDB import RestClient
				cert = os.environ['X509_USER_PROXY']
				if not cert.strip():
					print "X509_USER_PROXY not properly set. Get a voms proxy and set this environment variable to get N lumis from siteDB"
					return lumis_per_jobs_default
				rest_client = RestClient(cert=cert)
				import ast
				answer = ast.literal_eval(rest_client.get(url, api='filesummaries', params={'dataset': self.skimdataset[akt_nick]["dbs"]}))
				nlumis = answer[0]['num_lumi']
			return self.limit_n_jobs(nlumis, self.units_per_job)
		elif self.skimdataset[akt_nick].get("lumis_per_job", None):
			return int(self.skimdataset[akt_nick]["lumis_per_job"])
		elif self.skimdataset[akt_nick].get("n_lumis", None):
			nlumis = int(self.skimdataset[akt_nick]["n_lumis"])
			return self.limit_n_jobs(nlumis, lumis_per_jobs_default)
		return lumis_per_jobs_default


	def nick_list(self, in_dataset_file, tag_key = None, tag_values_str = None, query = None, nick_regex = None):
		self.inputdataset = datasetsHelperTwopz(in_dataset_file)
		tag_values = None
		if tag_key is None and query is None and nick_regex is None:
			return None
		if tag_values_str:
			tag_values = tag_values_str.strip('][').replace(' ', '').split(',')

		return(self.inputdataset.get_nick_list(tag_key=tag_key, tag_values=tag_values, query=query, nick_regex=nick_regex))


########## Functions related to management of crab tasks


#### Crab submission functions

	def submit_crab(self, filename=None, force=False):
		if len(self.skimdataset.get_nicks_with_query(query={"SKIM_STATUS" : "INIT"})) == 0:
			print "\nNo tasks will be submitted to the crab server. Set --init to add new tasks to submit.\n"
		else:
			print str(len(self.skimdataset.get_nicks_with_query(query={"SKIM_STATUS" : "INIT"})))+" tasks will be submitted to the crab server. Continue? [Y/n]"
			self.wait_for_user_confirmation()
		nerror=0
		for akt_nick in self.skimdataset.get_nicks_with_query(query={"SKIM_STATUS" : "INIT"}):
			if force and os.path.exists(os.path.join(self.workdir, "crab_"+akt_nick)):
				os.system("rm -rv "+os.path.join(self.workdir, "crab_"+akt_nick))

			config = self.crab_default_cfg() ## if there are parameters which should only be set for one dataset then its better to start from default again
			self.individualized_crab_cfg(akt_nick, config)
			if config.Data.inputDBS in ['list']:
				print akt_nick, " needs to be run with gc sinc it is not in site db"
				continue
			self.skimdataset[akt_nick]['outLFNDirBase'] = config.Data.outLFNDirBase
			self.skimdataset[akt_nick]['storageSite'] = config.Site.storageSite
			self.skimdataset[akt_nick]["crab_name"] = "crab_"+config.General.requestName

			submit_dict = {"config" : config, "proxy" : self.voms_proxy}
			q = Queue()
			p = Process(target=self.crab_cmd, args=({"cmd" : "submit", "args" : submit_dict}, q))
			p.start()
			submit_command_output = q.get()
			p.join()
			# submit_command_output = self.crab_cmd({"cmd" : "submit", "args" : submit_dict})
			if submit_command_output:
				self.skimdataset[akt_nick]["SKIM_STATUS"] = "SUBMITTED"
				self.skimdataset[akt_nick]["crab_task"] = submit_command_output["uniquerequestname"]
			else:
				self.skimdataset[akt_nick]["SKIM_STATUS"] = "EXCEPTION"

		self.save_dataset(filename)

	def crab_default_cfg(self):
		from CRABClient.UserUtilities import config
		config = config()
		config.General.workArea = self.workdir
		config.General.transferOutputs = True
		config.General.transferLogs = True
		config.User.voGroup = 'dcms' #comment out if not using German grid cert
		config.JobType.pluginName = 'Analysis'
		config.JobType.psetName = os.path.join(os.environ.get("CMSSW_BASE"), "src/Kappa/Skimming/higgsTauTau/", self.configfile)
		#config.JobType.inputFiles = ['Spring16_25nsV6_DATA.db', 'Spring16_25nsV6_MC.db']
		config.JobType.maxMemoryMB = 2500
		config.JobType.allowUndistributedCMSSW = True
		config.Site.blacklist = ["T3_FR_IPNL", "T3_US_UCR", "T2_BR_SPRACE", "T1_RU_*", "T2_RU_*", "T3_US_UMiss", "T2_US_Vanderbilt", "T2_EE_Estonia", "T2_TW_*"]
		# config.Data.splitting = 'Automatic'# 'FileBased'
		config.Data.splitting = self.job_splitting # 'FileBased'

		# unitsPerJob
		config.Data.outLFNDirBase = '/store/user/%s/higgs-kit/skimming/%s'%(self.getUsernameFromSiteDB_cache(), os.path.basename(self.workdir.rstrip("/")))
		config.Data.publication = False
		config.Data.allowNonValidInputDataset = False  # Set it true to run over incomplete datasets (for the ones still on Production status)
		config.Site.storageSite = self.storage_for_output
		return config

	def individualized_crab_cfg(self, akt_nick, config):
		config.General.requestName = hashlib.md5(akt_nick).hexdigest()
		config.Data.inputDBS = self.skimdataset[akt_nick].get("inputDBS", 'global')
		globalTag = self.get_global_tag(akt_nick)
		config.JobType.pyCfgParams = [str('globalTag=%s'%globalTag), 'kappaTag=KAPPA_2_1_0', str('nickname=%s'%(akt_nick)), str('outputfilename=kappa_%s.root'%(akt_nick)), 'testsuite=False']
		if config.Data.splitting == 'FileBased':
			config.Data.unitsPerJob = self.files_per_job(akt_nick)
		elif config.Data.splitting == 'EventAwareLumiBased':
			config.Data.unitsPerJob = self.events_per_job(akt_nick)
		elif config.Data.splitting == 'LumiBased':
			config.Data.unitsPerJob = self.lumis_per_job(akt_nick)
		config.Data.inputDataset = self.skimdataset[akt_nick]['dbs']
		config.Data.ignoreLocality = self.skimdataset[akt_nick].get("ignoreLocality", False) # Set to False to make it submit also if no whitelist is defined. Set to True if you how to configure it properly. ## i have very good experince with this option, but feel free to change it (maybe also add larger default black list for this, or start with a whitlist
		config.Site.blacklist.extend(self.skimdataset[akt_nick].get("blacklist", []))
		config.JobType.outputFiles = [str('kappa_%s.root'%(akt_nick))]

#### Functions for status check of crab tasks

	def status_crab(self):
		self.get_status_crab()
		self.update_status_crab()

	def get_status_crab(self):
		for akt_nick in self.skimdataset.nicks():
			if self.skimdataset[akt_nick]["SKIM_STATUS"] not in ["LISTED", "COMPLETED", "INIT"] and self.skimdataset[akt_nick]["GCSKIM_STATUS"] not in ["LISTED", "COMPLETED"]:
				crab_job_dir = os.path.join(self.workdir, self.skimdataset[akt_nick].get("crab_name", "crab_"+akt_nick[:100]))
				status_dict = {"proxy" : self.voms_proxy, "dir" : crab_job_dir}
				print "\nNickname:\t\t\t" + akt_nick
				self.skimdataset[akt_nick]['last_status'] = self.crab_cmd({"cmd" : "status", "args" : status_dict})
				if not self.skimdataset[akt_nick]['last_status']:
					self.skimdataset[akt_nick]["SKIM_STATUS"] = "EXCEPTION"
				elif self.skimdataset[akt_nick]['last_status']['dbStatus'] in ["KILLED"]:
					self.skimdataset[akt_nick]["SKIM_STATUS"] = "KILLED"

	def update_status_crab(self):
		# mostly copy paste from here: https://github.com/dmwm/CRABClient/blob/d41695646c20936a4d5671f2abd566ea91a7ac13/src/python/CRABClient/Commands/status.py#L513
		for akt_nick in self.skimdataset.nicks():
			statusCacheInfo = self.skimdataset[akt_nick].get('last_status', False)['jobs']
			# This record is no longer necessary and makes parsing more difficult.
			if 'DagStatus' in statusCacheInfo:
				del statusCacheInfo['DagStatus']

			jobsPerStatus = {}
			jobList = []
			result = {}
			for job, info in statusCacheInfo.items():
				jobStatus = info['State']
				jobsPerStatus.setdefault(jobStatus, 0)
				jobsPerStatus[jobStatus] += 1
				jobList.append([jobStatus, job])
			result['jobsPerStatus'] = jobsPerStatus
			result['jobList'] = jobList

			# Collect information about probe and tail jobs
			# Create dictionaries like {'finished' : 1, 'running' : 3}
			states = {}
			statesPJ = {}
			statesTJ = {}
			failedProcessing = 0
			for jobid, statusDict in statusCacheInfo.iteritems():
				jobStatus = statusDict['State'] if statusDict['State'] != 'cooloff' else 'toRetry'
				if jobid.startswith('0-'):
					statesPJ[jobStatus] = statesPJ.setdefault(jobStatus, 0) + 1
				elif '-' in jobid:
					statesTJ[jobStatus] = statesTJ.setdefault(jobStatus, 0) + 1
				else:
					states[jobStatus] = states.setdefault(jobStatus, 0) + 1
					if jobStatus == 'failed':
						failedProcessing += 1
			result['numProbes'] = sum(statesPJ.values())
			result['numUnpublishable'] = 0
			if result['numProbes'] > 0:
				result['numUnpublishable'] = failedProcessing

			def terminate(states, jobStatus, target='no output'):
				if jobStatus in states:
					states[target] = states.setdefault(target, 0) + states.pop(jobStatus)

			if sum(statesPJ.values()) > 0:
				if statesTJ:
					states.pop('failed', None) # remove failed from main jobs as they have been rescheduled as tail jobs
					for jobStatus in statesTJ:
						states[jobStatus] = states.setdefault(jobStatus, 0) + statesTJ[jobStatus]
				else:
					terminate(states, 'failed', target='rescheduled as tail jobs')

			if not self.skimdataset[akt_nick]['last_status']:
				self.skimdataset[akt_nick]["SKIM_STATUS"] = "EXCEPTION"
			elif self.skimdataset[akt_nick]['last_status']['dbStatus'] in ["KILLED"]:
				self.skimdataset[akt_nick]["SKIM_STATUS"] = "KILLED"
			else:
				self.skimdataset[akt_nick]["SKIM_STATUS"] = self.skimdataset[akt_nick]['last_status']['status']
			self.skimdataset[akt_nick]['n_jobs'] = sum(states[st] for st in states)
			all_jobs = self.skimdataset[akt_nick]['n_jobs']
			self.skimdataset[akt_nick]['crab_done'] = 0.0 if ((all_jobs == 0) or not states.get('finished', False))  else round(float(100.0*states['finished'])/float(all_jobs), 2)
			self.skimdataset[akt_nick]['crab_failed'] = 0.0 if ((all_jobs == 0) or not states.get('failed', False))  else round(float(100.0*states['failed'])/float(all_jobs), 2)
			self.skimdataset[akt_nick]['crab_running'] = 0.0 if ((all_jobs == 0) or not states.get('running', False))  else round(float(100.0*states['running'])/float(all_jobs), 2)
			self.skimdataset[akt_nick]['crab_other'] = round(max(100.0 - self.skimdataset[akt_nick]['crab_done'] - self.skimdataset[akt_nick]['crab_failed'] - self.skimdataset[akt_nick]['crab_running'], 0.0), 2)

#### Functions to allow resubmission and restart of crab tasks

	def kill_all(self):
		for dirpath, dirnames, fielnames in os.walk(self.workdir):
			for dirname in dirnames:
				if "crab" in dirname:
					crab_dir = os.path.join(dirpath, dirname)
					os.system('crab kill -d '+crab_dir)

	def purge(self, status_groups_to_purge):
		status_groups_to_purge = set(status_groups_to_purge.split(", "))
		tasks_to_purge = []
		if "ALL" in status_groups_to_purge:
			for dirpath, dirnames, fielnames in os.walk(self.workdir):
				for dirname in dirnames:
					if "crab" in dirname:
						crab_dir = os.path.join(dirpath, dirname)
						tasks_to_purge.append(crab_dir)
		elif status_groups_to_purge <= set(["COMPLETED", "LISTED", "KILLED", "FAILED"]):
			for status in status_groups_to_purge:
				for dataset_nick in self.skimdataset.nicks():
					if self.skimdataset[dataset_nick]["SKIM_STATUS"] == status or self.skimdataset[dataset_nick]["GCSKIM_STATUS"] == status:
						tasks_to_purge.append(self.skimdataset[dataset_nick].get("crab_name", "crab_"+dataset_nick[:100]))
		else:
			print "You specified an unsuitable status for purging. Please specify from this list: ALL, COMPLETED, LISTED, KILLED, FAILED."
		print len(tasks_to_purge), "crab task(s) to purge."
		for task in tasks_to_purge:
			print "Attempt to purge", task
			self.crab_cmd({"cmd" : "purge", "args" : {"dir":os.path.join(self.workdir, task), "cache":True}})
			print "--------------------------------------------"

	def remove_task(self, status_groups_to_remove):
		status_groups_to_remove = set(status_groups_to_remove.split(", "))
		if status_groups_to_remove <= set(["KILLED", "FAILED", "SUBMITFAILED"]):
			for status in status_groups_to_remove:
				for dataset_nick in self.skimdataset.nicks():
					if self.skimdataset[dataset_nick]["SKIM_STATUS"] == status or self.skimdataset[dataset_nick]["GCSKIM_STATUS"] == status:
						task = self.skimdataset[dataset_nick].get("crab_name", "crab_"+dataset_nick[:100])
						task_dir = os.path.join(self.workdir, task)
						print "Removing task " + dataset_nick + " and deleting directory " + task_dir
						try:
							shutil.rmtree(task_dir)
						except OSError as e:
							print ("Error: %s - %s." % (e.filename, e.strerror))
						try:
							self.skimdataset.base_dict.pop(dataset_nick)
						except KeyError:
							print ("Error: %s was not found in the skim summary dictionary." % dataset_nick)
		print "--------------------------------------------"

	def remake_task(self):
		nicks_to_remake = [nick for nick in self.skimdataset.nicks() if self.skimdataset[nick]["SKIM_STATUS"] in ["SUBMITFAILED", "EXCEPTION"]]
		all_subdirs = [os.path.join(self.workdir, self.skimdataset[akt_nick].get("crab_name", "crab_"+akt_nick[:100])) for akt_nick in nicks_to_remake]
		print len(all_subdirs), 'tasks that raised an exception will be remade. This will delete and recreate those folders in the workdir.'
		print 'Do you want to continue? [Y/n]'
		self.wait_for_user_confirmation()

		print '\033[94m'+'Getting crab tasks...'+'\033[0m'
		tasks = [] #self.get_crab_taskIDs()
		idir=1
		for subdir, nick in zip(all_subdirs, nicks_to_remake):
			print '\033[94m'+'('+str(idir)+'/'+str(len(all_subdirs))+')	REMAKING '+os.path.basename(subdir)+'\033[0m'
			idir+=1
			task_name = "blub" #self.skimdataset[akt_nick].get("crab_task", "NO_TASK_NAME_FOUND")
			if task_name in tasks:
				pass
			#		if os.path.exists(subdir):
			#			shutil.rmtree(subdir)
			#		os.system('crab remake --task='+task)
			#		os.system('crab resubmit -d '+subdir)
			#		nicks_to_remake.remove(nick)
			#		break
			else:
				print '\033[94m'+'No task name found for '+nick+'\033[0m'
				print '\033[94m'+nick+' will be RESUBMITTED by hand'+'\033[0m'
				if os.path.exists(subdir):
					shutil.rmtree(subdir)
				self.skimdataset.base_dict.pop(nick)
		if len(nicks_to_remake) > 0:
			self.add_new(nicks_to_remake)
			self.submit_crab()

	def resubmit_failed(self, argument_dict, ignore_killed):
		datasets_to_resubmit = []
		status_groups_to_ignore = ["COMPLETED", "LISTED"] + (["KILLED"] if ignore_killed else [])
		for dataset in self.skimdataset.nicks():
			if self.skimdataset[dataset]["SKIM_STATUS"] not in status_groups_to_ignore and self.skimdataset[dataset]["GCSKIM_STATUS"] not in status_groups_to_ignore:
				try:
					if "failed" in self.skimdataset[dataset]["last_status"]["jobsPerStatus"]:
						datasets_to_resubmit.append(self.skimdataset[dataset]["crab_name"])
				except:
					print "Failed to resubmit crab task", dataset, ". Possibly a problem with the skim_dataset.json. Try to recover the status of the task properly."
					pass
		print "Try to resubmit", len(datasets_to_resubmit), "tasks"
		for dataset in datasets_to_resubmit:
			print "Resubmission for", dataset
			argument_dict["dir"] = os.path.join(self.workdir, str(dataset))
			self.crab_cmd({"cmd" : "resubmit", "args" : argument_dict})
			print "--------------------------------------------"

#### Crab related helper functions

	def get_crab_taskIDs(self):
		output = subprocess.check_output("crab tasks", shell=True)
		tasks=[]
		for line in output.splitlines():
			if len(line) > 0:
				if line[0].isdigit():
					tasks.append(line)
		return tasks

########## Functions related to management of grid control tasks

#### Functions for resubmission with grid control for frequently failing crab tasks

	def prepare_resubmission_with_gc(self, nicks = None):

		datasets_to_resubmit = [dataset for dataset in self.skimdataset.nicks() if self.skimdataset[dataset]["SKIM_STATUS"] not in ["COMPLETED", "LISTED"] and self.skimdataset[dataset]["GCSKIM_STATUS"] not in ["COMPLETED", "LISTED"]]
		if nicks is not None:
			datasets_to_resubmit = [x for x in datasets_to_resubmit if x in nicks]
		self.write_while(datasets_to_submit=datasets_to_resubmit)

	def write_while(self, datasets_to_submit=None):
		if os.path.isfile(os.path.join(self.workdir, 'while.sh')):
			out_file = open(os.path.join(self.workdir, 'while.sh'), 'r')
			print '\n\033[92m'+'GC submission script exists with following configs:'+'\033[0m'
			for line in out_file.readlines():
				if line[:5]=='go.py':
					print line.strip('go.py '+os.path.join(self.workdir, 'gc_cfg'))
			out_file.close()
			print 'Overwrite? [Y/n]'
			if not self.wait_for_user_confirmation(true_false=True):
				print '\nScript will not be overwritten. To run with existing configs: '
				print os.path.join(self.workdir, 'while.sh')
				return

		out_file = open(os.path.join(self.workdir, 'while.sh'), 'w')
		out_file.write('#!/bin/bash\n')
		out_file.write('\n')
		out_file.write('touch .lock\n')
		out_file.write('\n')
		out_file.write('while [ -f ".lock" ]\n')
		out_file.write('do\n')
		for dataset in datasets_to_submit:
			out_file.write('go.py '+os.path.join(self.workdir, 'gc_cfg', dataset[:100]+'.conf -G\n'))
		out_file.write('echo "rm .lock"\n')
		out_file.write('sleep 2\n')
		out_file.write('done\n')
		out_file.close()

		os.system('chmod u+x '+os.path.join(self.workdir, 'while.sh'))

		print '\033[92m'+'To run GC submission loop with '+str(len(datasets_to_submit))+' datasets (will run until .lock file is removed), run:'+'\033[0m'
		print os.path.join(self.workdir, 'while.sh')
		print ''

	def create_gc_config(self, backend='freiburg'):
		shutil.copyfile(src=os.path.join(os.environ.get("CMSSW_BASE"), "src/Kappa/Skimming/higgsTauTau/", self.configfile), dst=os.path.join(self.workdir, 'gc_cfg', self.configfile))
		gc_config = self.gc_default_cfg(backend=backend)
		for akt_nick in self.skimdataset.get_nicks_with_query(query={"GCSKIM_STATUS" : "INIT"}):
			print "Create a new config for", akt_nick
			gc_config = self.gc_default_cfg(backend=backend)
			self.individualized_gc_cfg(akt_nick, gc_config)
			out_file_name = os.path.join(self.workdir, 'gc_cfg', akt_nick[:100]+'.conf')
			out_file = open(out_file_name, 'w')
			gc_workdir = os.path.join(self.workdir, akt_nick[:100])
			if os.path.exists(gc_workdir):
				print "GC workdir for", akt_nick, "exists. Do you whish to remove? To be removed:"
				print gc_workdir
				if self.wait_for_user_confirmation(true_false=True):
					shutil.rmtree(gc_workdir)
			for akt_key in ['global', 'jobs', 'CMSSW', 'storage']:
				out_file.write('['+akt_key+']\n')
				for akt_item in gc_config[akt_key]:
					out_file.write(akt_item+' = '+gc_config[akt_key][akt_item]+'\n')
			for akt_key in (set(gc_config.keys()) - set(['global', 'jobs', 'CMSSW', 'storage'])):
				out_file.write('['+akt_key+']\n')
				for akt_item in gc_config[akt_key]:
					out_file.write(akt_item+' = '+gc_config[akt_key][akt_item]+'\n')
			out_file.close()

	def gc_default_cfg(self, backend='freiburg'):
		cfg_dict = {}
		cfg_dict['global'] = {}
		cfg_dict['global']['task']  = 'CMSSW'
		if backend=='freiburg':
			cfg_dict['global']['backend']  = 'condor'
		elif backend=='naf':
			cfg_dict['global']['backend']  = 'local'
		else:
			print "Backend not supported. Please choose 'freiburg' or 'naf'."
			exit()
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
		cfg_dict['CMSSW']['area files'] = '-.* -config lib module */data *.xml *.sql *.cf[if] *.py *.h'
		cfg_dict['CMSSW']['config file'] = self.configfile

		cfg_dict['CMSSW']['dataset splitter'] = 'FileBoundarySplitter'
		cfg_dict['CMSSW']['files per job'] = '1'
		cfg_dict['CMSSW']['se runtime'] = 'True'
		cfg_dict['CMSSW'][';partition lfn modifier'] = '<srm:nrg>' ## comment out per default both can be changed during run, which can improve the succses rate
		cfg_dict['CMSSW']['depends'] = 'glite'
		cfg_dict['CMSSW']['parameter factory'] = "ModularParameterFactory"
		cfg_dict['CMSSW']['partition lfn modifier dict'] = "\n   <xrootd>    => root://cms-xrd-global.cern.ch//\n   <xrootd:eu> => root://xrootd-cms.infn.it//\n   <xrootd:us> => root://cmsxrootd.fnal.gov//\n   <xrootd:desy> => root://dcache-cms-xrootd.desy.de:1094/\n   <dcap:desy> => dcap://dcache-cms-dcap.desy.de//pnfs/desy.de/cms/tier2/\n   <local:desy> => file:///pnfs/desy.de/cms/tier2/\n   <srm:nrg> => srm://dgridsrm-fzk.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/dcms/disk-only/\n   <dcap:nrg> => dcap://dcnrgdcap.gridka.de:22125//pnfs/gridka.de/dcms/disk-only/\n   <xrootd:nrg> => root://cmsxrootd.gridka.de//pnfs/gridka.de/dcms/disk-only/\n   <dcap:gridka> => dcap://dccmsdcap.gridka.de:22125//pnfs/gridka.de/cms/disk-only/\n   <xrootd:gridka> => root://cmsxrootd.gridka.de//\n   <dcap:aachen> => dcap://grid-dcap-extern.physik.rwth-aachen.de/pnfs/physik.rwth-aachen.de/cms/\n   <xrootd:aachen> => root://grid-cms-xrootd.physik.rwth-aachen.de:1094/\n"

		cfg_dict['storage'] = {}
		cfg_dict['storage']['se output files'] = 'kappaTuple.root'
		cfg_dict['storage']['se output pattern'] = "/@NICK@/@FOLDER@/kappa_@NICK@_@GC_JOB_ID@.@XEXT@"

		if backend=="freiburg":
			cfg_dict['condor'] = {}
			cfg_dict['condor']['JDLData'] = 'Requirements=(TARGET.CLOUDSITE=="BWFORCLUSTER") +REMOTEJOB=True accounting_group=cms.higgs'
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

	def individualized_gc_cfg(self, akt_nick , gc_config):
		#se_path_base == srm://dgridsrm-fzk.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/dcms/disk-only/
		#se_path_base = 'srm://grid-srm.physik.rwth-aachen.de:8443/srm/managerv2\?SFN=/pnfs/physik.rwth-aachen.de/cms/'
		#se_path_base = 'srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/'
		storageSite = self.skimdataset[akt_nick].get("storageSite", self.storage_for_output)
		se_path_base = self.site_storage_access_dict[storageSite]["srm"]
		gc_config['storage']['se path'] = se_path_base+"store/user/%s/higgs-kit/skimming/%s/GC_SKIM/%s/"%(self.getUsernameFromSiteDB_cache(), os.path.basename(self.workdir.rstrip("/")), datetime.datetime.today().strftime("%y%m%d_%H%M%S"))
		#gc_config['storage']['se output pattern'] = "FULLEMBEDDING_CMSSW_8_0_21/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
		gc_config['CMSSW']['dataset'] = akt_nick+" : "+self.skimdataset[akt_nick]['dbs']
		gc_config['CMSSW']['files per job'] = str(self.files_per_job(akt_nick))
		gc_config['global']["workdir"] = os.path.join(self.workdir, akt_nick[:100])

		gc_config['dataset'] = {}
		gc_config['dataset']['dbs instance'] = self.skimdataset[akt_nick].get("inputDBS", 'global')
										   #URL=https://cmsdbsprod.cern.ch:8443/cms_dbs_prod_global_writer/servlet/DBSServlet
		gc_config['constants']['GLOBALTAG'] = self.get_global_tag(akt_nick)


#### Function for status check of grid-control tasks.

# Attention: the handling of grid-control tasks is intended to be done manually.
# Use the while.sh script to submit and to monitor your grid-control tasks.
# Adapt the grid-control configs listed in this script for example to resubmit jobs with modified parameters (memory, wall-time etc.)
# Here is only checked, whether the grid-control tasks is SUBMITTED or FINISHED.

	def status_gc(self):
		for dataset in self.skimdataset.nicks():
			if self.skimdataset[dataset]["GCSKIM_STATUS"] in ["SUBMITTED", "INIT"]:
				gc_workdir = os.path.join(self.workdir, dataset[:100])
				if os.path.exists(gc_workdir):
					if self.skimdataset[dataset]["GCSKIM_STATUS"] == "INIT":
						print "GC task status set to SUBMITTED for:"
						print dataset
						self.skimdataset[dataset]["GCSKIM_STATUS"] = "SUBMITTED"
					gc_output_dir = os.path.join(gc_workdir, "output")
					n_gc_jobs = int(gzip.open(os.path.join(gc_workdir, "params.map.gz"), 'r').read())
					done_jobs = 0
					for i in range(n_gc_jobs):
						job_info_path = os.path.join(gc_output_dir, "job_"+str(i), "job.info")
						if os.path.exists(job_info_path):
							job_info = open(job_info_path).read().split("\n")
							for info_line in job_info:
								if info_line == "EXITCODE=0":
									done_jobs += 1
									break
					if n_gc_jobs == done_jobs:
						print "GC task COMPLETED for", dataset
						self.skimdataset[dataset]["GCSKIM_STATUS"] = "COMPLETED"


########## Summary function, that prints out statistics on the running tasks

	def print_skim(self, summary=False):
		status_dict={}
		status_dict.setdefault('COMPLETED', [])
		status_dict.setdefault('EXCEPTION', [])
		status_dict.setdefault('FAILED', [])
		status_dict.setdefault('KILLED', [])
		status_dict.setdefault('SUBMITTED', [])

		for akt_nick in self.skimdataset.nicks():

			if self.skimdataset[akt_nick]["SKIM_STATUS"] in ["COMPLETED", "LISTED"] or self.skimdataset[akt_nick]["GCSKIM_STATUS"] in ["COMPLETED", "LISTED"]:
				status_dict['COMPLETED'].append(akt_nick)
			elif self.skimdataset[akt_nick]["SKIM_STATUS"] in ["SUBMITTED", "QUEUED", "UNKNOWN", "NEW"]:
				status_dict['SUBMITTED'].append(akt_nick)
			elif self.skimdataset[akt_nick]["SKIM_STATUS"] in ["FAILED", "RESUBMITFAILED"]:
				status_dict['FAILED'].append(akt_nick)
			elif self.skimdataset[akt_nick]["SKIM_STATUS"] in ["EXCEPTION", "SUBMITFAILED"]:
				status_dict['EXCEPTION'].append(akt_nick)
			elif self.skimdataset[akt_nick]["SKIM_STATUS"] in ["KILLED", "FAILED (KILLED)"]:
				status_dict['KILLED'].append(akt_nick)

		if summary:
			print "-----------------------------------------------"
			print "--------------- CRAB STATISTICS ---------------"
			print "-----------------------------------------------"
			print '\n'+'\033[92m'+'COMPLETED: '+str(len(status_dict['COMPLETED']))+' tasks'+'\033[0m'
			for nick in status_dict['COMPLETED']:
				print nick
			print '\n'+'\033[91m'+'FAILED: '+str(len(status_dict['FAILED']))+' tasks'+'\033[0m'
			for nick in status_dict['FAILED']:
				self.print_statistics(nick)
			print '\n'+'\033[91m'+'KILLED: '+str(len(status_dict['KILLED']))+' tasks'+'\033[0m'
			for nick in status_dict['KILLED']:
				self.print_statistics(nick)
			print '\n'+'\033[93m'+'EXCEPTION: '+str(len(status_dict['EXCEPTION']))+' tasks'+'\033[0m'
			for nick in status_dict['EXCEPTION']:
				self.print_statistics(nick)
			print '\n'+'SUBMITTED: '+str(len(status_dict['SUBMITTED']))+' tasks'
			for nick in status_dict['SUBMITTED']:
				self.print_statistics(nick)
			print '\n'

		status_json = open(os.path.join(self.workdir, 'skim_summary.json'), 'w')
		status_json.write(json.dumps(status_dict, sort_keys=True, indent=2))
		status_json.close()

	def print_statistics(self, nick):
		done_string = '\033[92m'+'Done: '+str(self.skimdataset[nick].get('crab_done', 0.0))+'%'+'\033[0m'
		failed_string = '\033[91m'+'Failed: '+str(self.skimdataset[nick].get('crab_failed', 0.0))+'%'+'\033[0m'
		running_string = '\033[93m'+'Running: '+str(self.skimdataset[nick].get('crab_running', 0.0))+'%'+'\033[0m'
		other_string = '\033[94m'+'Other: '+str(self.skimdataset[nick].get('crab_other', 0.0))+'%'+'\033[0m'
		print nick + "\t" + (4*" ").join([done_string, failed_string, running_string, other_string])

########## Functions to create or reset file lists for COMPLETED grid-control or crab tasks

	def create_filelist(self, date, create_recent_symlinks, force=False):
		filelist_folder_name = os.path.expandvars("$CMSSW_BASE/src/HiggsAnalysis/KITHiggsToTauTau/data/Samples")
		if not os.path.exists(filelist_folder_name):
			os.makedirs(filelist_folder_name)
		for dataset in self.skimdataset.nicks():
			storage_site = self.skimdataset[dataset].get("storageSite", self.storage_for_output)
			if not self.skimdataset[dataset].get("storageSite"):
				self.skimdataset[dataset]["storageSite"] = self.storage_for_output
			# File list for GC first
			if self.skimdataset[dataset]["GCSKIM_STATUS"] == "COMPLETED":
				gc_output_dir = os.path.join(self.workdir, dataset[:100], "output")
				n_jobs_info = os.path.join(self.workdir, dataset[:100], "params.map.gz")
				if os.path.exists(n_jobs_info):
					print "Getting GC file list for", dataset
					filelist_path = os.path.join(filelist_folder_name, "XROOTD_sample_"+dataset+"_"+date+".txt")
					filelist = open(filelist_path, 'w')
					n_gc_jobs = int(gzip.open(n_jobs_info, 'r').read())
					done_jobs = 0
					for i in range(n_gc_jobs):
						job_info_path = os.path.join(gc_output_dir, "job_"+str(i), "job.info")
						if os.path.exists(job_info_path):
							job_info = open(job_info_path).read().split("\n")
							for info_line in job_info:
								if info_line.startswith("FILE="):
									file_path_parts = info_line.strip('"').split("  ")[-2:]
									filelist.write(self.site_storage_access_dict[storage_site]["xrootd"]+re.sub(r'.*(store)', r'/store', file_path_parts[1]+file_path_parts[0]+"\n"))
					filelist.close()
					self.skimdataset[dataset]["GCSKIM_STATUS"] = "LISTED"
					if create_recent_symlinks:
						filelist_path_symlink = filelist_path.replace(date+".txt", "recent.txt")
						os.system("ln -fsv %s %s" % (os.path.relpath(filelist_path, os.path.dirname(filelist_path_symlink)), filelist_path_symlink))
					print "List creation successfull!"
					print "---------------------------------------------------------"
			# If GC task not completed, create a crab filelist
			elif (force and (self.skimdataset[dataset]["SKIM_STATUS"] != "KILLED" if args.ignore_killed else True)) or (self.skimdataset[dataset]["SKIM_STATUS"] == "COMPLETED" and self.skimdataset[dataset]["GCSKIM_STATUS"] != "LISTED"):
				print "Getting CRAB file list for", dataset
				filelist_path = os.path.join(filelist_folder_name, "XROOTD_sample_"+dataset+"_"+date+".txt")
				filelist = open(filelist_path, 'w')
				dataset_filelist = ""
				
				number_jobs = self.skimdataset[dataset].get("n_jobs", int(self.skimdataset[dataset].get("n_files", 0)) if force else 0)

				crab_number_folders = [str(i / 1000).zfill(4) for i in range(number_jobs+1)[::1000]]
				crab_numer_folder_regex = re.compile('|'.join(crab_number_folders))

				jobiddict ={}
				number_listed_jobs = 0
				for jobstatuslist in self.skimdataset[dataset].get("last_status").get("jobList"):
					if jobstatuslist[0] == 'finished':
						jobid = jobstatuslist[1]
						if re.search("-", jobid) == None:
							try:
								jobiddict["x"].append(jobid)
							except KeyError:
								jobiddict["x"] = [jobid]
						else:
							id_type_key = re.findall(r'\d+-', jobid)[0]+ "x"
							try:
								jobiddict[id_type_key].append(jobid)
							except KeyError:
								jobiddict[id_type_key]=[jobid]

				try:
					for id_type in jobiddict.keys():
						if id_type != "0-x":
							crab_dataset_filelist = subprocess.check_output("crab getoutput --xrootd --jobids {JOBID} --dir {DATASET_TASK} --proxy $X509_USER_PROXY".format(DATASET_TASK=os.path.join(self.workdir, self.skimdataset[dataset].get("crab_name", "crab_"+dataset[:100])), JOBID=str(jobiddict[id_type][0])), shell=True).strip('\n').split('\n')
							sample_file_path = crab_dataset_filelist[0]
							pattern = "_" + id_type[0:-1]+r'\d+.root'
							job_id_match = re.findall(pattern, sample_file_path)[0]
							sample_file_path =  sample_file_path.replace(job_id_match,"_"+ "{JOBID}.root")
							crab_number_folder_match = re.findall('|'.join(crab_number_folders), sample_file_path)[0]
							sample_file_path =  sample_file_path.replace(crab_number_folder_match, "{CRAB_NUMBER_FOLDER}")

							jobid = 0
							for jobindex in range(1, len(jobiddict[id_type])+1):
								if re.search("-", jobiddict[id_type][jobindex-1]) == None:
									jobid = jobiddict[id_type][jobindex-1]
								else:
									jobid = jobiddict[id_type][jobindex-1].split("-")[-1]

								dataset_filelist += sample_file_path.format(CRAB_NUMBER_FOLDER=crab_number_folders[int(jobid)/1000], JOBID=jobiddict[id_type][jobindex-1])+'\n'
								number_listed_jobs += 1

					print "Found", number_jobs, "files run on skimming."
					print "Found", number_listed_jobs, "output files finishing successfully and stored."
					dataset_filelist = dataset_filelist.strip('\n')
					filelist.write(dataset_filelist.replace("root://cms-xrd-global.cern.ch/", self.site_storage_access_dict[storage_site]["xrootd"]))
					filelist.close()
					print "Saved filelist in \"%s\"." % filelist_path
				except:
					print "Getting output from crab exited with error. Try again later."

				if create_recent_symlinks:
					filelist_path_symlink = filelist_path.replace(date+".txt", "recent.txt")
					os.system("ln -fsv %s %s" % (os.path.relpath(filelist_path, os.path.dirname(filelist_path_symlink)), filelist_path_symlink))

				filelist_check = open(filelist_path, 'r')
				if "0-x" in jobiddict.keys():
					if len(filelist_check.readlines()) == (number_jobs-len(jobiddict["0-x"])):
						self.skimdataset[dataset]["SKIM_STATUS"] = "LISTED"
						print "List creation successfull!"
				else:
					if len(filelist_check.readlines()) == (number_jobs):
						self.skimdataset[dataset]["SKIM_STATUS"] = "LISTED"
						print "List creation successfull!"
				filelist_check.close()
				print "---------------------------------------------------------"

		print "End of list creation."

	def reset_filelist(self):
		for dataset in self.skimdataset.nicks():
			if self.skimdataset[dataset]["SKIM_STATUS"] == "LISTED":
				self.skimdataset[dataset]["SKIM_STATUS"] = "COMPLETED"
			elif self.skimdataset[dataset]["GCSKIM_STATUS"] == "LISTED":
				self.skimdataset[dataset]["GCSKIM_STATUS"] = "COMPLETED"

########## Further general helper functions

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
				return("/net/scratch_cms3b/%s/kappa_skim_workdir/" % os.environ["USER"])
			else:
				print "Default workbase could not be found. Please specify working dir as absolute path."
				sys.exit()

	@classmethod
	def get_latest_subdir(self, work_base):
		all_subdirs = [os.path.join(work_base, d) for d in os.listdir(work_base) if os.path.isdir(work_base+d)]
		if len(all_subdirs) == 0:
			return None
		else:
			return max(all_subdirs, key=os.path.getmtime)

	@classmethod
	def wait_for_user_confirmation(self, true_false=False):
		choice = raw_input().lower()
		if choice in set(['yes', 'y', 'ye', '']):
			if true_false:
				return True
			pass
		elif choice in set(['no', 'n']):
			if true_false:
				return False
			exit()
		else:
			print "Please respond with yes or no"
			exit()

if __name__ == "__main__":

	work_base = SkimManagerBase.get_workbase()
	if not os.path.exists(work_base):
		os.makedirs(work_base)

	def_input = os.path.join(os.environ.get("CMSSW_BASE"), "src/Kappa/Skimming/data/datasets.json")

	parser = argparse.ArgumentParser(description="Tools for modify the dataset data base (aka datasets.json)")

	parser.add_argument("-i", "--input", dest="inputfile", default=def_input, help="input data base (Default: %s)"%def_input)
	parser.add_argument("-w", "--workdir", dest="workdir", default=os.path.join(work_base, strftime("%Y-%m-%d-%H-%M-%S", gmtime()))+"_kappa-skim", help="Set work directory  (Default: %(default)s)")
	parser.add_argument("-d", "--date", nargs="?", default=None, const=datetime.date.today().strftime("%Y-%m-%d"), help="Date (Default: %(default)s)")
	parser.add_argument("--query", dest="query", help="Query which each dataset has to fulfill. Works with regex e.g: --query '{\"campaign\" : \"RunIISpring16MiniAOD.*reHLT\"}' \n((!!! For some reasons the most outer question marks must be the \'))")
	parser.add_argument("--nicks", dest="nicks", help="Query which each dataset has to fulfill. Works with regex e.g: --nicks \".*_Run2016(B|C|D).*\"")
	parser.add_argument("--tag", dest="tag", help="Ask for a specific tag of a dataset. Optional arguments are --TagValues")
	parser.add_argument("--tagvalues", dest="tagvalues", help="The tag values, must be a comma separated string (e.g. --TagValues \"Skim_Base', Skim_Exetend\" ")
	parser.add_argument("--storage-for-output", dest="storage_for_output", default="T2_DE_RWTH", help="Specifies the storage element you want to write your outputs to. Default: %(default)s")

	parser.add_argument("--init", dest="init", help="Init or Update the dataset", action='store_true')

	parser.add_argument("--job-splitting", dest="job_splitting", default="Automatic", choices=["Automatic", "FileBased", "EventAwareLumiBased", "LumiBased"], help="Specifies the job splitting algorithm. Possible supported options: Automatic, FileBased, EventAwareLumiBased, LumiBased. Default: %(default)s")
	parser.add_argument("--units-per-job", dest="units_per_job", default="", help="Specifies the number of units per job. Default: not used for Automatic, 1 file for FileBased, 30k events for EventAwareLumiBased, 100 lumi sections for LumiBased. If total amount of jobs exceeds 10k, numbers are scaled accordingly.")

	parser.add_argument("--status-gc", action='store_true', default=False, dest="statusgc", help="")
	parser.add_argument("--summary", action='store_true', default=False, dest="summary", help="Prints summary and writes skim_summary.json in workdir with quick status overview of crab tasks.")

	parser.add_argument("--resubmit-with-options", default=None, dest="resubmit", help="Resubmit failed tasks. Options for crab resubmit can be specified via a python dict, e.g: --resubmit '{\"maxmemory\" : \"3000\", \"maxruntime\" : \"1440\"}'. To avoid options use '{}' Default: %(default)s")
	parser.add_argument("--ignore-killed", action='store_true', default=False, help="Ignore 'KILLED' tasks when resubmiting tasks. Default: %(default)s")
	parser.add_argument("--resubmit-with-gc", action='store_true', default=False, dest="resubmit_with_gc", help="Resubmits non-completed tasks with Grid Control.")
	parser.add_argument("--remake", action='store_true', default=False, dest="remake", help="Remakes tasks for which an exception occured. (Run after --crab-status). Default: %(default)s")
	parser.add_argument("--kill-all", action='store_true', default=False, dest="kill_all", help="kills all tasks. Default: %(default)s")
	parser.add_argument("--purge", default=None, dest="purge", help="Purges tasks specified groups of tasks defined by their status. Possible groups: ALL, COMPLETED, LISTED, FAILED, KILLED. You may specify multiple groups separated by a comma. Default: %(default)s")
	parser.add_argument("--remove", default=None, dest="remove", help="Removes tasks specified groups of tasks defined by their status. Always kill and purge before using this option. Possible groups: FAILED, KILLED. You may specify multiple groups separated by a comma. Default: %(default)s")

	parser.add_argument("--create-filelist", action='store_true', default=False, dest = "create_filelist", help="")
	parser.add_argument("--reset-filelist", action='store_true', default=False, dest = "reset_filelist", help="")
	parser.add_argument("-r", "--create-recent-symlinks", default=False, action="store_true", help="Create symlinks to filelists as recent ones. [Default: %(default)s]")

	parser.add_argument("-f", "--force", action='store_true', default=False, dest="force", help="Force current action (e.g. creation of filelists).")

	parser.add_argument("-b", "--backend", default='freiburg', dest="backend", help="Changes backend for the creation of Grid Control configs. Supported: freiburg, naf. Default: %(default)s")

	args = parser.parse_args()

	if args.workdir == parser.get_default("workdir"):
		latest_subdir = SkimManagerBase.get_latest_subdir(work_base=work_base)
		if latest_subdir is None:
			latest_subdir = args.workdir
		print '\nNo workdir specified. Do you want to continue the existing skim in '+latest_subdir+' ? [Y/n] (Selecting no will create new workdir)'
		if SkimManagerBase.wait_for_user_confirmation(true_false=True):
			args.workdir=latest_subdir
		else:
			print 'New workdir will be created: '+args.workdir

	if not os.path.exists(args.inputfile):
		print 'No input file found'
		exit()

	if args.date and args.init:
		args.workdir+="_"+args.date

	SKM = SkimManagerBase(storage_for_output=args.storage_for_output, workbase=work_base, workdir=args.workdir, job_splitting=args.job_splitting, units_per_job=args.units_per_job)
	nicks = SKM.nick_list(args.inputfile, tag_key=args.tag, tag_values_str=args.tagvalues, query=args.query, nick_regex=args.nicks)

	if args.init:
		SKM.add_new(nicks, args.force)
		SKM.create_gc_config(backend=args.backend)

	if args.kill_all:
		SKM.kill_all()
		exit()

	if args.purge:
		SKM.purge(args.purge)
		exit()

	if args.remove:
		SKM.remove_task(args.remove)
		SKM.save_dataset()
		exit()

	if args.remake:
		SKM.remake_task()
		exit()

	if args.resubmit:
		SKM.resubmit_failed(argument_dict=ast.literal_eval(args.resubmit), ignore_killed=args.ignore_killed)
		exit()

	if args.create_filelist:
		if not args.date:
			print "Please specify --date!"
			exit()
		SKM.create_filelist(args.date, args.create_recent_symlinks, args.force)
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
		SKM.submit_crab(force=args.force)
		SKM.status_crab()
		SKM.print_skim(summary=args.summary)

	SKM.save_dataset()
