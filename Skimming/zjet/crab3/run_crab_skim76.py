#!/bin/env python
# crab submission class


from mulitcrab_class import *
from optparse import OptionParser


global_work_area='/nfs/dust/cms/user/swayand/gc_zjets/'
name = "full_lep_v1"
cmsrun_cfg_file = "/afs/desy.de/user/s/swayand/xxl/jec/CMSSW_7_6_3_patch2/src/Kappa/Skimming/zjet/skim_76_cfg.py"


parser=OptionParser()
parser.add_option("-f", "--file", help="simple File with information about datasets. Should only contain lines with: Nick : Dataset/Fulll/Path/AOD ")
(opt, args) = parser.parse_args()


akt_jobs = multi_crab_job(name,global_work_area,cmsrun_cfg_file)
akt_jobs.get_jobs_from_workdir()
if opt.file:
  akt_jobs.init_jobs_from_simple_file(opt.file)

akt_jobs.submit_jobs()
#akt_jobs.crab_command('resubmit')
akt_jobs.crab_command()

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
