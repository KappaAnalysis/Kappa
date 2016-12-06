#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from  Kappa.Skimming.datasethelpertwopz import datasethelpertwopz
import argparse

work_dir_default = "/nfs/dust/cms/user/swayand/kappa_skim_workdir/"


def crab_cmd(cmd, config=None, proxy=None, crab_dir=None):
  from httplib import HTTPException
  from CRABAPI.RawCommand import crabCommand
  from CRABClient.ClientExceptions import ClientException
  try:
    if not config:
      return crabCommand(cmd, proxy=proxy, dir=crab_dir)
    else:
      return crabCommand(cmd, config = config, proxy=proxy)
  except HTTPException as hte:
    print "Failed submitting task: %s" % (hte.headers)
  except ClientException as cle:
    print "Failed submitting task: %s" % (cle)


class SkimMangerBase:
  def __init__(self, baseworkdir=work_dir_default, workdir="TEST_SKIM", use_proxy_variable=True):
    self.workdir = os.path.join(baseworkdir,workdir) 
    if not os.path.exists(self.workdir+"/gc_cfg"): 
      os.makedirs(self.workdir+"/gc_cfg")
    self.skimdataset = datasethelpertwopz(os.path.join(self.workdir,"skim_datataset.json"))
    self.skimdataset.keep_input_json = False ## will be updated very often
    
    self.max_crab_jobs_per_nick = 8000 # 10k is the hard limit
    self.voms_proxy = None
    self.UsernameFromSiteDB = None
    if use_proxy_variable:
      self.voms_proxy=os.environ['X509_USER_PROXY']
  def  __del__(self): 
    self.save_dataset()
  def save_dataset(self):
    self.skimdataset.write_to_jsonfile(None)  
    
  def add_new(self, in_dataset_file,  tag_key = None, tag_values_str = None, query = None, nick_regex = None):
    self.inputdataset = datasethelpertwopz(in_dataset_file)
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
    self.save_dataset() 
  def getUsernameFromSiteDB_cache(self):
    if self.UsernameFromSiteDB:
      return self.UsernameFromSiteDB
    else:
      from CRABClient.UserUtilities import getUsernameFromSiteDB
      self.UsernameFromSiteDB = getUsernameFromSiteDB()
      return self.UsernameFromSiteDB
  def get_globa_tag(self, akt_nick):
    return self.skimdataset[akt_nick].get("globalTag", '80X_dataRun2_2016SeptRepro_v4' if self.skimdataset.isData(akt_nick) else '80X_mcRun2_asymptotic_2016_miniAODv2_v1')
    
  def gc_defautl_cfg(self):
    cfg_dict = {}
    cfg_dict['global'] = {}
    cfg_dict['global']['task']  = 'CMSSW'   
    #cfg_dict['global']['backend']  = 'condor'
    cfg_dict['global']['backend']  = 'local'
    #cfg_dict['global']['backend']  = 'cream'
    
    
    cfg_dict['global']["workdir create"] = 'True '

    cfg_dict['jobs'] = {}
    cfg_dict['jobs']['in flight'] = '2000'
    cfg_dict['jobs']['wall time'] = '02:00:00'
    cfg_dict['jobs']['memory'] = '3000'
    cfg_dict['jobs']['jobs'] = '5'
    
    
    cfg_dict['CMSSW'] = {}
    cfg_dict['CMSSW']['project area'] = '$CMSSW_BASE/'
    cfg_dict['CMSSW']['config file'] = 'kSkimming_run2_new_cfg.py'
    
    cfg_dict['CMSSW']['dataset splitter'] = 'FileBoundarySplitter'
    cfg_dict['CMSSW']['files per job'] = '1'
    cfg_dict['CMSSW']['se runtime'] = 'True'
    cfg_dict['CMSSW'][';;partition lfn modifier'] = '<srm:nrg>' ## comment out per default both can be changed during run, which can improve the succses rate 
    cfg_dict['CMSSW']['depends'] = 'glite'
    cfg_dict['CMSSW']['parameter factory'] = "ModularParameterFactory"
    cfg_dict['CMSSW']['partition lfn modifier dict'] = "\n   <xrootd>    => root://cms-xrd-global.cern.ch//\n   <xrootd:eu> => root://xrootd-cms.infn.it//\n   <xrootd:us> => root://cmsxrootd.fnal.gov//\n   <xrootd:desy> => root://dcache-cms-xrootd.desy.de:1094/\n   <srm:nrg> => srm://dgridsrm-fzk.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/dcms/disk-only/\n   <dcap:nrg> => dcap://dcnrgdcap.gridka.de:22125//pnfs/gridka.de/dcms/disk-only/\n   <xrootd:nrg> => root://cmsxrootd.gridka.de//pnfs/gridka.de/dcms/disk-only/\n   <dcap:gridka> => dcap://dccmsdcap.gridka.de:22125//pnfs/gridka.de/cms/disk-only/\n   <xrootd:gridka> => root://cmsxrootd.gridka.de//\n   <dcap:aachen> => dcap://grid-dcap-extern.physik.rwth-aachen.de/pnfs/physik.rwth-aachen.de/cms/\n"
    
    
    
    cfg_dict['storage'] = {}
    cfg_dict['storage']['se output files'] = 'kappaTuple.root'
    cfg_dict['storage']['se output pattern'] = "FULLEMBEDDING_CMSSW_8_0_21/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
  
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

    cfg_dict['backend'] = {}
    cfg_dict['backend']['ce'] = "cream-ge-2-kit.gridka.de:8443/cream-sge-sl6"
    
    cfg_dict['constants'] = {}
    cfg_dict['constants']['GC_GLITE_LOCATION'] = '/cvmfs/grid.cern.ch/emi3ui-latest/etc/profile.d/setup-ui-example.sh'
    cfg_dict['constants']['X509_USER_PROXY'] = '$X509_USER_PROXY'
    

    cfg_dict['parameters'] = {}
    cfg_dict['parameters']['parameters'] = 'transform("FOLDER", "GC_JOB_ID % 100 + 1")'
    
    return cfg_dict
    
  def submit_gc(self):
    from multiprocessing import Process
    for akt_nick in self.skimdataset.get_nicks_with_query(query={"GCSKIM_STATUS" : "INIT"}):
      gc_config = self.gc_defautl_cfg()
      self.individualized_gc_cfg(akt_nick, gc_config)
      out_file_name = os.path.join(self.workdir,'gc_cfg',akt_nick[:100]+'.conf')
      out_file = open(out_file_name,'w')
      for akt_key in ['global','jobs','CMSSW','dataset','storage']:
	out_file.write('['+akt_key+']\n')
	for akt_item in gc_config[akt_key]:
	  out_file.write(akt_item+' = '+gc_config[akt_key][akt_item]+'\n')
      for akt_key in (set(gc_config.keys()) - set(['global','jobs','CMSSW','dataset','storage'])):
	out_file.write('['+akt_key+']\n')
	for akt_item in gc_config[akt_key]:
	  out_file.write(akt_item+' = '+gc_config[akt_key][akt_item]+'\n')
      
	
      out_file.close()
      
    
  def individualized_gc_cfg(self, akt_nick ,gc_config):
    
      #se_path_base == srm://dgridsrm-fzk.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/dcms/disk-only/
      #se_path_base =srm://grid-srm.physik.rwth-aachen.de:8443/srm/managerv2\?SFN=/pnfs/physik.rwth-aachen.de/cms/store/
      se_path_base = "srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/"
      gc_config['storage']['se path'] = se_path_base+"/store/user/%s/higgs-kit/skimming/%s/gc"%(self.getUsernameFromSiteDB_cache(), os.path.basename(self.workdir))
      gc_config['storage']['se output pattern'] = "FULLEMBEDDING_CMSSW_8_0_21/@NICK@/@FOLDER@/@XBASE@_@GC_JOB_ID@.@XEXT@"
      gc_config['CMSSW']['dataset'] = akt_nick+" : "+self.skimdataset[akt_nick]['dbs']
      gc_config['CMSSW']['files per job'] = str(self.files_per_job(akt_nick))
      gc_config['global']["workdir"] = os.path.join(self.workdir,akt_nick[:100])
      
      gc_config['dataset'] = {}
      gc_config['dataset']['dbs instance'] = "http://cmsdbsprod.cern.ch/cms_dbs_prod_%s/servlet/DBSServlet"%(self.skimdataset[akt_nick].get("inputDBS",'global'))
      
      gc_config['constants']['GLOBALTAG'] = self.get_globa_tag(akt_nick)

      
    
  
  def crab_default_cfg(self):
    from CRABClient.UserUtilities import config
    config = config()
    config.General.workArea = self.workdir
    config.General.transferOutputs = True
    config.General.transferLogs = True
    config.User.voGroup = 'dcms'
    config.JobType.pluginName = 'Analysis'
    config.JobType.psetName = 'kSkimming_run2_cfg.py'
    #config.JobType.inputFiles = ['Spring16_25nsV6_DATA.db', 'Spring16_25nsV6_MC.db']
    config.JobType.allowUndistributedCMSSW = True
    config.Site.blacklist = ["T2_BR_SPRACE"]
    config.Data.splitting = 'FileBased'
    config.Data.outLFNDirBase = '/store/user/%s/higgs-kit/skimming/%s'%(self.getUsernameFromSiteDB_cache(), os.path.basename(self.workdir))
    config.Data.publication = False
    config.Site.storageSite = "T2_DE_DESY"
    return config
  
  def submit_crab(self):
    from multiprocessing import Process
    for akt_nick in self.skimdataset.get_nicks_with_query(query={"SKIM_STATUS" : "INIT"}):
      config = self.crab_default_cfg () ## if there are parameters which should only be set for one dataset then its better to start from default again
      self.individualized_crab_cfg(akt_nick, config)
      if config.Data.inputDBS in ['list']:
	print akt_nick," needs to be run with gc sinc it is not in site db"
	continue 
      self.skimdataset[akt_nick]['outLFNDirBase'] = config.Data.outLFNDirBase
      self.skimdataset[akt_nick]['storageSite'] = config.Site.storageSite 
      self.skimdataset[akt_nick]["SKIM_STATUS"] = "SUBMITTED"
      self.skimdataset[akt_nick]["crab_name"] = "crab_"+config.General.requestName
      p = Process(target=crab_cmd, args=('submit',config,self.voms_proxy))
      p.start()
      p.join()  ###make no sens for multiprocessing here, since python will wait until p is finished. Solution would be to save all p's and then join them in in a seperate loop. 
    self.save_dataset()
  def individualized_crab_cfg(akt_nick, config):
    config.General.requestName = akt_nick[:100]
    config.Data.inputDBS = self.skimdataset[akt_nick].get("inputDBS",'global')
    globalTag = self.get_globa_tag(akt_nick)
    config.JobType.pyCfgParams = ['globalTag=%s'%globalTag,'kappaTag=KAPPA_2_1_0',str('nickname=%s'%(akt_nick)),str('outputfilename=kappa_%s.root'%(akt_nick)),'testsuite=False']
    config.Data.unitsPerJob = self.files_per_job(akt_nick) 
    config.Data.inputDataset = self.skimdataset[akt_nick]['dbs']
    config.Data.ignoreLocality = self.skimdataset[akt_nick].get("ignoreLocality", True) ## i have very good experince with this option, but feel free to change it (maybe also add larger default black list for this, or start with a whitlist 
    config.Site.blacklist.extend(self.skimdataset[akt_nick].get("blacklist", []))
    config.JobType.outputFiles = [str('kappa_%s.root'%(akt_nick))]
  
  
  def files_per_job(self, akt_nick):
    return 200
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


       

if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog='./DatasetManager.py', usage='%(prog)s [options]', description="Tools for modify the dataset data base (aka datasets.json)") 
  
  def_input = os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/datasets_conv.json")
  parser.add_argument("--input", dest="input", help="input data base (default=%s)"%def_input, default=def_input)
  
  
  parser.add_argument("--query", dest="query", help="Query which each dataset has to fulfill. Works with regex e.g: --query '{\"campaign\" : \"RunIISpring16MiniAOD.*reHLT\"}' \n((!!! For some reasons the most outer question marks must be the \'))")
  parser.add_argument("--nicks", dest="nicks", help="Query which each dataset has to fulfill. Works with regex e.g: --nicks \".*_Run2016(B|C|D).*\"")
  parser.add_argument("--tag", dest="tag", help="Ask for a specific tag of a dataset. Optional arguments are --TagValues")
  parser.add_argument("--tagvalues", dest="tagvalues", help="The tag values, must be a comma separated string (e.g. --TagValues \"Skim_Base',Skim_Exetend\" ")
  parser.add_argument("--init", dest="init", help="Init or Update the dataset", action='store_true')
  
  parser.add_argument("--print", dest="print_ds", help="Print ", action='store_true')
  args = parser.parse_args()
  
  SKM = SkimMangerBase()
  
  if args.init:
    SKM.add_new(args.input, tag_key=args.tag, tag_values_str=args.tagvalues, query=args.query, nick_regex=args.nicks)
    
  SKM.submit_gc() 
 # SKM.submit_crab()
  SKM.status_crab()
  SKM.print_skim()
  

		   


