#-# Copyright (c) 2010 - All Rights Reserved
#-#   Fred Stober <stober@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>

import re
from grid_control import datasets, DatasetError
from grid_control.datasets import NickNameProducer

def lookup(data, keyMap, default = None):
	for key in keyMap:
		if key in data:
			return keyMap[key]
	return (default, '')[default == None]

def addPart(data):
	return ('_%s' % data, '')[data == '']

def parseCuts(data):
	tmp = re.findall('([0-9]+)to([0-9]+)', data.lower())
	if tmp:
		return tmp[0]
	return filter(lambda x: int(x) > 0, re.findall('pt[-_]*([0-9]+)', data.lower()))


class Summer10Nicks(NickNameProducer):
	def getName(self, oldnick, dataset, block):
		if oldnick != '':
			return oldnick
		(pd, sd, tier) = dataset.lstrip('/').split('/')

		genMap = {
			'madgraph': 'MG',
			'alpgen': 'AG',
			'herwigjimmy': 'HJ',
			'herwig': 'HW',
			'pythia8': 'P8',
		}
		tuneMap = {
			'madgraph': '',
			'alpgen': '',
			'herwigjimmy': '',
			'herwig': '',
			'pythia8': 'T1',
			'ProPT0': 'ProPT0',
			'Z2': 'Z2',
		}
		condMap = {
			'Summer10-START36_V9': 'Su10S36v9',
			'Summer10-START36_V10': 'Su10S36v10',
		}
		dsMap = {
			'QCD': 'qcd',
			'MinBias': 'mb',
		}
		metaMap = {
			'2Jets': '2j',
			'3Jets': '3j',
			'4Jets': '4j',
			'5Jets': '5j',
			'6Jets': '6j',
		}

		nick = '%s%s%s' % (lookup(pd, dsMap, 'xyz'), lookup(pd, genMap, 'P6'), lookup(pd, metaMap, ''))
		nick += addPart(lookup(pd, tuneMap, 'D6T'))
		nick += addPart(lookup(sd, condMap))
		if 'flat' in pd.lower():
			nick += '_flat'
		else:
			nick += addPart(str.join('_', map(lambda x: '%04d' % int(x), parseCuts(pd))))
		return nick


class Fall10Nicks(NickNameProducer):
	def getName(self, oldnick, dataset, block):
		if oldnick != '':
			return oldnick
		(pd, sd, tier) = dataset.lstrip('/').split('/')

		dsMap = {
			'QCD': 'qcd',
			'MinBias': 'mb',
		}
		genMap = {
			'pythia8': 'P8',
		}
		condMap = {
			'Fall10-START38_V12': 'F10S38v12',
			'BX156_START38_V12': 'F10S38v12_PPU',
		}
		tuneMap = dict(map(lambda x: ('Tune' + x, x), ['Z2', 'ProPT0', 'P0', 'DW', 'D6T', 'CW']))
		tuneMap['pythia8'] = 'T1'
		metaMap = dict(map(lambda x: (x, x), ['TauBiased', 'MuEnrichedPt', 'MuPt5Enriched', 'EMEnriched']))
		nick = '%s%s' % (lookup(pd, dsMap, 'xyz'), lookup(pd, genMap, 'P6'))
		nick += addPart(lookup(pd, tuneMap, 'D6T'))
		nick += addPart(lookup(sd, condMap))
		nick += addPart(lookup(pd, metaMap))
		if 'flat' in pd.lower():
			nick += '_flat'
		else:
			nick += addPart(str.join('_', map(lambda x: '%04d' % int(x), parseCuts(pd))))
		return nick


class Summer11Nicks(NickNameProducer):
	def getName(self, oldnick, dataset, block):
		if oldnick != '':
			return oldnick
		try:
			(pd, sd, tier) = dataset.lstrip('/').split('/')
			pd = pd.replace('_pythia', '-pythia')
			pd = pd.replace('_herwig', '-herwig')
			dsMap = {
				'QCD': 'qcd',
				'MinBias': 'mb',
			}
			genMap = {
				'herwig6': 'HJ',
				'herwigpp': 'HW',
				'pythia6': 'P6',
				'pythia8': 'P8',
			}
		
			condMap = {
				'Summer11-PU_S3_START42_V11': 'SU11S42v11PUS3',
				'Summer11-PU_S4_START42_V11': 'SU11S42v11PUS4',
			}
			print pd.split("_")
			if pd.count("_") < 3:
				ds, cut, other = pd.split('_', 2)
			else:
				ds, cut, tune, other = pd.split('_', 3)
			if 'Tune' not in tune:
				tune += '_' + (filter(lambda x: x.startswith('Tune'), pd.split('_')) + ['!'])[0]
			tune = tune.replace('Tune', '')
			nick = '%s%s_%s' % (lookup(pd, dsMap, '!'), lookup(pd, genMap, '!'), tune)
			nick += addPart(lookup(sd, condMap, '!'))
			if 'flat' in pd.lower():
				nick += '_flat'
			else:
				nick += addPart(str.join('_', map(lambda x: '%04d' % int(x), parseCuts(cut))))
			if '!' in nick:
				raise DatasetError("Dataset %s was mapped to %s" % (dataset, nick))
		except:
			print oldnick, dataset
			raise
		return nick
