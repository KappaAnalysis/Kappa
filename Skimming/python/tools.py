# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Thomas Mueller <tmuller@cern.ch>

import os
import subprocess
import sys


def flattenList(listOfLists):
	"""
	flatten 2D list
	return [1, 2, 3, 4, ...] for input [[1, 2], [3, 4, ...], ...]
	"""
	return [item for subList in listOfLists for item in subList]


def get_repository_revisions(repo_scan_base_dirs=["$CMSSW_BASE/src"], repo_scan_depth=3):
	import glob
	import subprocess
	
	# expand possible environment variables in paths
	if isinstance(repo_scan_base_dirs, basestring):
		repo_scan_base_dirs = [repo_scan_base_dirs]
	repo_scan_base_dirs = [os.path.expandvars(repoScanBaseDir) for repoScanBaseDir in repo_scan_base_dirs]
	
	# construct possible scan paths
	subDirWildcards = ["*/" * level for level in range(repo_scan_depth+1)]
	scanDirWildcards = [os.path.join(repoScanBaseDir, subDirWildcard) for repoScanBaseDir in repo_scan_base_dirs for subDirWildcard in subDirWildcards]
	
	# globbing and filter for directories
	scanDirs = flattenList([glob.glob(scanDirWildcard) for scanDirWildcard in scanDirWildcards])
	scanDirs = [scanDir for scanDir in scanDirs if os.path.isdir(scanDir)]
	
	# key: directory to check type of repository
	# value: command to extract the revision
	repoVersionCommands = {
		".git" : "git rev-parse HEAD",
		".svn" : "svn info"# | grep Revision | awk '{print $2}'"
	}
	
	result = {}
	
	# loop over dirs and revision control systems and write revisions to the config dict
	for repoDir, currentRevisionCommand in repoVersionCommands.items():
		repoScanDirs = [os.path.join(scanDir, repoDir) for scanDir in scanDirs]
		repoScanDirs = [glob.glob(os.path.join(scanDir, repoDir)) for scanDir in scanDirs]
		repoScanDirs = flattenList([glob.glob(os.path.join(scanDir, repoDir)) for scanDir in scanDirs])
		repoScanDirs = [os.path.abspath(os.path.join(repoScanDir, "..")) for repoScanDir in repoScanDirs]
		
		for repoScanDir in repoScanDirs:
			popenCout, popenCerr = subprocess.Popen(currentRevisionCommand.split(), stdout=subprocess.PIPE, cwd=repoScanDir).communicate()
			result[repoScanDir] = popenCout.replace("\n", "")
	
	return result

def get_cmssw_version():
	"""returns 'CMSSW_X_Y_Z'"""
	return os.environ["CMSSW_RELEASE_BASE"].split('/')[-1]

def get_cmssw_version_number():
	"""returns 'X_Y_Z' (without 'CMSSW_')"""
	return get_cmssw_version().split("CMSSW_")[1]

def read_grid_control_includes(filenames):
	nicknameslist = []
	for filename in filenames:
		nicknameslist.append(read_grid_control_include(filename))
	nicknames = [item for sublist in nicknameslist for item in sublist]
	return nicknames

def read_grid_control_include(filename):
	f = open(filename)
	a = []
	for line in f:
		a.append(line.replace("\n", "").replace("\t", "").replace(" ",""))
	a.remove("[global]")
	a.remove("include=")
	nicks = []
	for line in a:
		if(not line.startswith(";")):
			if(line.endswith(".conf")):
			#	print line
				for nick in read_grid_control_dataset(line):
					nicks.append(nick)
			else:
				print "could not parse " + line + " from " + filename
				sys.exit()
	return nicks

def read_grid_control_dataset(filename):
	f = open(filename)
	a = []
	nicks = []
	for line in f:
		a.append(line.replace("\n", "").replace("\t", "").replace(" ",""))
	a.remove("[CMSSW_Advanced]")
	a.remove("dataset+=")
	a.remove("")
	#print a
	for line in a:
		nick = line.split(":")
		if not nick[0].startswith(";"):
			nicks.append(nick[0])
	return nicks

def is_above_cmssw_version(version_to_test):
	cmssw_version_number = get_cmssw_version_number()
	split_cmssw_version = [int(i) for i in cmssw_version_number.split("_")[0:3]]
	for index in range(len(version_to_test)):
		if(version_to_test[index] > split_cmssw_version[index]):
			return False
		elif(version_to_test[index] < split_cmssw_version[index]):
			return True
	return True

