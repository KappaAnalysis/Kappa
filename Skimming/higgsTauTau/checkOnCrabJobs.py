#!/bin/env python
# usage: script must be called within the folder
# where the crab directories are. it's not clear
# why that is, yet

import argparse
import os

def checkStatus(path, verbosity=0, dirs_submitted=None, dirs_failed=None, dirs_completed=None, dirs_other=None):
	if verbosity > 0:
		print "checkStatus("+path+", "+str(verbosity)+")"
	
	if dirs_submitted is None:	
		dirs_submitted = []
		
	if dirs_failed is None:	
		dirs_failed = []
		
	if dirs_completed is None:	
		dirs_completed = []
		
	if dirs_other is None:	
		dirs_other = []
	
	for dir in os.listdir(path):
		if os.path.isfile(dir) or dir in dirs_completed:
			continue
		checkCommand = "crab status --dir "+dir
		os.system(checkCommand+" >> tempStatus.txt")
		if verbosity > 0:
			os.system("cat tempStatus.txt")
		with open("tempStatus.txt") as file:
			for line in file:
				if "Task status:" in line:
					if "SUBMITTED" in line and not dir in dirs_submitted:
						dirs_submitted.append(dir)
					elif "FAILED" in line and not "SUBMITFAILED" in line and not dir in dirs_failed:
						dirs_failed.append(dir)
					elif "COMPLETED" in line:
						dirs_completed.append(dir)
					else:
						if not dir in dirs_other:
							dirs_other.append(dir)
				elif "Jobs status:" in line:
					if "failed" in line and not dir in dirs_failed:
						if dir in dirs_submitted:
								dirs_submitted.remove(dir)
						dirs_failed.append(dir)
		os.system("rm tempStatus.txt")
	return dirs_submitted, dirs_failed, dirs_completed, dirs_other
	
def resubmit(tasks, additional_args="", verbosity=0):		
	for task in tasks:
		if verbosity > 0:
			print "resubmitting task "+task+" using "+additional_args
		resubmitCommand = "crab resubmit "+additional_args+" --dir "+task
		os.system(resubmitCommand)
		tasks.remove(task)

def writeOutput(path, submitted, failed, completed, other, verbosity=0):
	if verbosity > 0:
		print "writeOutput("+path+", ...)"
		
	output_submitted = open(path+"/submitted.txt","w")
	for task in submitted:
		output_submitted.write(task+"\n")
		
	output_submitted.close()
	
	output_failed = open(path+"/failed.txt","w")
	for task in failed:
		output_failed.write(task+"\n")
		
	output_failed.close()
	
	output_completed = open(path+"/completed.txt","w")
	for task in completed:
		output_completed.write(task+"\n")
		
	output_completed.close()
	
	output_other = open(path+"/other.txt","w")
	for task in other:
		output_other.write(task+"\n")
		
	output_other.close()

def getExistingInputs(path, verbosity=0):#TODO: needs proper implementation
	if verbosity > 0:
		print "getExistingInputs("+path+")"
	
	#return submitted, failed, completed, other

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Check in on how your crab jobs are doing.")
	
	parser.add_argument("-d", "--dir", required=True,
	                    help="Directory containing the crab jobs.")
	parser.add_argument("--use-existing-inputs", action="store_true", default=False,
						help="Take output from previous execution of this script into account. [Default: %(default)s]")
	parser.add_argument("-r","--resubmit", action="store_true", default=False,
						help="Automatically resubmit failed jobs. [Default: %(default)s]")
	parser.add_argument("--resubmit-args", default="",
						help="Additional arguments for job resubmission. [Default: %(default)s]")
	parser.add_argument("-v","--verbosity", type=int, default=0, choices=[0,1,2],
						help="Control how much info is printed. [Default: %(default)s]")
	
	args = parser.parse_args()
	
	if args.use_existing_inputs:
		print "Not implemented, yet"
	else:
		submitted, failed, completed, other = checkStatus(args.dir, args.verbosity)
	
	if args.resubmit:
		resubmit(failed,args.resubmit_args, args.verbosity)
	
	writeOutput(args.dir, submitted, failed, completed, other, args.verbosity)
		
	if args.verbosity > 0:
		print "---------- List of tasks with failed jobs ----------"
		os.system("cat "+args.dir+"/failed.txt")
		print
		print "---------- List of tasks with other jobs ----------"
		os.system("cat "+args.dir+"/other.txt")
		print
	if args.verbosity > 1:
		print "---------- List of tasks with submitted jobs ----------"
		os.system("cat "+args.dir+"/submitted.txt")
		print
		print "---------- List of tasks with completed jobs ----------"
		os.system("cat "+args.dir+"/completed.txt")
		print
	
	print "---------- Summary ----------"
	print "Submitted: "+str(len(submitted))
	print "Failed:    "+str(len(failed))
	print "Completed: "+str(len(completed))
	print "Other:     "+str(len(other))
