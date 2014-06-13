
# -*- coding: utf-8 -*-
from Kappa.Skimming.datasets import *

def getProcess(nickname):
	for string in Data:
		if string in nickname:
			return "Data"
	for string in Embedded:
		if string in nickname:
			return "Embedded"
	for string in DYJets:
		if string in nickname:
			return "DYJets"
	for string in TTJets:
		if string in nickname:
			return "TTJets"
	for string in Dibosons:
		if string in nickname:
			return "Dibosons"
	for string in WJets:
		if string in nickname:
			return "WJets"
	for string in SM_GluGluToHToTauTau:
		if string in nickname:
			return "SM_GluGluToHToTauTau"
	for string in SM_VBFHToTauTau:
		if string in nickname:
			return "SM_VBFHToTauTau"
	for string in SM_WH_ZH_TTH_HToTauTau:
		if string in nickname:
			return "SM_WH_ZH_TTH_HToTauTau"
	for string in SM_TTH_HToTauTau:
		if string in nickname:
			return "SM_TTH_HToTauTau"
	return ""

def getIsEmbedded(nickname):
	if getProcess(nickname) == "Embedded":
		return True
	return False

def getJetMultiplicity(nickname):
	for string in DYJets:
		if string in nickname:
			if string[2] in ["1", "2", "3", "4"]:
				return int(string[2])
			else:
				return 0
	return 0

def getRunPeriod(nickname):
	for string in Data:
		if string in nickname:
			posLeft = nickname.find("_Run") + 4
			posRight = posLeft + nickname[posLeft:].find("_")
			return nickname[posLeft:posRight]
	return "0"

def getGenerator(nickname): ########todo
	if getProcess(nickname) == "Data": return "None"
	generators = ["madgraph_tauola", "pythia_tauola", "powheg_tauola", "powheg_pythia", "pythia", "madgraph"]
	for generator in generators:
		if nickname.find(generator) > -1: return generator
#	raise NameError("Generator information for nickname " + nickname + " could not be determined!")
	return ""

def getDatasetName(nickname):
	posLeft = nickname.rfind("_")
	centerOfMassEnergy = getCenterOfMassEnergy(nickname)
	return datasets[nickname[0:posLeft]]["dataset"][centerOfMassEnergy]


def getPuScenario(nickname, centerOfMassEnergy):
	if getProcess(nickname) == "Data": return "None"
	dataSetName = getDatasetName(nickname)
	posLeft = dataSetName.find("PU_")
	posRight = posLeft + dataSetName[posLeft+3:].find("_")
	return dataSetName[posLeft:posRight+3]

def getProductionCampaignGlobalTag(nickname, centerOfMassEnergy):
	dataSetName = getDatasetName(nickname)
	if getProcess(nickname) == "Data": return "None"
	posLeft = dataSetName.find("_START") +1
	print posLeft
	if posLeft < 1 :
		return ""
	posRight = posLeft + dataSetName[posLeft+5:].find("-")
	return dataSetName[posLeft:posRight+5]

def getCenterOfMassEnergy(nickname):
	posLeft = nickname.rfind("_")+1
	posRight = nickname.rfind("TeV")
	if posLeft != posRight:
		return int(nickname[posLeft:posRight])
	else:
		return 8

def isData(nickname):
	return (getProcess(nickname) == "Data" or getProcess(nickname) == "Embedded")

def checkDatasets():
	for nickname in datasets:
		for centerOfMassEnergy in datasets[nickname]["dataset"]:
			tmpNickname = nickname + "_" + str(centerOfMassEnergy) + "TeV"
			print ""
			print "Nickname:" + tmpNickname
			print "Process: " + str(getProcess(tmpNickname))
			print "Energy: " + str(centerOfMassEnergy) + " GeV"
			print "Embedded: " + str(getIsEmbedded(tmpNickname))
			print "JetMulitplicity: " + str(getJetMultiplicity(tmpNickname))
			print "runPeriod: " + str(getRunPeriod(tmpNickname))
			print "Generator: " + str(getGenerator(tmpNickname))
			print "PU Scenario: " + str(getPuScenario(tmpNickname, centerOfMassEnergy))
			print "Dataset Name: " + str(getDatasetName(tmpNickname))
			print "Production Campaign Global Tag: " + str(getProductionCampaignGlobalTag(tmpNickname, centerOfMassEnergy))
			print "isData: " + str(isData(tmpNickname))

def checkDataset(nickname):
	centerOfMassEnergy = getCenterOfMassEnergy(nickname)
	print ""
	print "Nickname:" + nickname
	print "Process: " + str(getProcess(nickname))
	print "Energy: " + str(centerOfMassEnergy) + " GeV"
	print "Embedded: " + str(getIsEmbedded(nickname))
	print "JetMulitplicity: " + str(getJetMultiplicity(nickname))
	print "runPeriod: " + str(getRunPeriod(nickname))
	print "Generator: " + str(getGenerator(nickname))
	print "PU Scenario: " + str(getPuScenario(nickname, centerOfMassEnergy))
	print "Dataset Name: " + str(getDatasetName(nickname))
	print "Production Campaign Global Tag: " + str(getProductionCampaignGlobalTag(nickname, centerOfMassEnergy))
	print "isData: " + str(isData(nickname))
