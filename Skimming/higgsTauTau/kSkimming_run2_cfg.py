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

# Kappa test: CMSSW 7.2.2
# Kappa test: scram arch slc6_amd64_gcc481
# Kappa test: checkout script scripts/checkoutCmssw72xPackagesForSkimming.py
# Kappa test: output kappaTuple.root

import os
import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.datasetsHelper2015 as datasetsHelper
import Kappa.Skimming.tools as tools


def getBaseConfig( globaltag= 'START70_V7::All',
                   testfile=cms.untracked.vstring(""),
                   maxevents=100, ## -1 = all in file
                   nickname = 'VBFHToTauTauM125_Phys14DR_PU20bx25_13TeV_MINIAODSIM',
                   kappaTag = 'Kappa_2_0_0' ):

	## ------------------------------------------------------------------------
	# Configure Kappa
	from Kappa.Skimming.KSkimming_template_cfg import process

	process.source.fileNames      = testfile
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

	process.kappaTuple.active += cms.vstring('VertexSummary')            # save VertexSummary,
	if miniaod:
		process.kappaTuple.VertexSummary.whitelist = cms.vstring('offlineSlimmedPrimaryVertices')  # save VertexSummary,
		process.kappaTuple.VertexSummary.rename = cms.vstring('offlineSlimmedPrimaryVertices => goodOfflinePrimaryVerticesSummary')  # save VertexSummary,
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
	from Kappa.Skimming.hlt import hltBlacklist, hltWhitelist
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
	process.load("Kappa.Skimming.KMuons_run2_cff")
	process.kappaTuple.active += cms.vstring('Muons')
	if(miniaod):
		process.kappaTuple.Muons.muons.src = cms.InputTag("slimmedMuons")
		process.kappaTuple.Muons.muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.kappaTuple.Muons.muons.srcMuonIsolationPF = cms.InputTag("")
	process.kappaTuple.Muons.minPt = cms.double(8.0)
	if (not miniaod):
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
		process.kappaTuple.Electrons.ids = cms.vstring("egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-miniAOD-standalone-veto",
						"egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-miniAOD-standalone-loose",
						"egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-miniAOD-standalone-medium",
						"egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-miniAOD-standalone-tight")

	if not miniaod:
		process.load("Kappa.Skimming.KElectrons_run2_cff")
		process.kappaTuple.Electrons.minPt = cms.double(8.0)
		from Kappa.Skimming.KElectrons_run2_cff import setupElectrons

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
		process.pfMetMVAEM.srcLeptons = cms.VInputTag("slimmedElectrons", "mvaMETMuons" )
		process.pfMetMVAET.srcLeptons = cms.VInputTag("slimmedElectrons", "slimmedTaus")
		process.pfMetMVAMT.srcLeptons = cms.VInputTag("mvaMETMuons"    , "slimmedTaus")
		process.pfMetMVATT.srcLeptons = cms.VInputTag("slimmedTaus")
		process.pfMetMVAEM.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.pfMetMVAET.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.pfMetMVAMT.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.pfMetMVATT.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.pfMetMVAEM.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.pfMetMVAET.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.pfMetMVAMT.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.pfMetMVATT.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.makeKappaMET = cms.Sequence( process.ak4PFJets * process.calibratedAK4PFJetsForPFMVAMEt * process.mvaMETJets * process.puJetIdForPFMVAMEt * process.mvaMETMuons * process.pfMetMVAEM * process.pfMetMVAET * process.pfMetMVAMT * process.pfMetMVATT )

		## Standard MET and GenMet from pat::MET
		process.kappaTuple.active += cms.vstring('PatMET')


	process.p *= process.makeKappaMET
	## ------------------------------------------------------------------------
	## GenJets 
	if not miniaod:
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

	## ------------------------------------------------------------------------
	## let Kappa run
	process.p *= ( process.kappaOut )

	## ------------------------------------------------------------------------
	## Write out edmFile for debugging perposes 
	#process.load("Kappa.Skimming.edmOut")

	return process

if __name__ == "__main__":
	if("@" in "@NICK@"): # run local skim by hand without replacements by grid-control

		# TauPlusX_Run2012B_22Jan2013_8TeV
		#process = getBaseConfig(globaltag="FT_53_V21_AN4::All", nickname="TauPlusX_Run2012B_22Jan2013_8TeV", testfile=cms.untracked.vstring("root://cms-xrd-global.cern.ch//store/data/Run2012B/TauPlusX/AOD/22Jan2013-v1/20000/0040CF04-8E74-E211-AD0C-00266CFFA344.root"))
		
		# DoubleMu_PFembedded_Run2012A_22Jan2013_mt_8TeV
		#process = getBaseConfig(globaltag="FT_53_V21_AN4::All", nickname="DoubleMu_PFembedded_Run2012A_22Jan2013_mt_8TeV", testfile=cms.untracked.vstring("root://cms-xrd-global.cern.ch//store/results/higgs/DoubleMu/StoreResults-Run2012A_22Jan2013_v1_PFembedded_trans1_tau116_ptmu1_16had1_18_v1-5ef1c0fd428eb740081f19333520fdc8/DoubleMu/USER/StoreResults-Run2012A_22Jan2013_v1_PFembedded_trans1_tau116_ptmu1_16had1_18_v1-5ef1c0fd428eb740081f19333520fdc8/0000/00F5125E-A3E4-E211-A54D-0023AEFDE638.root"))

		# DYJetsToLL_M_50_madgraph_13TeV
		#process = getBaseConfig(globaltag="PHYS14_25_V1::All", nickname="DYJetsToLL_M_50_madgraph_13TeV", testfile=cms.untracked.vstring("root://xrootd.unl.edu//store/mc/Phys14DR/DYJetsToLL_M-50_13TeV-madgraph-pythia8/MINIAODSIM/PU20bx25_PHYS14_25_V1-v1/00000/0432E62A-7A6C-E411-87BB-002590DB92A8.root"))
		
		# SM_VBFHToTauTau_M_125_powheg_pythia_13TeV
		#process = getBaseConfig(globaltag="PHYS14_25_V1::All", nickname="SM_VBFHToTauTau_M_125_powheg_pythia_13TeV", testfile=cms.untracked.vstring("root://xrootd.unl.edu//store/mc/Phys14DR/VBF_HToTauTau_M-125_13TeV-powheg-pythia6/MINIAODSIM/PU20bx25_tsg_PHYS14_25_V1-v2/00000/147B369C-9F77-E411-B99D-00266CF9B184.root"))

		# SM_VBFHToTauTau_M_125_powheg_pythia_13TeV
		#process = getBaseConfig(globaltag="PHYS14_25_V1::All", nickname="SM_VBFHToTauTau_M_125_powheg_pythia_13TeV", testfile=cms.untracked.vstring("file:///nfs/dust/cms/user/fcolombo/VBF_HToTauTau_M-125_13TeV-powheg-pythia6_PU20bx25_tsg_PHYS14_25_V1-v2_0ACE16B2-5677-E411-87FF-7845C4FC3A40.root"))

		# SM_VBFHToTauTau_M_125_powheg_pythia_13TeV MiniAOD
		# Input file for test script
		testPaths = ['/storage/a/berger/kappatest/input', '/nfs/dust/cms/user/jberger/kappatest/input']
		testPath = [p for p in testPaths if os.path.exists(p)][0]
		process = getBaseConfig(globaltag="PHYS14_25_V1::All", nickname="VBFHToTauTauM125_Phys14DR_PU20bx25_13TeV_MINIAODSIM", testfile=cms.untracked.vstring("file://%s/VBF_HToTauTau_Miniaod.root" % testPath))
		#process = getBaseConfig(globaltag="PHYS14_25_V1::All", nickname="VBFHToTauTauM125_Phys14DR_PU20bx25_13TeV_AODSIM", testfile=cms.untracked.vstring("file://%s/VBF_HToTauTau_M-125_13TeV_PHYS14.root" % testPath))

	## for grid-control:
	else:
		process = getBaseConfig("@GLOBALTAG@", nickname="@NICK@", kappaTag="@KAPPA_TAG@")

