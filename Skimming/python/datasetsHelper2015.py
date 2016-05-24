# -*- coding: utf-8 -*-
#-# Copyright (c) 2014 - All Rights Reserved
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>

from Kappa.Skimming.registerDatasetHelper import *
import FWCore.ParameterSet.Config as cms

def isData(nickname):
	sample = get_sample_by_nick(nickname)
	dict = load_database(dataset)
	sample_details = dict[sample]
	data = sample_details["data"]
	return data

def getProcess(nickname):
	sample = get_sample_by_nick(nickname)
	dict = load_database(dataset)
	sample_details = dict[sample]
	process = sample_details["process"]
	return process

def getTreeInfo(nickname, globaltag, kappaTag):

	sample = get_sample_by_nick(nickname)
	dict = load_database(dataset)
	sample_details = dict[sample]

	pd_name, details, filetype = sample.strip("/").split("/")

	centerOfMassEnergy = int(sample_details["energy"])
	data = sample_details["data"]
	isEmbedded = sample_details["embedded"]
	miniaod = (sample_details["format"] == "MINIAODSIM" or sample_details["format"] == "MINIAOD")

	return data, isEmbedded, miniaod, cms.PSet(
		dataset               = cms.string(str(sample)),
		generator             = cms.string(str(sample_details["generator"])),
		productionProcess     = cms.string(str(sample_details["process"])),
		globalTag             = cms.string(globaltag),
		scenario              = cms.string(str(sample_details["scenario"])),
		campaign              = cms.string(str(sample_details["campaign"])),
		kappaTag              = cms.string(kappaTag),
		isEmbedded            = cms.bool(isEmbedded),
		centerOfMassEnergy    = cms.int32(centerOfMassEnergy),
		isData                = cms.bool(data)
	)
