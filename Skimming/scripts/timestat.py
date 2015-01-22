#!/usr/bin/env python
# -*- coding: utf8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Joram Berger <joram.berger@cern.ch>

import operator
import re
import sys
import copy
import numpy as np


# this script works but it is ugly
# feel free to clean up or leave it to me when I am back
# Joram

def main(args):
	print "START"
	cmssw, kappa, numbers = parsefile('timerep.txt')
	#print cmssw, kappa, numbers
	print numbers
	tables = preparetable(cmssw, kappa)
	p = Barplot()
	kappa.sort(key=lambda k: int(k[9]), reverse=True)
	tables[0].sort(key=lambda k: int(k[1]), reverse=True)
	for k in kappa[:20]:
		print k
	print p.getmax([['a', 1, 4,], [2, -2, 'b']])
	bartab, names = bartable(tables[0][:20], kappa[:20])
	for b in bartab:
		print bartab.index(b), ":",  ", ".join(["%2.0f" % i for i in b])
	print names, len(names), len(bartab[0])
	p.stackedplot(bartab, numbers, 'test.pdf', ['DarkRed', 'Orange', 'black', 'DarkBlue', 'LightSkyBlue', 'DodgerBlue']*5, names, ['CPU', 'I/O', 'once' ,'run', 'lumi' , 'event'])
	print "done"


def preparetable(producers):
	pass
	
def prepareplot(producers, maxlines=20, mintime=5):
	pass

def plot(producers, filename='skim_timestat.png'):
	pass


multiple = {}
notpassed = {}


def bartable(producers, kprod):
	"""
	"""
	prods = filter(lambda x: x[0] != 'kappaTuple', producers)
	names = [p[0] for p in prods] + [k[0] for k in kprod]
	
	#ncmssw = len(producers)
	#nkappa = len(kprod)
	#print knumbers, ktime[2]
	#for i in range(len(ktime)):
	#	for col in range(4):
	#		ktime[i][col+1] *= float(knumbers[col]) / knumbers[3]
	#	print ktime[i][1:2]

	#ktime = sorted(ktime, key=operator.itemgetter(4), reverse=True)
	
	result = [
		[p[1] for p in prods] + [0]*len(kprod),
		[p[4] for p in prods] + [0]*len(kprod),
		([0] * len(prods)) + [k[5] for k in kprod],  # once
		([0] * len(prods)) + [k[6] for k in kprod],  # run
		([0] * len(prods)) + [k[7] for k in kprod],  # lumi
		([0] * len(prods)) + [k[8] for k in kprod],  # event
	]
	return result, names
	

def parsefile(filename):
	"""parse a given cmssw log file (with reports) and return three items:
	two lists of timing information for CMSSW and Kappa producers
	and general numbers about the CMSSW run
	"""
	timeon = False
	trigon = False
	kappaon = False
	numbers = {
		'once': 0,
		'runs': 0,
		'lumis': 0,
		'events': 0,       # from Kappa
		'nevents': 0,      # from CMSSW
		'producers': 0,
		'kproducers': 0,
		'runtime': 0,      # overall per event
		'kappatime': 0,    # Kappa runtime from Kappa information
		'kapparuntime': 0, # Kappa runtime from CMSSW information
	}
	producers = []  # each producer: name, real, cpu, count
	kproducers = [] # each procuder: name, once, run, lumi, event
	counts = {}     # temporary counts storage
	with open(filename) as f:
		log = f.read().split('\n')

	for line in log:
		l = line.split()
		if "TrigReport Events total" in line:  #parse directly
			try:
				numbers['nevents'] = int(l[4])
			except:
				print "The number of events could not be read from this line:"
				print line

		# switch parsing modes by heading
		if "TimeReport ---------- Module Summary ---[sec]----" in line:
			timeon = True
		if "T---Report end!" in line:
			timeon = False
		if "TrigReport ---------- Module Summary ------------" in line:
			trigon = True
		if "TimeReport ---------- Event  Summary ---[sec]----" in line:
			trigon = False
		if "Kappa timing information" in line:
			kappaon = True

		# parse in different modes
		if timeon:
			if "CPU" not in line and "per module-run" not in line and len(l) > 7:
				producers.append([l[7], float(l[2])*1000, float(l[1])*1000])
				numbers['runtime'] += float(l[2])*1000
		elif trigon:
			if "Visited" not in line and len(l) > 6:
				counts[l[6]] = int(l[1])
		elif kappaon:
			if line and "entries" in line:
				knumbers = line[15:].split()
				numbers['once'], numbers['runs'], numbers['lumis'], numbers['events'] = [int(n) for n in knumbers]
			if line and "timing" not in line and "KProducer" not in line and "entries" not in line:
				name, times = line.split(':')
				times = times.split()
				kproducers.append([name.strip(), float(times[2]), float(times[0]), float(times[1]), float(times[3])])

	for i in range(len(producers)):
		producers[i].append(counts[producers[i][0]] / numbers['nevents'])  # fill count value by producer name
		producers[i].append(max(0, producers[i][1] - producers[i][2]))  # IO (>0)
		producers[i].append(min(0, producers[i][1] - producers[i][2]))  # multicore speed up (<0)
	for i in range(len(kproducers)):
		kproducers[i].append(float(numbers['once']) / numbers['events'] * kproducers[i][1])
		kproducers[i].append(float(numbers['runs']) / numbers['events'] * kproducers[i][2])
		kproducers[i].append(float(numbers['lumis'])/ numbers['events'] * kproducers[i][3])
		kproducers[i].append(float(numbers['events'])/numbers['events'] * kproducers[i][4])
		kproducers[i].append(
			kproducers[i][5] +
			kproducers[i][6] +
			kproducers[i][7] +
			kproducers[i][8]
		)
	for p in producers:
		if p[0] == 'kappaTuple':
			numbers['kapparuntime'] = p[1]
			print "K", p[1]
	numbers['cmsswruntime'] = numbers['runtime'] - numbers['kapparuntime']
	return producers, kproducers, numbers
# groups: hpsPFTauDiscr, others

def preparetable(producers, kappaprod):
	print "BA"
	#producers = sorted(producers.iteritems(), key=operator.itemgetter(1).itemgetter(1), reverse=True)
	# shorten producer names
	replacements = {
		'phPFIsoDeposit': 'phDep:',
		'muPFIsoDeposit': 'muDep:',
		'muPFIsoValue': 'muIso:',
		'elPFIsoDeposit': 'elDep:',
		'elPFIsoValue': 'elIso:',
		'hpsPFTauDiscriminationBy': 'tauD:',
	}
	for p in producers:
		for rkey, rval in replacements.items():
			p[0] = p[0].replace(rkey, rval)

	# filter unused and multiple producers
	multi = {}
	unused = {}
	for p in producers:
		if len(p) == 0:
			raise IOError("emtpy producer")
		if p[3] == 0:
			unused[p[0]] = p[3]
		elif p[3] > 1:
			multi[p[0]] = p[3]
	print multi, unused
	# grouping - order: object > software > producer
	groups = { # name : [cmssw module, cmssw addons]
		'Electrons': ['patElectron', '^el'],
		'Muons': ['muon', '^(mu|pfmuIso)'],
		'Taus': ['^pfTaus($|Prod)', '(pfTauPile|PiZero|pfTausDisc|hps|tau|HPS|5PFJets|Associator|pf(Reco)?TauTag|combinatoricRecoTaus|Voronoi$|^recoTauP)'],
		'Jets': [None, 'xzy'],
		'PFCandidates': ['^pf(Pile|No|All)',None],
		'GenInfo': [None, 'TriggerResults'],
		'DataInfo': [None, 'TriggerResults'],
		'VertexSummary': ['OfflinePrimaryVert', None],
		'MET': ['pfMET', None],
		'unused': [None, '^ph'],
		'TreeInfo': [None, None],
		'BeamSpot': [None, None],
		'TriggerObjects': [None, None],
		'GenParticles': [None, None],
		'GenTaus': [None, None],
		'PileupDensity': [None, None],
		'BasicMET': [None, None],
		'kappa': ['kappaTuple', None],
	}
	objProducers = []
	matchednames = []
	# nested :  groupname    CMSSW main producers with timing       others CMSSW    Kappa producer
	# example: ['electrons', [['patElectrons', 63.]], [], [['KElectronProducer', 68.]]]
	for gname, gexp in groups.items():
		objProducers.append([gname, [], [], []])
		for i in range(2):
			for p in producers:
				if gexp[i] and re.search(gexp[i], p[0]) and p[0] not in matchednames:
					objProducers[-1][i+1] += [[p[0], p[1]]]
					matchednames.append(p[0])
		for p in kappaprod:
			if re.search("^%s$" % gname, p[0]) and p[0] not in matchednames:
				objProducers[-1][3] += [[p[0], p[5]]]
				matchednames.append(p[0])

	# find unmatched
	objProducers.append(['unmatched', [], [], []])
	for o in objProducers:
		for i in range(1,4):
			for q in o[i]:
				matchednames.append(q[0])
	for p in producers:
		if p[0] not in matchednames:
			objProducers[-1][2].append([p[0], p[1]])
	for p in kappaprod:
		if p[0] not in matchednames:
			objProducers[-1][3].append([p[0], p[5]])
	# print sorting
	for g in objProducers:
		print g[0], '-------------------------------'
		for i in range(3):
			print "  %s: %s" % (['C', 'c', 'K'][i], ", ".join(["%s(%.1f)" % (p[0], p[1]) for p in g[i+1]]))
	#print objProducers
	return producers, objProducers, multi, unused

def nix():
	multtime = 0
	for i in count:
		#print i, count[i], nevents
		if count[i] != nevents:
			multiple[i] = count[i]/nevents
			multtime += (count[i]/nevents-1) * real[i]


def printtable(producers, numbers):

	# print the output:
	print "Tested with %d events" % numbers['nevents']
	print "Running %d modules" % len(producers)
	print "Time per event: %.3f s\n" % numbers['runtime']

	#if modulesfailed:
	#	print "%d modules failed:"
	#	print "  "

	if multiple:
		print " %d modules run multiple times:" % len(multiple)
		for module in multiple:
			print "%3d   %s" %(multiple[module], module)
		print "this requires %1.1f ms more time than running them once" % multtime

	times = []
	ctimes = []
	modules = []
	print "\nTimes per module in ms"
	print "   real |   cpu | Module"
	restc = 0
	restr = 0
	for module, time in reals[:maxlines]:
		if time >= mintime:
			print "%7.1f %7.1f   %s" %(time, cpu[module], module)
			if module != 'kappaTuple':
				times += [time]
				ctimes += [cpu[module]]
				modules += [module]
		else:
			print cpu[module], time, module
			restc += cpu[module]
			restr += time


def pnix():
	modules += ['all others']
	times += [restr]
	ctimes += [restc]

	"""plotting:
	CMSSW: min(real,cpu), max(real,cpu) with diff. color
	Kappa: stacked: run, lumi, first, event
	"""
	ncmssw = len(modules)
	print knumbers, ktime[2]
	for i in range(len(ktime)):
		for col in range(4):
			ktime[i][col+1] *= float(knumbers[col]) / knumbers[3]
		print ktime[i][1:2]

	ktime = sorted(ktime, key=operator.itemgetter(4), reverse=True)

	krun = ([0] * ncmssw) + [sum(k[1:2]) for k in ktime]
	klumi = ([0] * ncmssw) + [sum(k[1:3]) for k in ktime]
	kfirst = ([0] * ncmssw) + [sum(k[1:4]) for k in ktime]
	kevent = ([0] * ncmssw) + [sum(k[1:5]) for k in ktime]

	modules += [k[0] for k in ktime]
	times += [0] * len(ktime)
	ctimes += [0] * len(ktime)

	ymax = 1.12 * max([max(l) for l in [kevent, times, ctimes]])

import matplotlib.pyplot as mpl

class Barplot():
	defaultwidth = 0.8
	
	def getmax(self, lists, tmp=0):
		"""return the maximum of numbers in a deeply nested list"""
		t = tmp
		for i in lists:
			if type(i) == list:
				t = max(t, self.getmax(i, tmp))
			elif type(i) == int or type(i) == float:
				t = max(t, i)
		return t

	def getmax2(self, lists):
		pass
	
	def __init__(self):
		mpl.rcParams['text.usetex'] = False
		mpl.rcParams['font.size'] = 9
		mpl.rcParams['legend.fontsize'] = 8
		self.width = self.defaultwidth

	def _axis(self, ymax, xmax):
		self.fig = mpl.figure(figsize=[7,4])
		self.ax = self.fig.add_subplot(111, position=[0.1, 0.4, 0.7, 0.52])
		self.ymax = ymax
		self.ax2 = self.fig.add_subplot(111, position=[0.3, 0.6, 0.2, 0.2], aspect='equal')
		self.ax.set_xlim(0, xmax)
		self.ax.set_ylim(0, ymax)



	def _labels(self, names):
		self.ax.set_ylabel("time / ms")
		self.ax.set_title("Module execution time per event")
		self.ind = np.arange(len(names)) + 0.05  # the x locations for the groups
		self.ax.set_xticks(self.ind)
		print names, self.ind
		self.ax.set_xticklabels(names, rotation=-90, ha='left')
		self.ax.legend(loc='center right')
	def bla():
		ax.axvline(ncmssw, color='black')
		ax.text(ncmssw + 0.3, 0.90*self.ymax, "Kappa", color='DarkBlue')
		ax.text(ncmssw - 0.3, 0.90*self.ymax, "CMSSW", ha='right', color='DarkRed') 
		ax.text(0.3 * ncmssw, 0.90*self.ymax, "runs: %d" % knumbers[0])
		ax.text(0.3 * ncmssw, 0.85*self.ymax, "lumisections: %d" % knumbers[1])
		ax.text(0.3 * ncmssw, 0.80*self.ymax, "events: %d" % knumbers[3]) # nproducers, nkprod, timek, timec, time all


	
	def _multistackedbars(self, lists, colors, labels):
		"""plot a list of lists of lists:
			- bars next to each other
			- bars stacked
			- normal bars
		"""
		# plot the output:
		# done independently from plotting frameworks on purpose

		mintimes = [min(r,c) for r,c in zip(times, ctimes)]
		self.width = self.defaultwidth / len(lists)
		
		
		for i, l in zip(range(len(lists)), lists):
			shift = 0.1 + i * self.width

			self._stackedbars(stack, shift, colors, labels)

	def _stackedbars(self, stack, shift, colors, labels):
		ys = [np.array([0]*len(stack[0]))]
		print ys
		for s in stack:
			print "S", np.array(s)
			print len(s), len(ys[-1])
			ys.append([a + b for a, b in zip(ys[-1], s)])
		for i, y in zip(range(len(ys)), reversed(ys)):
			if labels is not None:
				self._bars(self.ind+shift, y, color=colors[len(colors) - 1 - i], label=labels[len(labels) - 1 - i])
			else:
				self._bars(self.ind+shift, y, color=colors[len(colors) - 1 - i])
		self.ax.legend(loc='center right')


	def _bars(self, x, y, color, label=None):
		print "%r, %r, %r, %r, %r" %(x, y, self.width, color, label)
		self.ax.bar(x, y, self.width, color=color, label=label)
		"""
		rects3 = ax.bar(ind+shift, mintimes, width, color='DarkRed', label="CPU time")
		rects7 = ax.bar(ind+shift, kevent, width, color='LightSkyBlue', label="per event")
		rects6 = ax.bar(ind+shift, kfirst, width, color='DodgerBlue', label="once")
		rects5 = ax.bar(ind+shift, klumi, width, color='Blue', label="per lumi")
		rects4 = ax.bar(ind+shift, krun, width, color='DarkBlue', label="per run")
		"""

	def _insertpie(self, values, colors):
		self.ax.pie()
		
	def _save(self, timeplot_filename):
		self.fig.savefig(timeplot_filename)

	def multistackedplot(self, lists, filename, colors, labels):
		self.ymax = self.getmax(lists)
		self._axis()
		self._labels()
		self._multistackedbars(lists, colors, labels)
		self._save(filename)
	
	def stackedplot(self, lists, numbers, filename, colors, xlabels, labels=None):
		self._axis(self.getmax(lists) * 1.2, len(xlabels) + 0.2)
		self._labels(xlabels)
		self._stackedbars(lists, 0.1, colors, labels)
		self.ax.axvline(19.05, color='black')
		self.ax2.pie([numbers['cmsswruntime'],numbers['kapparuntime']], colors = ['DarkRed', 'DodgerBlue'], #labels=['CMSSW', 'Kappa']
			autopct='%.f%%') #, startangle=90)
		self._save(filename)

if __name__ == "__main__":
	main(sys.argv)
