#-# Copyright (c) 2014 - All Rights Reserved
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>
#-#   Stefan Wayand <stefan.wayand@gmail.com>
#-#   Thomas Mueller <tmuller@cern.ch>
#-#   Yasmin Anstruther <yasmin.anstruther@kit.edu>

## ------------------------------------------------------------------------
# Central cmsRun config file to be used with grid-control 
# Settings are stored ordered on physics objects
# Object-related settings should be done in designated python configs
# if possible, run2 configs import the run1 configs and add some extra information
## ------------------------------------------------------------------------

# Kappa test: CMSSW 7.4.14
# Kappa test: scram arch slc6_amd64_gcc491
# Kappa test: checkout script scripts/checkoutCmssw7414PackagesForSkimming.py
# Kappa test: output kappaTuple.root

import sys
if not hasattr(sys, 'argv'):
	sys.argv = ["cmsRun", "runFrameworkMC.py"]

import os
import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.datasetsHelper2015 as datasetsHelper
import Kappa.Skimming.tools as tools

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('python')
options.register('globalTag', 'MCRUN2_74_V9', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'GlobalTag')
options.register('kappaTag', 'KAPPA_2_0_0', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'KappaTag')
options.register('nickname', 'SUSYGluGluToHToTauTauM160_RunIISpring15DR74_Asympt25ns_13TeV_MINIAOD_pythia8', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Dataset Nickname')
options.register('testfile', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Path for a testfile')
options.register('maxevents', -1, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'maxevents')
options.register('outputfilename', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Filename for the Outputfile')
options.register('testsuite', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'Run the Kappa test suite. Default: True')
options.register('preselect', True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'apply preselection at CMSSW level on leptons')
options.parseArguments()

cmssw_version_number = tools.get_cmssw_version_number()
split_cmssw_version = cmssw_version_number.split("_")

def getBaseConfig( globaltag= 'START70_V7::All',
                   testfile=cms.untracked.vstring(""),
                   maxevents=100, ## -1 = all in file
                   nickname = 'SUSYGluGluToHToTauTauM160_RunIISpring15DR74_Asympt25ns_13TeV_MINIAOD_pythia8',
                   kappaTag = 'Kappa_2_0_0',
				   outputfilename = ''):

	from Kappa.Skimming.KSkimming_template_cfg import process
	## ------------------------------------------------------------------------
	# count number of events before doing anything elese
	process.p *= process.nEventsTotal
	process.p *= process.nNegEventsTotal

	muons = "slimmedMuons"
	electrons = "slimmedElectrons"
	taus = "slimmedTaus"
	# produce selected collections and filter events with not even one Lepton
	if(options.preselect):
		from Kappa.Skimming.KSkimming_preselection import do_preselection
		do_preselection(process)
		process.p *= process.goodEventFilter

		process.selectedKappaTaus.cut = cms.string('pt > 15 && abs(eta) < 2.5') 
		process.selectedKappaMuons.cut = cms.string('pt > 8 && abs(eta) < 2.6')
		process.selectedKappaElectrons.cut = cms.string('pt > 8 && abs(eta) < 2.7')
		process.goodEventFilter.minNumber = cms.uint32(2)
		muons = "selectedKappaMuons"
		electrons = "selectedKappaElectrons"
		taus = "selectedKappaTaus"
	## ------------------------------------------------------------------------
		# possibility to write out edmDump. Be careful when using unsceduled mode
	process.load("Kappa.Skimming.edmOut")
	process.ep = cms.EndPath()
	#process.ep *= process.edmOut

	## ------------------------------------------------------------------------
	# Configure Kappa
	if testfile:
		process.source.fileNames      = testfile
	else:
		process.source 			  = cms.Source('PoolSource', fileNames=cms.untracked.vstring())
	process.maxEvents.input	      = maxevents
	process.kappaTuple.verbose    = cms.int32(0)
	process.kappaTuple.profile    = cms.bool(True)
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag   = globaltag
		print "GT (overwritten):", process.GlobalTag.globaltag
	## ------------------------------------------------------------------------
	# Configure Metadata describing the file
	# Important to be evaluated correctly for the following steps
	process.kappaTuple.active = cms.vstring('TreeInfo')
	data, isEmbedded, miniaod, process.kappaTuple.TreeInfo.parameters = datasetsHelper.getTreeInfo(nickname, globaltag, kappaTag)

	## ------------------------------------------------------------------------
	# General configuration
	if ((cmssw_version_number.startswith("7_4") and split_cmssw_version[2] >= 14) or (cmssw_version_number.startswith("7_6"))):
		process.kappaTuple.Info.pileUpInfoSource = cms.InputTag("slimmedAddPileupInfo")

	process.kappaTuple.active += cms.vstring('VertexSummary')            # save VertexSummary,

	process.load("Kappa.Skimming.KVertices_cff")
	process.goodOfflinePrimaryVertices.src = cms.InputTag('offlineSlimmedPrimaryVertices')
	process.p *= ( process.makeVertexes )
	process.kappaTuple.VertexSummary.whitelist = cms.vstring('offlineSlimmedPrimaryVertices')  # save VertexSummary,
	process.kappaTuple.VertexSummary.rename = cms.vstring('offlineSlimmedPrimaryVertices => goodOfflinePrimaryVerticesSummary')
	if (cmssw_version_number.startswith("7_6")):
		process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("offlineSlimmedPrimaryVertices"))

	process.kappaTuple.active += cms.vstring('TriggerObjectStandalone')
	if(data and ("Run2015" in nickname)):
		process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "RECO")

	process.kappaTuple.active += cms.vstring('BeamSpot')                 # save Beamspot,
	if (cmssw_version_number.startswith("7_6")):
		process.kappaTuple.BeamSpot.offlineBeamSpot = cms.PSet(src = cms.InputTag("offlineBeamSpot"))

	if not isEmbedded and data:
			process.kappaTuple.active+= cms.vstring('DataInfo')          # produce Metadata for data,

	if not isEmbedded and not data:
			process.kappaTuple.active+= cms.vstring('GenInfo')           # produce Metadata for MC,
			process.kappaTuple.active+= cms.vstring('GenParticles')      # save GenParticles,
			process.kappaTuple.active+= cms.vstring('GenTaus')           # save GenParticles,

			process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")
			process.kappaTuple.GenTaus.genTaus.src = cms.InputTag("prunedGenParticles")

	if isEmbedded:
		#process.load('RecoBTag/Configuration/RecoBTag_cff')
		#process.load('RecoJets/JetAssociationProducers/ak5JTA_cff')
		#process.ak5PFJetNewTracksAssociatorAtVertex.tracks = "tmfTracks"
		#process.ak5PFCHSNewJetTracksAssociatorAtVertex.tracks = "tmfTracks"
		#process.p *= process.btagging
		# disable overrideHLTCheck for embedded samples, since it triggers an Kappa error
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)
		process.kappaTuple.active += cms.vstring('DataInfo')
		process.kappaTuple.active += cms.vstring('GenParticles') # save GenParticles,
		process.kappaTuple.active += cms.vstring('GenTaus') # save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("genParticles","","EmbeddedRECO")

	## ------------------------------------------------------------------------
	# Trigger
	from Kappa.Skimming.hlt_run2 import hltBlacklist, hltWhitelist
	process.kappaTuple.Info.hltWhitelist = hltWhitelist
	process.kappaTuple.Info.hltBlacklist = hltBlacklist

	## ------------------------------------------------------------------------

	#process.kappaTuple.active += cms.vstring('packedPFCandidates') # save PFCandidates. Not sure for what, because might not be usefull for isolation
	#process.kappaTuple.packedPFCandidates.packedPFCandidates = cms.PSet(src = cms.InputTag("packedPFCandidates"))


	from RecoMET.METPUSubtraction.localSqlite import recorrectJets
	recorrectJets(process)
	jetCollection = "patJetsReapplyJEC"


	## ------------------------------------------------------------------------
	# Configure Muons
	process.load("Kappa.Skimming.KMuons_miniAOD_cff")
	process.kappaTuple.Muons.muons.src = cms.InputTag(muons)
	process.kappaTuple.Muons.muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Muons.muons.srcMuonIsolationPF = cms.InputTag("")
	process.kappaTuple.Muons.use03ConeForPfIso = cms.bool(True)
	for src in [ "muPFIsoDepositCharged", "muPFIsoDepositChargedAll", "muPFIsoDepositNeutral", "muPFIsoDepositGamma", "muPFIsoDepositPU"]:
		setattr(getattr(process, src), "src", cms.InputTag(muons))

	process.kappaTuple.active += cms.vstring('Muons')
	process.kappaTuple.Muons.noPropagation = cms.bool(True)
	process.p *= ( process.makeKappaMuons )

	## ------------------------------------------------------------------------
	# Configure Electrons
	process.kappaTuple.active += cms.vstring('Electrons')
	process.load("Kappa.Skimming.KElectrons_miniAOD_cff")
	process.kappaTuple.Electrons.electrons.src = cms.InputTag("slimmedElectrons")
	process.kappaTuple.Electrons.electrons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Electrons.electrons.rhoIsoInputTag = cms.InputTag("slimmedJets", "rho")
	process.kappaTuple.Electrons.electrons.allConversions = cms.InputTag("reducedEgamma", "reducedConversions")
	from Kappa.Skimming.KElectrons_miniAOD_cff import setupElectrons
	process.kappaTuple.Electrons.srcIds = cms.string("standalone");

	process.kappaTuple.Electrons.ids = cms.vstring("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-veto",
					"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-loose",
					"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-medium",
					"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-tight",
					"electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values")


	setupElectrons(process, electrons)
	process.p *= ( process.makeKappaElectrons )
	## ------------------------------------------------------------------------
	process.kappaTuple.active += cms.vstring('PatTaus')
	process.kappaTuple.PatTaus.taus.binaryDiscrBlacklist = cms.vstring()
	process.kappaTuple.PatTaus.taus.floatDiscrBlacklist = cms.vstring()
	# just took everything from https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendation13TeV
	process.kappaTuple.PatTaus.taus.preselectOnDiscriminators = cms.vstring ()
	process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist = cms.vstring(
	                                                                       "decayModeFinding",
	                                                                       "decayModeFindingNewDMs",
	                                                                       "byLooseCombinedIsolationDeltaBetaCorr3Hits",
	                                                                       "byMediumCombinedIsolationDeltaBetaCorr3Hits",
	                                                                       "byTightCombinedIsolationDeltaBetaCorr3Hits",
	                                                                       "byCombinedIsolationDeltaBetaCorrRaw3Hits",
	                                                                       "chargedIsoPtSum",
	                                                                       "neutralIsoPtSum",
	                                                                       "puCorrPtSum",
	                                                                       "footprintCorrection",
	                                                                       "photonPtSumOutsideSignalCone",
	                                                                       "byIsolationMVArun2v1DBoldDMwLTraw",
	                                                                       "byLooseIsolationMVArun2v1DBoldDMwLT",
	                                                                       "byMediumIsolationMVArun2v1DBoldDMwLT",
	                                                                       "byTightIsolationMVArun2v1DBoldDMwLT",
	                                                                       "byVTightIsolationMVArun2v1DBoldDMwLT",
	                                                                       "byIsolationMVArun2v1DBnewDMwLTraw",
	                                                                       "byLooseIsolationMVArun2v1DBnewDMwLT",
	                                                                       "byMediumIsolationMVArun2v1DBnewDMwLT",
	                                                                       "byTightIsolationMVArun2v1DBnewDMwLT",
	                                                                       "byVTightIsolationMVArun2v1DBnewDMwLT",
	                                                                       "againstMuonLoose3",
	                                                                       "againstMuonTight3",
	                                                                       "againstElectronMVA5category",
	                                                                       "againstElectronMVA5raw",
	                                                                       "againstElectronVLooseMVA5",
	                                                                       "againstElectronLooseMVA5",
	                                                                       "againstElectronMediumMVA5",
	                                                                       "againstElectronTightMVA5",
	                                                                       "againstElectronVTightMVA5",
	                                                                       "againstElectronMVA6category",
	                                                                       "againstElectronMVA6raw",
	                                                                       "againstElectronVLooseMVA6",
	                                                                       "againstElectronLooseMVA6",
	                                                                       "againstElectronMediumMVA6",
	                                                                       "againstElectronTightMVA6",
	                                                                       "againstElectronVTightMVA6",
	                                                                       "byLooseCombinedIsolationDeltaBetaCorr3HitsdR03",
	                                                                       "byMediumCombinedIsolationDeltaBetaCorr3HitsdR03",
	                                                                       "byTightCombinedIsolationDeltaBetaCorr3HitsdR03",
	                                                                       "byLooseIsolationMVArun2v1DBdR03oldDMwLT",
	                                                                       "byMediumIsolationMVArun2v1DBdR03oldDMwLT",
	                                                                       "byTightIsolationMVArun2v1DBdR03oldDMwLT",
	                                                                       "byVTightIsolationMVArun2v1DBdR03oldDMwLT"
	)
	process.kappaTuple.PatTaus.taus.floatDiscrWhitelist = process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist
	## ------------------------------------------------------------------------
	## Configure Jets
	process.kappaTuple.active += cms.vstring('PileupDensity')
	process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
	process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")
	if (cmssw_version_number.startswith("7_6")):
		process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAll"))
	process.kappaTuple.active += cms.vstring('PatJets')
	if (cmssw_version_number.startswith("7_6")):
		process.kappaTuple.PatJets.ak4PF = cms.PSet(src=cms.InputTag(jetCollection))
	#from Kappa.Skimming.KMET_run2_cff import configureMVAMetForMiniAOD
	#configureMVAMetForMiniAOD(process)

	## Standard MET and GenMet from pat::MET
	process.kappaTuple.active += cms.vstring('PatMET')
	process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag("slimmedMETs"))
	process.kappaTuple.PatMET.pfmetT1 = cms.PSet(src=cms.InputTag("patpfMETT1"))
	process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"))

	## Write MVA MET to KMETs
	process.kappaTuple.active += cms.vstring('PatMETs')
	# new MVA MET
	from RecoMET.METPUSubtraction.MVAMETConfiguration_cff import runMVAMET
	runMVAMET( process, jetCollectionPF = jetCollection)
	process.kappaTuple.PatMETs.MVAMET = cms.PSet(src=cms.InputTag("MVAMET", "MVAMET"))
	process.MVAMET.srcLeptons  = cms.VInputTag(muons, electrons, taus) # to produce all possible combinations
	process.MVAMET.requireOS = cms.bool(False)


	## ------------------------------------------------------------------------
	## GenJets 
	if not data:
		process.load('PhysicsTools/JetMCAlgos/TauGenJets_cfi')
		process.load('PhysicsTools/JetMCAlgos/TauGenJetsDecayModeSelectorAllHadrons_cfi')
		process.tauGenJets.GenParticles = cms.InputTag("prunedGenParticles")
		process.p *= ( 
			process.tauGenJets +
			process.tauGenJetsSelectorAllHadrons
			)
		process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets")
		process.kappaTuple.active += cms.vstring('GenJets')
		if (cmssw_version_number.startswith("7_6")):
			process.kappaTuple.GenJets.tauGenJets = cms.PSet(src=cms.InputTag("tauGenJets"))
			process.kappaTuple.GenJets.tauGenJetsSelectorAllHadrons = cms.PSet(src=cms.InputTag("tauGenJetsSelectorAllHadrons"))

	## ------------------------------------------------------------------------
	## Further information saved to Kappa output 
	# add python config to TreeInfo
	process.kappaTuple.TreeInfo.parameters.config = cms.string(process.dumpPython())

	# add repository revisions to TreeInfo
	for repo, rev in tools.get_repository_revisions().iteritems():
			setattr(process.kappaTuple.TreeInfo.parameters, repo, cms.string(rev))


	## ------------------------------------------------------------------------
	## Count Events after running all filters 
	if not data:
		process.nEventsTotal.isMC = cms.bool(True)
		process.nNegEventsTotal.isMC = cms.bool(True)
		process.nEventsFiltered.isMC = cms.bool(True)
		process.nNegEventsFiltered.isMC = cms.bool(True)

	process.p *= process.nEventsFiltered
	process.p *= process.nNegEventsFiltered
	process.kappaTuple.active += cms.vstring('FilterSummary')

	## ------------------------------------------------------------------------
	## if needed adapt output filename
	process.p *= process.kappaOut
	if outputfilename != '':
		process.kappaTuple.outputFile = cms.string('%s'%outputfilename)

	return process

if __name__ == "__main__" or __name__ == "kSkimming_run2_cfg":

	if options.testsuite:
		testPaths = ['/storage/6/fcolombo/kappatest/input', '/nfs/dust/cms/user/fcolombo/kappatest/input']
		testPath = [p for p in testPaths if os.path.exists(p)][0]
		globalTag = 'MCRUN2_74_V9'
		testFile = "SUSYGluGluHToTauTau_M-120_13TeV_MCRUN2.root"
		nickName = "SUSYGluGluToHToTauTauM120_RunIISpring15DR74_Asympt25ns_13TeV_AODSIM_pythia8"
		process = getBaseConfig(options.globalTag, nickname=options.nickname, kappaTag=options.kappaTag, testfile=cms.untracked.vstring("file://%s"%options.testfile), maxevents=options.maxevents)

	else:
		if options.testfile:
			process = getBaseConfig(options.globalTag, nickname=options.nickname, kappaTag=options.kappaTag, testfile=cms.untracked.vstring("file://%s"%options.testfile), maxevents=options.maxevents)
		else:
			if options.outputfilename:
				process = getBaseConfig(options.globalTag, nickname=options.nickname, kappaTag=options.kappaTag, maxevents=options.maxevents, outputfilename=options.outputfilename)
			else:
				process = getBaseConfig(options.globalTag, nickname=options.nickname, kappaTag=options.kappaTag, maxevents=options.maxevents)
