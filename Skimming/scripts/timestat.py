#!/usr/bin/env python

import operator

# this script works but it is ugly
# feel free to clean up or leave it to me when I am back
# Joram

# options -> argparse
mintime = 5
maxlines = 12

with open('timerep.txt') as f: # the logfile of the CMSSW run
	log = f.read().split('\n')
# this file should be directly accessed in the root file
timeplot_filename = 'skim_timestat.png'
# end options


real = {}
cpu = {}
count = {}
multiple = {}
realsum = 0
notpassed = {}

timeon = False
trigon = False

for line in log:
	l = line.split()
	if "TrigReport Events total" in line:
		try:
			nevents = int(l[4])
		except:
			print "The number of events could not be read from this line:"
			print line
			
	if "TimeReport ---------- Module Summary ---[sec]----" in line:
		timeon = True
	if "T---Report end!" in line:
		timeon = False
	if "TrigReport ---------- Module Summary ------------" in line:
		trigon = True
	if "TimeReport ---------- Event  Summary ---[sec]----" in line:
		trigon = False

	if timeon:
		if "CPU" not in line and "per module-run" not in line and len(l) > 7:
			real[l[7]] = float(l[2])*1000
			cpu[l[7]] = float(l[1])*1000
			realsum += float(l[2])
			#print l[7], l[2]
	if trigon:
		#print "ON"
		if "Visited" not in line and len(l) >6:
			count[l[6]] = int(l[1])

reals = sorted(real.iteritems(), key=operator.itemgetter(1), reverse=True)

multtime = 0
for i in count:
	#print i, count[i], nevents
	if count[i] != nevents:
		multiple[i] = count[i]/nevents
		multtime += (count[i]/nevents-1)*real[i]


# print the output:
print "Tested with %d events" % nevents
print "Running %d modules" % len(real)
print "Time per event: %.3f s\n" % realsum

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
for module, time in reals[:maxlines]:
	if time >= mintime:
		print "%7.1f %7.1f   %s" %(time, cpu[module], module)
		times += [time]
		ctimes += [cpu[module]]
		modules += [module]


# plot the output:
# done independently from plotting frameworks on purpose
import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
plt.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.3)
ax = fig.add_subplot(111)



ind = np.arange(len(modules))  # the x locations for the groups
width = 0.35       # the width of the bars
rects1 = ax.bar(ind, times, width, color='DarkBlue', label="real time")
rects2 = ax.bar(ind+width, ctimes, width, color='Orange', label="CPU time")
ax.set_ylabel("time / ms")
ax.set_title("Module execution time per event")

ax.set_xticks(ind)
ax.set_xticklabels(modules, rotation=-35, ha='left')
ax.legend()

fig.savefig(timeplot_filename)

