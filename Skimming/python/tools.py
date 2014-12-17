
# -*- coding: utf-8 -*-

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
