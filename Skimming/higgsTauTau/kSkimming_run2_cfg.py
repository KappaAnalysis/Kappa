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

# Kappa test: CMSSW 7.2.2, 7.4.6_patch6
# Kappa test: scram arch slc6_amd64_gcc481, slc6_amd64_gcc491
# Kappa test: checkout script scripts/checkoutCmssw72xPackagesForSkimming.py, scripts/checkoutCmssw74xPackagesForSkimming.py
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
options.parseArguments()

cmssw_version_number = tools.get_cmssw_version_number()

def getBaseConfig( globaltag= 'START70_V7::All',
                   testfile=cms.untracked.vstring(""),
                   maxevents=100, ## -1 = all in file
                   nickname = 'VBFHToTauTauM125_Phys14DR_PU20bx25_13TeV_MINIAODSIM',
                   kappaTag = 'Kappa_2_0_0',
				   outputfilename = ''):

	## ------------------------------------------------------------------------
	# Configure Kappa
	from Kappa.Skimming.KSkimming_template_cfg import process

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
	process.load("Kappa.Skimming.customJECs_cff")
	if data:
		process.jec.toGet = cms.VPSet(
			cms.PSet(
			record = cms.string('JetCorrectionsRecord'),
			tag = cms.string('JetCorrectorParametersCollection_Summer15_50nsV4_DATA_AK4PF'),
			label  = cms.untracked.string('AK4PF'))
			)
		process.jec.connect = cms.string('sqlite:Summer15_50nsV4_DATA.db')

	process.kappaTuple.active += cms.vstring('VertexSummary')            # save VertexSummary,
	if miniaod:
		process.load("Kappa.Skimming.KVertices_cff")
		process.goodOfflinePrimaryVertices.src = cms.InputTag('offlineSlimmedPrimaryVertices')
		process.p *= ( process.makeVertexes )
		if (cmssw_version_number.startswith("7_4")):
			process.kappaTuple.VertexSummary.whitelist = cms.vstring('offlineSlimmedPrimaryVertices')  # save VertexSummary,
			process.kappaTuple.VertexSummary.rename = cms.vstring('offlineSlimmedPrimaryVertices => goodOfflinePrimaryVerticesSummary')
		else:
			process.kappaTuple.VertexSummary.whitelist = cms.vstring('goodOfflinePrimaryVertices')  # save VertexSummary,

		process.kappaTuple.active += cms.vstring('TriggerObjectStandalone')

	process.kappaTuple.active += cms.vstring('BeamSpot')                 # save Beamspot,

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

		if (cmssw_version_number.startswith("7_4")):
			process.kappaTuple.Electrons.ids = cms.vstring("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-veto",
						"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-loose",
						"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-medium",
						"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-tight",
						"electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values")
		else:
			process.kappaTuple.Electrons.ids = cms.vstring("egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-miniAOD-standalone-veto",
						"egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-miniAOD-standalone-loose",
						"egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-miniAOD-standalone-medium",
						"egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-miniAOD-standalone-tight")

	if not miniaod:
		process.load("Kappa.Skimming.KElectrons_run2_cff")
		process.kappaTuple.Electrons.minPt = cms.double(8.0)
		from Kappa.Skimming.KElectrons_run2_cff import setupElectrons

		if (cmssw_version_number.startswith("7_4")):
			process.kappaTuple.Electrons.ids = cms.vstring("cutBasedEleIdPHYS14Loose",
							       	   "cutBasedEleIdPHYS14Medium",
							       	   "cutBasedEleIdPHYS14Tight",
							       	   "cutBasedEleIdPHYS14Veto",
								   "mvaNonTrig25nsPHYS14")
		else:
			process.kappaTuple.Electrons.ids = cms.vstring("cutBasedEleIdPHYS14Loose",
							       	   "cutBasedEleIdPHYS14Medium",
							       	   "cutBasedEleIdPHYS14Tight",
							       	   "cutBasedEleIdPHYS14Veto",
							       	   "mvaTrigV050nsCSA14",
							       	   "mvaTrigV025nsCSA14",
							       	   "mvaNonTrigV050nsCSA14",
							       	   "mvaNonTrigV025nsCSA14",
						       		   "mvaNonTrigV025nsPHYS14")

	setupElectrons(process)
	process.p *= ( process.makeKappaElectrons )
	## ------------------------------------------------------------------------
	if(miniaod):
		process.kappaTuple.active += cms.vstring('PatTaus')
		#process.kappaTuple.PATTaus.taus.binaryDiscrBlacklist = cms.vstring("^shrinkingCone.*", ".*PFlow$", ".*raw.*", ".*Raw.*", "^hpsPFTauDiscriminationByVLoose.*", "^hpsPFTauDiscriminationByVTight.*", "^hpsPFTauDiscriminationByMedium.*")
		process.kappaTuple.PatTaus.taus.preselectOnDiscriminators = cms.vstring()
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
			process.makePFJets *
			process.makePFJetsCHS *
		#	process.makeQGTagging *
			process.makeBTagging *
			process.makePUJetID *
			process.kt6PFJets
		)

	if miniaod:
		process.kappaTuple.active += cms.vstring('PatJets')
		process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
		process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")


	## ------------------------------------------------------------------------
	## MET
	process.load("Kappa.Skimming.KMET_run2_cff")
	process.kappaTuple.active += cms.vstring('MET')                       ## produce/save KappaPFMET and MVA MET

	if (not miniaod):
		process.kappaTuple.active += cms.vstring('BasicMET')                  ## produce/save KappaMET

	if(miniaod):
		process.ak4PFJets.src = cms.InputTag("packedPFCandidates")
		process.pfMetMVA.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.puJetIdForPFMVAMEt.jec =  cms.string('AK4PF')
		process.puJetIdForPFMVAMEt.vertexes = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.puJetIdForPFMVAMEt.rho = cms.InputTag("fixedGridRhoFastjetAll")
		process.mvaMETMuons.src = cms.InputTag("slimmedMuons")
		# process.mvaMETElectrons.src = cms.InputTag("slimmedElectrons")
		# Todo for miniAOD: find a selector that works in pat Taus and slimmedElectrons
		process.metMVAEM.srcLeptons = cms.VInputTag("slimmedElectrons", "slimmedMuons" )
		process.metMVAET.srcLeptons = cms.VInputTag("slimmedElectrons", "slimmedTaus")
		process.metMVAMT.srcLeptons = cms.VInputTag("slimmedMuons"    , "slimmedTaus")
		process.metMVATT.srcLeptons = cms.VInputTag("slimmedTaus"     , "slimmedTaus")
		process.metMVAEM.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.metMVAET.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.metMVAMT.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.metMVATT.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.metMVAEM.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.metMVAET.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.metMVAMT.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.metMVATT.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.makeKappaMET = cms.Sequence( 
		                process.ak4PFJets * 
		                process.calibratedAK4PFJetsForPFMVAMEt * 
		                process.mvaMETJets * 
		                process.puJetIdForPFMVAMEt * 
		                process.mvaMETMuons * 
		                process.metMVAEM * 
		                process.metMVAET * 
		                process.metMVAMT * 
		                process.metMVATT )

		## Standard MET and GenMet from pat::MET
		process.kappaTuple.active += cms.vstring('PatMET')
		## Write MVA MET to KMETs. To check what happens on AOD
		process.kappaTuple.active += cms.vstring('PatMETs')
		process.kappaTuple.PatMETs.whitelist = cms.vstring(
		                                                   "metMVAEM",
		                                                   "metMVAET",
		                                                   "metMVAMT",
		                                                   "metMVATT"
		                                                    )


	process.p *= process.makeKappaMET
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

	## ------------------------------------------------------------------------
	## Further information saved to Kappa output 
	# add python config to TreeInfo
	process.kappaTuple.TreeInfo.parameters.config = cms.string(process.dumpPython())

	# add repository revisions to TreeInfo
	for repo, rev in tools.get_repository_revisions().iteritems():
			setattr(process.kappaTuple.TreeInfo.parameters, repo, cms.string(rev))

	## if needed adapt output filename
	if outputfilename != '':
		process.kappaTuple.outputFile = cms.string('%s'%outputfilename)

	## ------------------------------------------------------------------------
	## let Kappa run
	process.p *= ( process.kappaOut )

	## ------------------------------------------------------------------------
	## Write out edmFile for debugging perposes 
	#process.load("Kappa.Skimming.edmOut")

	return process

if __name__ == "__main__" or __name__ == "kSkimming_run2_cfg":
	if options.testfile:
		process = getBaseConfig(options.globalTag, nickname=options.nickname, kappaTag=options.kappaTag, testfile=cms.untracked.vstring("file://%s"%options.testfile), maxevents=options.maxevents)
	else:
		if options.outputfilename:
			process = getBaseConfig(options.globalTag, nickname=options.nickname, kappaTag=options.kappaTag, maxevents=options.maxevents, outputfilename=options.outputfilename)
		else:
			process = getBaseConfig(options.globalTag, nickname=options.nickname, kappaTag=options.kappaTag, maxevents=options.maxevents)
