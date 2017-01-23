#!/usr/bin/env python
# encoding: utf8


def diff(datasetLumis, processedLumis):
	''' diff(X, Y) -> (X-Y)
	
	given X and a strict subset Y of X it will calculate all elements not in Y.
	Where X and Y are dicts of string to list-of-pairs.
	
	>>> diff({'foo':[[1,13]]}, {})
	{'foo': [[1, 13]]}
	
	CASE-1:
	 a[x] =               [-----------]
	 b[x] = [------]
	CASE-2:
	 a[x] =               [-----------]
	 b[x] =                                 [------]
	>>> diff({'foo':[[1,3],[10,15],[20,25]]}, {'foo':[[1,3], [20,25]]})     # CASE-1 and CASE-2
	{'foo': [[10, 15]]}
	
	CASE-3:
	 a[x] =               [-----------]
	 b[x] =               [-----------]
	>>> diff({'foo':[[1,3],[10,15],[20,25]]}, {'foo':[[10,15]]})     # CASE-3
	{'foo': [[1, 3], [20, 25]]}
	
	CASE-4:
	 a[x] =               [-----------]
	 b[x] =               [-----]
	>>> diff({'foo':[[1,13]]}, {'foo':[[1,7]]})     # CASE-4
	{'foo': [[8, 13]]}
	
	CASE-5:
	 a[x] =               [-----------]
	 b[x] =                     [-----]
	>>> diff({'foo':[[1,13]]}, {'foo':[[7,13]]})    # CASE-5
	{'foo': [[1, 6]]}
	
	CASE-6:
	 a[x] =               [-----------]
	 b[x] =                  [----]
	>>> diff({'foo':[[1,13]]}, {'foo':[[5,7]]})  # CASE-6
	{'foo': [[1, 4], [8, 13]]}
	
	CASE-7:
	 a[x] =               [-----------]
	 b[x] =               [----]  [---]
	>>> diff({'foo':[[1,13]]}, {'foo':[[1,5],[7,13]]})  # CASE-7
	{'foo': [[6, 6]]}
	
	CASE-8:
	 a[x] =               [-----------]
	 b[x] =               [--] [-] [--]
	>>> diff({'foo':[[1,13]]}, {'foo':[[1,5],[7,8],[10,13]]})  # CASE-8
	{'foo': [[6, 6], [9, 9]]}
	
	'''

	missingLumis = dict()
	
	for run in datasetLumis:
		if run not in processedLumis:
			missingLumis[run] = datasetLumis[run]
			continue
		
		tempList = list()
		for lumiSection in datasetLumis[run]:
			lumiRange = range(lumiSection[0], lumiSection[1]+1)
			for lumiSubsec in processedLumis[run]:
				if lumiSubsec[0] in lumiRange:
					tempList.append(lumiSubsec)
			if tempList == []:
				missingLumis.setdefault(run, list()).append(lumiSection)
			for i in range(len(tempList)):
				if tempList[i] == tempList[0] and tempList[0][0] > lumiSection[0]:
					missingLumis.setdefault(run, list()).append([lumiSection[0], tempList[i][0]-1])
				if tempList[i] == tempList[-1]:
					if tempList[-1][1] < lumiSection[1]:
						missingLumis.setdefault(run, list()).append([tempList[i][1]+1, lumiSection[1]])
					continue
				missingLumis.setdefault(run, list()).append( [tempList[i][1]+1, tempList[i+1][0]-1] )
			tempList = list()
	return missingLumis




if __name__ == '__main__':
	
	import argparse
	import glob
	import os
	import sys

	import json

	
	parser = argparse.ArgumentParser(description='Create the missingLumis.json file')

	parser.add_argument("-d", "--crabtask-dir", required=True,
						help="Directory containing the crab task")

	args = parser.parse_args()

	inputDatasetLumisFile = json.load(open(os.path.join(args.crabtask_dir, 'results/inputDatasetLumis.json'), 'r'))
	processedLumisFile = json.load(open(os.path.join(args.crabtask_dir, 'results/processedLumis.json'), 'r'))
	
	with open(os.path.join(args.crabtask_dir, 'results/missingLumis.json'), 'w') as outfile:
		json.dump(diff(inputDatasetLumisFile, processedLumisFile), outfile)



