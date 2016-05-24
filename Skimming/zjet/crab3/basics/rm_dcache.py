#!/usr/bin/env python

import sys,ConfigParser,os,string,commands,time,shutil,subprocess
from optparse import OptionParser, SUPPRESS_HELP
import subprocess
from signal import alarm, signal, SIGALRM, SIGKILL
import multiprocessing

parser=OptionParser()
parser.add_option("-f", "--folder", help="please give a folder on naf dcace which you want to delete recursively (rm -rf) e.g. -f /pnfs/desy.de/cms/tier2/store/user/swayand/MuMu_embedding/") ##Rootfilename
parser.add_option("-v", "--verbose", action="store_true", help="show all excueded bash commands", default=False) ##Rootfilename 
(opt, args) = parser.parse_args()



def run_bash(cmd,trys=5,time=20, inc=10, max_time=120): ## like you would execute it direct in the shell. The options are usefull if you have comannds which can hanging up (e.g. xrd or srm). Here it trys up to 5 times to run the the bash command cmd. It gives eaach try  max(20 + (number of try - 1)*10, 120) seconds time to return a result. Keep in mind if the cmd returns an error the try was successful and will return the bash output 
    akt_count=0
    loooop=1
    out=""
    if time <=0: ## it time is set to zero or below just run the it foever 
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.stdout.read().strip()
        return out  #This is the stdout from the shell command 
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    while loooop and (akt_count<trys):
        akt_count+=1
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if time>max_time:
            time=max_time
        signal(SIGALRM, alarm_handler)
        alarm(time)
        time+=inc
        try:
            out=proc.stdout.read().strip()
            alarm(0)
            loooop=0
        except Alarm:
            proc.kill()
    return out


def run_bash_default(cmd): ## simplyfication of the run_bash method. Helpfull for the multicore mode 
    if opt.verbose:
        print cmd
    return run_bash(cmd,5,20,10)

class rm_grid_folder():
  def __init__(self, folder):
    self.folder = folder.rstrip('/')
    self.folderdict = {} ## Here the folder will be listed with all subdirectories 
    self.rm_cmd = None  ## make rm_cmd optional. E.g  srmrm or lcg-del
    self.rmdir_cmd = None ## make rm_cmd optional. E.g  srmdir or lcg-del 
    self.ls_cmd = None ## make the ls_cmd optional. E.g. srmls or lcg-ls or ls (on the NAF for /pnfs/deys.de stuff)
    self.prefix = ""  ## prefix is need for the grid comands 
    self.rm_files_cmds = []  ## here will be all files wich will be removed with cd self.rm_cmd 
    self.ncores = 10 ## the file removal will be done with the multicore mode. 
    self.nfiles = 0 ## Only for extra  inforamtion
    self.nfolder = 0 ## Only for extra inforamtion
  def set_ekp_cmd(self): ## if one is on ekp resources only takr srm commands
    self.rm_cmd = 'srmrm' 
    self.rmdir_cmd = 'srmrmdir' 
    self.ls_cmd = 'srmls'
    self.set_prefix()
  def set_naf_cmd(self): ## on the naf use ls for the /pnfs/desy.de folder. Otherwise you should also switch to srm only commands
    self.rm_cmd = 'srmrm' 
    self.rmdir_cmd = 'srmrmdir' 
    self.ls_cmd = 'ls'
    self.set_prefix()
  def set_prefix(self): ## check if the folder is in Karlsruhe or on NAF (Hamburg)
    if 'desy.de' in self.folder:
      self.prefix = 'srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN='
    elif 'gridka.de' in self.folder:
      self.prefix = 'srm://dgridsrm-fzk.gridka.de:8443/srm/managerv2?SFN='
  def list_full_dir(self, akt_folder = None, akt_dict=None): ## Go recursively true the folder 
    if not akt_folder: ## if it is the first time set some default values
      akt_folder = self.folder
      self.folderdict[akt_folder] = {} ## For each folder create a new sub dict 
      akt_dict = self.folderdict[akt_folder] ## And in this dict the Files and all other dicts will be filled
    akt_result = [] ## Will contain the result of the ls_cmd. The format should be full/path/to/file or full/path/to/subfolder 
    if self.ls_cmd in ['ls']: ## Use python tools instead of run_bash stuff
        akt_result = [os.path.join(akt_folder,f) for f in os.listdir(akt_folder)] ## make it the full path
    else:
        cmd = self.ls_cmd+' '+self.prefix+akt_folder ## this is thested for the srmls cmd
        akt_result = run_bash_default(cmd).splitlines()[1:] ## remove the first line since it the original path.
    for akt_result_lines in akt_result:
      akt_type,akt_obj =  self.get_line_info(akt_result_lines) ## pull the information out of the lines
      if akt_type in ['Folder']: ## If it is a folder  
        self.nfolder+=1 ## count the number of folder 
        akt_dict[akt_obj] = {} ## create a new subdic 
        self.list_full_dir(akt_folder+'/'+akt_obj,akt_dict[akt_obj]) ## and start the regression  
      else: ## if not folder is is a file
        self.nfiles+=1  ## count the number of files
        akt_dict.setdefault(akt_type, []).append(akt_obj) ## add ths enty to the list of files 
  def get_line_info(self,akt_line):
#    print akt_line
      test_element = akt_line.split('/')[-1].strip()
      if self.ls_cmd in ['srmls'] and not test_element: ## the srmls command adds a '/' if the entry is a folder. The last emlement is ''.strip() == None
          return 'Folder',akt_line.split('/')[-2].strip()
      if self.ls_cmd in ['ls'] and  os.path.isdir(akt_line): ## For the ls comand on can use python tools for the check if it is a directory
          return 'Folder',test_element
      elif test_element.split('.')[-1] in ['gz','root','sh','tar']: ## add here the known files 
              return 'Files',test_element
      else:
          print "Following entry is not recognized\n",akt_line,'\ntry it as file' ## will only pop up if the file is not known. Or something strange happens
          return 'Files',test_element

  def print_dict(self,akt_dict=None,akt_level=''): ## print the dict in a long format (for ech entry one line)
    if not akt_dict:
      akt_dict = self.folderdict[self.folder]
      print '-',self.folder
    for akt_key in akt_dict:
      if akt_key in ['Files']:
        for akt_file in akt_dict[akt_key]:
          print akt_level,' ',akt_file
      elif akt_dict[akt_key]:
        print akt_level,'-',akt_key
        self.print_dict(akt_dict[akt_key],akt_level+' ')
      else:
        print akt_level,'-',akt_key,'(empty)'
  def fill_all_rmfiles_cmds(self,akt_dict,akt_folder): ## Collect all files in the dict and add the rm_cmd
    for akt_key in akt_dict:
      if akt_key in ['Files']:
        while akt_dict[akt_key]:
          self.rm_files_cmds.append(self.rm_cmd+' '+self.prefix+akt_folder+'/'+akt_dict[akt_key].pop())
      else:
        self.fill_all_rmfiles_cmds(akt_dict[akt_key],akt_folder+'/'+akt_key)
  def rm_all_files(self): ## Will rm all files in the dict 
    self.fill_all_rmfiles_cmds(self.folderdict[self.folder],self.folder) ## Get all rm_cmds in one list
    p = multiprocessing.Pool(self.ncores) ## start ncores which will perform the parallel file removal 
    result = p.map(run_bash_default,self.rm_files_cmds) ## super cool pyton stuff: distribute the jobs to the ncores. Wait until it is finished. But works only with separate functions, therefore the run_bash_default is not part of the class 
    for err in result: ## Go through the ouptut and check for errors. Not tested jet (moslty because it seems to work perfetly)
        if not err:
            continue
        if not err.strip():
            continue
        print err
  def rm_all(self): ## Here the logcial order of the commands 
      print "start listing files"
      self.list_full_dir()
      print "start removing files:",self.nfiles
      self.rm_all_files() ## First rm all files. Usaly this takes the largest time. It can be parallelized straight forward.   
      print "start removing folder"
      self.rm_all_folders(self.folderdict[self.folder],self.folder) ## If  all (sub-)folders are empty they can be removed  
      print "finished"
  def rm_all_folders(self,akt_dict,akt_folder): ## Recursive rm the folders the most sub folder must be the first
    for akt_key in akt_dict: ## loop over all keys 
      if akt_key in ['Files']:
        if len(akt_dict[akt_key])>0: # Only internal check. If the rm file was not succefull this will not help
            print "Folder still contains files:"
            print akt_folder 
      else:
        self.rm_all_folders(akt_dict[akt_key],akt_folder+'/'+akt_key) ## go in all directory keys 
    run_bash_default(self.rmdir_cmd+' '+self.prefix+akt_folder) ## If the loop is finished one is at the very last surviving enty and kill them 





#folder_to_rm = rm_grid_folder('/pnfs/gridka.de/dcms/disk-only/store/user/swayand/test_skimming/')
#folder_to_rm = rm_grid_folder('/pnfs/gridka.de/dcms/disk-only/store/user/btreiber/test')

#folder_to_rm = rm_grid_folder('/pnfs/gridka.de/dcms/disk-only/store/user/btreiber/test/DYJetsToTauTau_M-50_13TeV-madgraph-pythia8-tauola_v2_FlatPU_0_50/K2Skims')


if __name__ == "__main__":
    if not opt.folder:
        parser.error("must give the one fodler with -f  /path/to/folder  e.g. -f /pnfs/desy.de/cms/tier2/store/user/swayand/MuMu_embedding/") 

    folder_to_rm = rm_grid_folder(opt.folder)
#    folder_to_rm.set_ekp_cmd()
    folder_to_rm.set_naf_cmd()    
    folder_to_rm.rm_all()


#    folder_to_rm.list_full_dir()



#loop = True
#while loop:
#  answer = raw_input( ("Sure that you wan't to delete"+opt.folder+" ? (Yes or No):  ") )
#  print answer
#  if answer in ['Yes']:
#    loop=False
#    print 'del: ',opt.folder    
#    rm_dir_rec(opt.folder)
#  elif answer in ['No']:
#    loop=False
#  else:
#    print "Please answer Yes or No (with capitals) and be aware what you are doing!!!!!"

