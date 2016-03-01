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
	## Write out edmFile to allos unscheduled modules to work
	process.load("Kappa.Skimming.edmOut")
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
	process.ep *= process.kappaOut
	## ------------------------------------------------------------------------
	# Configure Metadata describing the file
	# Important to be evaluated correctly for the following steps
	process.kappaTuple.active = cms.vstring('TreeInfo')
	data, isEmbedded, miniaod, process.kappaTuple.TreeInfo.parameters = datasetsHelper.getTreeInfo(nickname, globaltag, kappaTag)

	process.p *= process.nEventsTotal
	process.p *= process.nNegEventsTotal
	## ------------------------------------------------------------------------
	# General configuration
	if ((cmssw_version_number.startswith("7_4") and split_cmssw_version[2] >= 14) or (cmssw_version_number.startswith("7_6"))):
		process.kappaTuple.Info.pileUpInfoSource = cms.InputTag("slimmedAddPileupInfo")

	process.kappaTuple.active += cms.vstring('VertexSummary')            # save VertexSummary,
	if miniaod:
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
	if not miniaod:
		process.kappaTuple.active += cms.vstring('TriggerObjects')

	if not isEmbedded and data:
			process.kappaTuple.active+= cms.vstring('DataInfo')          # produce Metadata for data,

	if not isEmbedded and not data:
			process.kappaTuple.active+= cms.vstring('GenInfo')           # produce Metadata for MC,
			process.kappaTuple.active+= cms.vstring('GenParticles')      # save GenParticles,
			process.kappaTuple.active+= cms.vstring('GenTaus')           # save GenParticles,

			if(miniaod):
				process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")
				process.kappaTuple.GenTaus.genTaus.src = cms.InputTag("prunedGenParticles")
	# Prune genParticles
	if not isEmbedded and not data and not miniaod:
		process.load("Kappa.Skimming.PruneGenParticles_cff")
	
	# Special settings for embedded samples
	# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonTauReplacementWithPFlow
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
	# Configure PFCandidates and offline PV
	if(not miniaod):
		process.load("Kappa.Skimming.KPFCandidates_run2_cff")
		process.kappaTuple.active += cms.vstring('PFCandidates') # save PFCandidates for deltaBeta corrected
		process.kappaTuple.PFCandidates.whitelist = cms.vstring( # isolation used for electrons and muons.
		##	"pfNoPileUpChargedHadrons",    ## switch to pfAllChargedParticles
			"pfAllChargedParticles",       ## same as pfNoPileUpChargedHadrons +pf_electrons + pf_muons
			"pfNoPileUpNeutralHadrons",
			"pfNoPileUpPhotons",
			"pfPileUpChargedHadrons",
			)
		##process.p *= ( process.makePFBRECO * process.makePFCandidatesForDeltaBeta )
		process.p *= ( process.makeKappaPFCandidates )

	if(miniaod):
		process.kappaTuple.active += cms.vstring('packedPFCandidates') # save PFCandidates. Not sure for what, because might not be usefull for isolation
		if (cmssw_version_number.startswith("7_6")):
			process.kappaTuple.packedPFCandidates.packedPFCandidates = cms.PSet(src = cms.InputTag("packedPFCandidates"))


	from RecoMET.METPUSubtraction.localSqlite import recorrectJets
	recorrectJets(process)
	jetCollection = "patJetsReapplyJEC"


	## ------------------------------------------------------------------------
	# Configure Muons
	if not miniaod:
		process.load("Kappa.Skimming.KMuons_run2_cff")
	if(miniaod):
		process.load("Kappa.Skimming.KMuons_miniAOD_cff")
		process.kappaTuple.Muons.muons.src = cms.InputTag("slimmedMuons")
		process.kappaTuple.Muons.muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.kappaTuple.Muons.muons.srcMuonIsolationPF = cms.InputTag("")
		process.kappaTuple.Muons.use03ConeForPfIso = cms.bool(True)

	process.kappaTuple.active += cms.vstring('Muons')
	process.kappaTuple.Muons.minPt = cms.double(8.0)
	process.kappaTuple.Muons.noPropagation = cms.bool(True)
	process.p *= ( process.makeKappaMuons )

	## ------------------------------------------------------------------------
	# Configure Electrons
	process.kappaTuple.active += cms.vstring('Electrons')
	if(miniaod):
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

	if not miniaod:
		process.load("Kappa.Skimming.KElectrons_run2_cff")
		process.kappaTuple.Electrons.minPt = cms.double(8.0)
		from Kappa.Skimming.KElectrons_run2_cff import setupElectrons

		process.kappaTuple.Electrons.ids = cms.vstring("cutBasedElectronID_Spring15_25ns_V1_standalone_loose",
						"cutBasedElectronID_Spring15_25ns_V1_standalone_medium",
						"cutBasedElectronID_Spring15_25ns_V1_standalone_tight",
						"cutBasedElectronID_Spring15_25ns_V1_standalone_veto",
						"ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values")

	setupElectrons(process)
	process.p *= ( process.makeKappaElectrons )
	## ------------------------------------------------------------------------
	if(miniaod):
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
	# Configure Taus
	if(not miniaod):
		process.load("Kappa.Skimming.KTaus_run2_cff")
		process.kappaTuple.active += cms.vstring('Taus')
		process.kappaTuple.Taus.minPt = cms.double(8.0)
		process.p *= ( process.makeKappaTaus )

	# Reduced number of Tau discriminators
	# The blacklist is to some degree arbitrary to get below 64 binaty tau discriminators
	# - they may need to be changed as soon as 'official' discriminators for TauID 2014 will be published
		process.kappaTuple.Taus.taus.binaryDiscrBlacklist = cms.vstring("^shrinkingCone.*", ".*PFlow$", ".*raw.*", ".*Raw.*", "^hpsPFTauDiscriminationByVLoose.*", "^hpsPFTauDiscriminationByVTight.*", "^hpsPFTauDiscriminationByMedium.*")
		process.kappaTuple.Taus.taus.preselectOnDiscriminators = cms.vstring("hpsPFTauDiscriminationByDecayModeFindingNewDMs")

	## ------------------------------------------------------------------------
	## Configure Jets

	process.kappaTuple.active += cms.vstring('PileupDensity')
	if not miniaod:
		process.load("Kappa.Skimming.KJets_run2_cff")
		process.kappaTuple.active += cms.vstring('Jets')
		process.kappaTuple.Jets = process.kappaTupleJets
		process.kappaTuple.Jets.minPt = cms.double(10.0)

		#Check if working
		process.p *= (
			process.ak4PFJetsCHScor *
		#	process.makePFJets *
		#	process.makePFJetsCHS *
		#	process.makeQGTagging *
		#	process.makeBTagging *
		#	process.makePUJetID *
			process.kt6PFJets
		)

	if miniaod:
		process.kappaTuple.active += cms.vstring('PatJets')
		if (cmssw_version_number.startswith("7_6")):
			process.kappaTuple.PatJets.ak4PF = cms.PSet(src=cms.InputTag(jetCollection))
	if (cmssw_version_number.startswith("7_6")):
		process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAll"))
	process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
	process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")


	## ------------------------------------------------------------------------
	## MET
	process.load("Kappa.Skimming.KMET_run2_cff")

	if (not miniaod):
		from Kappa.Skimming.KMET_run2_cff import configureMVAMetForAOD
		configureMVAMetForAOD(process)
		process.kappaTuple.active += cms.vstring('GenMET')                  ## produce/save KappaMET
		process.kappaTuple.active += cms.vstring('MET')                       ## produce/save KappaPFMET and MVA MET
		## Write MVA MET to KMETs. To check what happens on AOD
		process.kappaTuple.active += cms.vstring('PatMETs')
		process.kappaTuple.PatMETs.whitelist = cms.vstring(
		                                                   "metMVAEM",
		                                                   "metMVAET",
		                                                   "metMVAMT",
		                                                   "metMVATT"
		                                                    )
		process.p *= process.makeKappaMET

	if(miniaod):
		from Kappa.Skimming.KMET_run2_cff import configureMVAMetForMiniAOD
		configureMVAMetForMiniAOD(process)

		## Standard MET and GenMet from pat::MET
		process.kappaTuple.active += cms.vstring('PatMET')
		process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag("slimmedMETs"))
		process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"))

		## Write MVA MET to KMETs. To check what happens on AOD
		process.kappaTuple.active += cms.vstring('PatMETs')
		process.kappaTuple.PatMETs.metMVAEM = cms.PSet(src=cms.InputTag("metMVAEM"))
		process.kappaTuple.PatMETs.metMVAET = cms.PSet(src=cms.InputTag("metMVAET"))
		process.kappaTuple.PatMETs.metMVAMT = cms.PSet(src=cms.InputTag("metMVAMT"))
		process.kappaTuple.PatMETs.metMVATT = cms.PSet(src=cms.InputTag("metMVATT"))
		process.load('JetMETCorrections.Configuration.JetCorrectionServices_cff')
		process.p *= (process.makeKappaMET)

		# new MVA MET
		from RecoMET.METPUSubtraction.MVAMETConfiguration_cff import runMVAMET
		runMVAMET( process, jetCollectionPF = jetCollection)
		process.kappaTuple.PatMETs.MVAMET = cms.PSet(src=cms.InputTag("MVAMET", "MVAMET"))
		process.MVAMET.srcLeptons  = cms.VInputTag("slimmedMuons", "slimmedElectrons", "slimmedTaus") # to produce all possible combinations
		process.MVAMET.requireOS = cms.bool(False)

	## ------------------------------------------------------------------------
	## GenJets 
	if not data:
		process.load('PhysicsTools/JetMCAlgos/TauGenJets_cfi')
		process.load('PhysicsTools/JetMCAlgos/TauGenJetsDecayModeSelectorAllHadrons_cfi')
		if(miniaod):
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
	if outputfilename != '':
		process.kappaTuple.outputFile = cms.string('%s'%outputfilename)

	return process

if __name__ == "__main__" or __name__ == "kSkimming_run2_cfg":

	if options.testsuite:
		testPaths = ['/storage/a/berger/kappatest/input', '/nfs/dust/cms/user/jberger/kappatest/input']
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
