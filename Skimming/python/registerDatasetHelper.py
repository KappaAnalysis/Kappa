#! /usr/bin/env python
# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Raphael Friese <Raphael.Friese@cern.ch>

import os
import string

import json
import re
from Kappa.Skimming.getNumberGeneratedEventsFromDB import getNumberGeneratedEventsFromDB
cmssw_base = os.environ.get("CMSSW_BASE")
dataset = os.path.join(cmssw_base, "src/Kappa/Skimming/data/datasets.json")

def get_campaign(details, default=None, energy=None):
	if (default == None):
		campaign = details.split("-")[0]
		if energy == "8":
			campaign = campaign.split("_")[0]
		return campaign
	else:
		return default


def get_scenario(details, default=None, energy=None, data=False):
	if data:
		return ''.join(details.split('-')[1:])
	if (default == None):
		scenario = details.split("-")[1]
		if (energy == "7" or energy == "8"):
			scenario = scenario.split("_")[0] +"_"+ scenario.split("_")[1]
		if (energy == "13" or energy =="14"):
			scenario = scenario.split("_")[0]
		return scenario
	else:
		return default

def get_energy(pd_name, details, default=None, data=False):
	if (default == None):
		if not data:
			endpos = pd_name.find("TeV")
			startpos = pd_name[0:endpos].rfind("_")+1
			return pd_name[startpos:endpos] 
		else: 
			if details.find("2011")!=-1: return "7"
			if details.find("2012")!=-1: return "8"
			if details.find("2015")!=-1: return "13"
			if details.find("2016")!=-1: return "14"
			return "0"
	else:
		return default


def get_generator(pd_name, default=None, data=False):
	if data:
		return ""

	if (default == None):
		pos = pd_name.find("TeV")+4
		generators = []
		if "amcatnlo" in pd_name[pos:]:
			generators.append("amcatnlo")
		if "powheg" in pd_name[pos:]:
			generators.append("powheg")
		if "madgraph" in pd_name[pos:]:
			generators.append("madgraph")
		if "pythia" in pd_name[pos:]:
			generators.append(pd_name[pos:][pd_name[pos:].find("pythia"):pd_name[pos:].find("pythia")+7])
		return '-'.join(generators)
	else:
		return default

def get_process(pd_name, default=None):
	if (default == None):
		pos = pd_name.find("_")
		if(pos!=-1):
			process = pd_name[0:pos]
		else:
			process = pd_name
		posMass = pd_name.find("_M-")
		if posMass != -1:
			length = 3+ pd_name[posMass+3:].find("_")
			try:
				int (pd_name[posMass+3])
				process = pd_name[0:posMass+length].replace("-", "")
			except:
				pass
		else:
			posMass = pd_name.find("_M")
			if posMass != -1:
				length = 2+ pd_name[posMass+2:].find("_")
				try:
					int (pd_name[posMass+2])
					process = pd_name[0:posMass+length]
				except:
					pass
		htPos = pd_name.find("HT-")
		if(htPos!=-1):
			length = pd_name[htPos:].find("_")
			process += "_"+pd_name[htPos: htPos + length]
		return process 
	else:
		return default

def get_globaltag(details, default=None):
	if (default == None):
		return details.split("_")[0]
	else:
		return default

def is_embedded(filetype, default=False):
	if (default == True):
		return True
	else:
		return filetype == "USER"

def get_format(filetype, default=False):
	if (default == None):
		return filetype.replace("AODSIM", "AOD")
	else:
		return default


def is_data(prod_camp, default=None):
	if (default == None):
		pos = prod_camp.find("Run")+3
		year = prod_camp[pos:pos+4]
		if year in ["2011", "2012", "2015", "2016"]:
			return True
		else:
			return False
	else:
		return default

def get_n_generated_events(sample):
	return getNumberGeneratedEventsFromDB(sample)

def get_n_generated_events_from_nick(nick):
	sample = get_sample_by_nick(nick)
	dict = load_database(dataset)
	if sample in dict and "n_events_generated" in dict[sample]:
		return dict[sample]["n_events_generated"]
	else:
		return -1

def get_xsec(nick):
	sample = get_sample_by_nick(nick)
	dict = load_database(dataset)
	if sample in dict and "xsec" in dict[sample]:
		return dict[sample]["xsec"]
	else:
		return -1

def get_generator_weight(nick):
	sample = get_sample_by_nick(nick)
	dict = load_database(dataset)
	if sample in dict and "generatorWeight" in dict[sample]:
		return dict[sample]["generatorWeight"]
	else:
		return -1

def make_nickname(dict):
	nick = ""
	nick += dict["process"].replace("_", "")  + "_"
	nick += dict["campaign"].replace("_", "") + "_"
	nick += dict["scenario"].replace("_", "") + "_"
	nick += dict["energy"].replace("_", "")   + "TeV_"
	nick += dict["format"].replace("_", "") + ("" if (dict["data"] or dict["embedded"]) else "_")
	nick += dict["generator"].replace("_", "")
	return nick

def load_database(dataset):
	json_data = open(dataset)
	return json.load(json_data)

def save_database(dict, dataset):

	with open(dataset, 'w') as fp:
		json.dump(dict, fp, sort_keys=True, indent = 4)

def query_result(query):
	dict = load_database(dataset)

	for sample, values in dict.iteritems():
		matches = True
		for name, attribute in values.iteritems():
			if not name in query: continue
			if query[name] == '': continue
			if not (re.match('\\b'+str(query[name])+'\\b', str(attribute).replace("_", "")) != None):
				matches = False
		if matches:
			return sample

def get_sample_by_nick(nickname):

	# split nickname
	split_nick = nickname.split("_")
	query = {
		"process" : split_nick[0],
		"campaign" : split_nick[1],
		"scenario" : split_nick[2],
		"energy" : split_nick[3].strip("TeV"),
		"format" : split_nick[4],
		"generator" : (split_nick[5] if (len(split_nick) > 5) else "")
	}

	#query_nick, sample = query_result(query)
	return query_result(query)
	#pd_name, details, filetype = options.sample.strip("/").split("/")
	#return pd_name, details, filetype
