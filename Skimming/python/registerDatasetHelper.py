#! /usr/bin/env python
# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Raphael Friese <Raphael.Friese@cern.ch>

import os
import string

import json
import re

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
		return pd_name[pos:] 
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
			process = pd_name[0:posMass+length].replace("-", "")
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
		return filetype
	else:
		return default


def is_data(prod_camp, default=None):
	if (default == None):
		return prod_camp.find("DR")==-1
	else:
		return default 

def make_nickname(dict):
	nick = ""
	nick += dict["process"].replace("_", "")  + "_"
	nick += dict["campaign"].replace("_", "") + "_"
	nick += dict["scenario"].replace("_", "") + "_"
	nick += dict["energy"].replace("_", "")   + "TeV_"
	nick += dict["format"].replace("_", "")
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
			if not (re.match(str(query[name]), str(attribute).replace("_", "")) != None):
				matches = False
		if matches:
			return sample

def get_sample_by_nick(nickname):

	# split nickname
	process, campaign, scenario, energy, format = nickname.split("_")
	query = {
		"process" : process,
		"campaign" : campaign,
		"scenario" : scenario,
		"energy" : energy.strip("TeV"),
		"format" : format
	}

	#query_nick, sample = query_result(query)
	return query_result(query)
	#pd_name, details, filetype = options.sample.strip("/").split("/")
	#return pd_name, details, filetype
