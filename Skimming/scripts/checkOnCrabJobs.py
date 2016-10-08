#!/bin/env python
# usage: script must be called within the folder
# where the crab directories are. it's not clear
# why that is, yet

import argparse
import os
import json

def checkStatus(path, useExistingInput=False, verbosity=0):
	if verbosity > 0:
		print "checkStatus("+path+")"
		
	taskDict = {}
	
	if not useExistingInput:
		for dir in os.listdir(path):
			if os.path.isfile(dir):
				continue
			status = checkStatusOfSingleTask(dir, verbosity)
			taskDict = updateJobStatus(taskDict, dir, status, verbosity)
	else:
		taskDict = getExistingInputs(path, verbosity)
		for dir, status in taskDict.iteritems():
			if "COMPLETED" in status:
				continue
			status = checkStatusOfSingleTask(dir, verbosity)
			taskDict = updateJobStatus(taskDict, dir, status, verbosity)
	
	return taskDict

def checkStatusOfSingleTask(task, verbosity=0):
	if verbosity > 0:
		print "checkStatusOfSingleTask("+task+")"
		
	checkCommand = "crab status --dir "+task
	os.system(checkCommand+" >> tempStatus.txt")# TODO: find a way to read output from shell without creating temporary file
	
	status = "OTHER"
	
	with open("tempStatus.txt") as file:
		for line in file:
			if "Task status:" in line:
				if "SUBMITTED" in line:
					status = "SUBMITTED"
				elif "FAILED" in line:
					status = "FAILED"
				elif "COMPLETED" in line:
					status = "COMPLETED"
			elif "Jobs status:" in line:
				if "failed" in line:
					status = "FAILED"
	os.system("rm tempStatus.txt")
	
	return status

def updateJobStatus(taskDict, task, newStatus, verbosity=0):
	if verbosity > 0:
		print "updateJobStatus(taskDict, "+task+", "+newStatus+")"
	
	taskExists = False
	
	for key, status in taskDict.iteritems():
		if key == task:
			taskExists = True
			taskDict[task] = newStatus
	
	if not taskExists:
		taskDict.update({task : newStatus})
	
	return taskDict

def resubmit(taskDict, additional_args="", verbosity=0):
	if verbosity > 0:
		print "resubmit(taskDict, "+additional_args+")"
	
	for task, status in taskDict.iteritems():
		if "FAILED" in status:
			if verbosity > 1:
				print "resubmitting task "+task+" using "+additional_args
			resubmitCommand = "crab resubmit "+additional_args+" --dir "+task
			os.system(resubmitCommand)
			updateJobStatus(taskDict, task, "SUBMITTED", verbosity)
	
	return taskDict

def writeOutput(path, taskDict, verbosity=0):
	if verbosity > 0:
		print "writeOutput("+path+")"
	
	with open(path+"/taskStatus.json","w") as output:
		json.dump(taskDict, output)
	
	output.close()

def getExistingInputs(path, verbosity=0):
	if verbosity > 0:
		print "getExistingInputs("+path+")"

	taskDict = {}

	with open(path+"/taskStatus.json","r") as input:
		taskDict = json.load(input)
	
	return taskDict

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
	
	startDir = os.getcwd()
	os.chdir(args.dir)
	
	taskStatus = checkStatus(args.dir, args.use_existing_inputs, args.verbosity)
	
	if args.resubmit:
		taskStatus = resubmit(taskStatus, args.resubmit_args, args.verbosity)
	
	writeOutput(args.dir, taskStatus, args.verbosity)
	
	os.chdir(startDir)
	
	submitted = []
	failed = []
	completed = []
	other = []
	
	for task, status in taskStatus.iteritems():
		if "SUBMITTED" in status:
			submitted.append(task)
		elif "FAILED" in status:
			failed.append(task)
		elif "COMPLETED" in status:
			completed.append(task)
		else:
			other.append(task)
	
	if args.verbosity > 0:
		print "---------- List of tasks with failed jobs ----------"
		for task in failed:
			print task
		print
		print "---------- List of tasks with other jobs ----------"
		for task in other:
			print task
		print
	if args.verbosity > 1:
		print "---------- List of tasks with submitted jobs ----------"
		for task in submitted:
			print task
		print
		print "---------- List of tasks with completed jobs ----------"
		for task in completed:
			print task
		print
	
	print "---------- Summary ----------"
	print "Submitted: "+str(len(submitted))
	print "Failed:    "+str(len(failed))
	print "Completed: "+str(len(completed))
	print "Other:     "+str(len(other))
