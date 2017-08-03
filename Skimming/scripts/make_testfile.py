import FWCore.ParameterSet.Config as cms
from WMCore.DataStructs.LumiList import LumiList
import sys, os

from  Kappa.Skimming.datasetsHelperTwopz import datasetsHelperTwopz
datasetsHelper = datasetsHelperTwopz(os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/datasets.json"))

process = cms.Process('NoSplit')

nicknames = [
"SingleElectron_Run2017B_23Jun2017v1_13TeV_MINIAOD",	
"SUSYGluGluToHToTauTauM160_RunIISpring16MiniAODv1_PUSpring16_13TeV_MINIAOD_pythia8",	
"SUSYGluGluToHToTauTauM160_RunIIFall15MiniAODv2_PU25nsData2015v1_13TeV_MINIAOD_pythia8"
	]
nicknames = [nick for nick in nicknames if datasetsHelper.is_compatible_release(nick)]
for nick in nicknames:
	print "Extracting 100 Events. Nickname: " + nick
	testfile = datasetsHelper.get_testfile_for_nick(nick)
	print "Testfile: \t " + testfile
	process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(testfile))
	process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(100))
	process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
	process.output = cms.OutputModule("PoolOutputModule",
	    outputCommands = cms.untracked.vstring( "keep *_*_*_*"),
	    fileName = cms.untracked.string(nick+".root"),
	)
	process.out = cms.EndPath(process.output)
print "ok"
