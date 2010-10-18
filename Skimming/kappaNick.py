import re
from grid_control import datasets, DatasetError
from grid_control.datasets import NickNameProducer

def lookup(data, keyMap, default = None):
	for key in keyMap:
		if key in data:
			return keyMap[key]
	return (default, '')[default == None]

def addPart(data):
	return ("_%s" % data, '')[data == '']

def parseCuts(data):
	tmp = re.findall('([0-9]+)to([0-9]+)', data.lower())
	if tmp:
		return tmp[0]
	return re.findall('pt[-_]*([0-9]+)', data.lower())

class Summer10Nicks(NickNameProducer):
	def getName(self, oldnick, dataset):
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

		nick = "%s%s%s" % (lookup(pd, dsMap, 'xyz'), lookup(pd, genMap, 'P6'), lookup(pd, metaMap, ''))
		nick += addPart(lookup(pd, tuneMap, 'D6T'))
		nick += addPart(lookup(sd, condMap))
		if 'flat' in pd.lower():
			nick += "_flat"
		else:
			nick += addPart(str.join('_', map(lambda x: "%04d" % int(x), parseCuts(pd))))
		return nick
