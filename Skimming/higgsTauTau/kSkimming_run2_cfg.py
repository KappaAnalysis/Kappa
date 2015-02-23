#-# Copyright (c) 2014 - All Rights Reserved
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>
#-#   Stefan Wayand <stefan.wayand@gmail.com>
#-#   Thomas Mueller <tmuller@cern.ch>
#-#   Yasmin Anstruther <yasmin.anstruther@kit.edu>

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.datasetsHelper as datasetsHelper
import Kappa.Skimming.tools as tools


def getBaseConfig(globaltag= 'START70_V7::All', testfile=cms.untracked.vstring(""), maxevents=100, nickname = 'SM_VBFHToTauTau_M_90_powheg_pythia_8TeV', kappaTag = 'Kappa_1_0_0'):

	from Kappa.Skimming.KSkimming_template_cfg import process
	process.source.fileNames      = testfile
	process.maxEvents.input	      = maxevents				## number of events to be processed (-1 = all in file)
	process.kappaTuple.outputFile = 'kappaTuple.root'			## name of output file
	process.kappaTuple.verbose    = cms.int32(0)				## verbosity level
	process.kappaTuple.profile    = cms.bool(True)
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag   = globaltag
		print "GT (overwritten):", process.GlobalTag.globaltag
	data = datasetsHelper.isData(nickname)
	centerOfMassEnergy = datasetsHelper.getCenterOfMassEnergy(nickname)
	isEmbedded = datasetsHelper.getIsEmbedded(nickname)
	
	process.p = cms.Path ( )
	## ------------------------------------------------------------------------
	# Configure Metadata describing the file
	process.kappaTuple.active = cms.vstring('TreeInfo')
	process.kappaTuple.TreeInfo.parameters = datasetsHelper.getTreeInfo(nickname, globaltag, kappaTag)


	## ------------------------------------------------------------------------
	# General configuration

	process.kappaTuple.active += cms.vstring('VertexSummary')	## save VertexSummary,
	process.kappaTuple.active += cms.vstring('BeamSpot')		## save Beamspot,
	process.kappaTuple.active += cms.vstring('TriggerObjects')

	if not isEmbedded and data:
			process.kappaTuple.active+= cms.vstring('DataInfo')		## produce Metadata for data,

	if not isEmbedded and not data:
			process.kappaTuple.active+= cms.vstring('GenInfo')		## produce Metadata for MC,
			process.kappaTuple.active+= cms.vstring('GenParticles')		## save GenParticles,
			process.kappaTuple.active+= cms.vstring('GenTaus')				## save GenParticles,
	
	# prune GenParticles
	if not data and not isEmbedded:
		process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
		process.prunedGenParticles = cms.EDProducer("GenParticlePruner",
			src = cms.InputTag("genParticles", "", "SIM"),
			select = cms.vstring(
				"drop  *",
				"keep status == 3",  # all status 3
				"keep++ abs(pdgId) == 23", # Z
				"keep++ abs(pdgId) == 24", # W
				"keep++ abs(pdgId) == 25", # H
				"keep abs(pdgId) == 11 || abs(pdgId) == 13",  # charged leptons
				"keep++ abs(pdgId) == 15"  # keep full tau decay chain
			)
		)
	
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
		process.kappaTuple.active+= cms.vstring('DataInfo')
		process.kappaTuple.active+= cms.vstring('GenParticles')		## save GenParticles,
		process.kappaTuple.active+= cms.vstring('GenTaus')				## save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("genParticles","","EmbeddedRECO")

	from Kappa.Skimming.hlt import hltBlacklist, hltWhitelist
	 
	process.kappaTuple.Info.hltWhitelist = hltWhitelist
	
	process.kappaTuple.Info.hltBlacklist = hltBlacklist

	## ------------------------------------------------------------------------
	# Configure PFCandidates and offline PV
	# PFCandidates ------------------------------------------------------------
	process.load("Kappa.Skimming.KPFCandidates_cff")
	# Modifications for new particleFlow Pointers
	process.pfPileUp.PFCandidates = cms.InputTag("particleFlowPtrs")
	process.pfPileUpIso.PFCandidates = cms.InputTag("particleFlowPtrs")
	process.pfNoPileUp.bottomCollection = cms.InputTag("particleFlowPtrs")
	process.pfNoPileUpIso.bottomCollection = cms.InputTag("particleFlowPtrs")
	process.pfJetTracksAssociatorAtVertex.jets= cms.InputTag("ak5PFJets")

	#process.kappaTuple.active += cms.vstring('PFCandidates')		## save PFCandidates for deltaBeta corrected
	process.kappaTuple.PFCandidates.whitelist = cms.vstring(                ## isolation used for electrons and muons.
##		"pfNoPileUpChargedHadrons",    ## switch to pfAllChargedParticles
		"pfAllChargedParticles",       ## same as pfNoPileUpChargedHadrons +pf_electrons + pf_muons
		"pfNoPileUpNeutralHadrons",
		"pfNoPileUpPhotons",
		"pfPileUpChargedHadrons",
		)

	#process.p *= ( process.makePFBRECO * process.makePFCandidatesForDeltaBeta )
	process.p *= ( process.makeKappaPFCandidates)

	## ------------------------------------------------------------------------
	# Configure Muons
	process.load("Kappa.Skimming.KMuons_cff")
	process.kappaTuple.active += cms.vstring('Muons')	                ## produce/save KappaMuons
	process.kappaTuple.Muons.minPt = cms.double(8.0)
	process.p *= process.makeKappaMuons
	
	## for muon iso
	# https://github.com/ajgilbert/ICHiggsTauTau/blob/master/test/higgstautau_new_cfg.py#L430-L460
	process.load("CommonTools.ParticleFlow.Isolation.pfMuonIsolation_cff")
	process.muPFIsoValueCharged04PFIso = process.muPFIsoValueCharged04.clone()
	process.muPFIsoValueChargedAll04PFIso = process.muPFIsoValueChargedAll04.clone()
	process.muPFIsoValueGamma04PFIso = process.muPFIsoValueGamma04.clone()
	process.muPFIsoValueNeutral04PFIso = process.muPFIsoValueNeutral04.clone()
	process.muPFIsoValuePU04PFIso = process.muPFIsoValuePU04.clone()
	
	process.muonPFIsolationValuesSequence = cms.Sequence(
		process.muPFIsoValueCharged04PFIso+
		process.muPFIsoValueChargedAll04PFIso+
		process.muPFIsoValueGamma04PFIso+
		process.muPFIsoValueNeutral04PFIso+
		process.muPFIsoValuePU04PFIso
	)
	process.muPFIsoDepositCharged.src = cms.InputTag("muons")
	process.muPFIsoDepositChargedAll.src = cms.InputTag("muons")
	process.muPFIsoDepositNeutral.src = cms.InputTag("muons")
	process.muPFIsoDepositGamma.src = cms.InputTag("muons")
	process.muPFIsoDepositPU.src = cms.InputTag("muons")

	## ------------------------------------------------------------------------
	# Configure Electrons
	process.load("Kappa.Skimming.KElectrons_run2_cff")
	process.kappaTuple.active += cms.vstring('Electrons')	                ## produce/save KappaElectrons,
	process.kappaTuple.Electrons.ids = cms.vstring("cutBasedEleIdPHYS14Loose",
						       "cutBasedEleIdPHYS14Medium",
						       "cutBasedEleIdPHYS14Tight",
						       "cutBasedEleIdPHYS14Veto",
						       "mvaTrigV050nsCSA14",
						       "mvaTrigV025nsCSA14",
						       "mvaNonTrigV050nsCSA14",
						       "mvaNonTrigV025nsCSA14",
						       "mvaNonTrigV025nsPHYS14")
	process.kappaTuple.Electrons.minPt = cms.double(8.0)

	## for the Run 2 cutBased Id
	# https://github.com/ikrav/ElectronWork/blob/master/ElectronNtupler/test/runIdDemoPrePHYS14AOD.py#L29-L56
	from PhysicsTools.SelectorUtils.tools.vid_id_tools import setupAllVIDIdsInModule, setupVIDElectronSelection 
	from PhysicsTools.SelectorUtils.centralIDRegistry import central_id_registry
	process.load("RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cfi")
	process.egmGsfElectronIDSequence = cms.Sequence(process.egmGsfElectronIDs)
	# Define which IDs we want to produce
	# Each of these IDs contains all four standard cut-based ID working points 
	my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_PHYS14_PU20bx25_V1_cff']
	for idmod in my_id_modules:
		setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)

	process.p *= (
		process.egmGsfElectronIDSequence *
		process.makeKappaElectrons
	)

	## for electron iso
	# https://github.com/ajgilbert/ICHiggsTauTau/blob/master/test/higgstautau_new_cfg.py#L349-L384
	process.load("CommonTools.ParticleFlow.Isolation.pfElectronIsolation_cff")
	process.elPFIsoValueCharged04PFIdPFIso = process.elPFIsoValueCharged04PFId.clone()
	process.elPFIsoValueChargedAll04PFIdPFIso = process.elPFIsoValueChargedAll04PFId.clone()
	process.elPFIsoValueGamma04PFIdPFIso = process.elPFIsoValueGamma04PFId.clone()
	process.elPFIsoValueNeutral04PFIdPFIso = process.elPFIsoValueNeutral04PFId.clone()
	process.elPFIsoValuePU04PFIdPFIso = process.elPFIsoValuePU04PFId.clone()
	
	process.elPFIsoValueGamma04PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.08)','EcalBarrel:ConeVeto(0.08)'))
	process.elPFIsoValueNeutral04PFIdPFIso.deposits[0].vetos = (cms.vstring())
	process.elPFIsoValuePU04PFIdPFIso.deposits[0].vetos = (cms.vstring())
	process.elPFIsoValueCharged04PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.015)'))
	process.elPFIsoValueChargedAll04PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.015)','EcalBarrel:ConeVeto(0.01)'))
	
	process.electronPFIsolationValuesSequence = cms.Sequence(
		process.elPFIsoValueCharged04PFIdPFIso+
		process.elPFIsoValueChargedAll04PFIdPFIso+
		process.elPFIsoValueGamma04PFIdPFIso+
		process.elPFIsoValueNeutral04PFIdPFIso+
		process.elPFIsoValuePU04PFIdPFIso
	)
	process.elPFIsoDepositCharged.src = cms.InputTag("patElectrons")
	process.elPFIsoDepositChargedAll.src = cms.InputTag("patElectrons")
	process.elPFIsoDepositNeutral.src = cms.InputTag("patElectrons")
	process.elPFIsoDepositGamma.src = cms.InputTag("patElectrons")
	process.elPFIsoDepositPU.src = cms.InputTag("patElectrons")

	# electron/muon PF iso sequence
	process.pfiso = cms.Sequence(
		process.muonPFIsolationDepositsSequence +
		process.muonPFIsolationValuesSequence +
		process.electronPFIsolationDepositsSequence +
		process.electronPFIsolationValuesSequence
	)

	# rho for electron iso
        from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
        process.kt6PFJetsForIsolation = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
        process.kt6PFJetsForIsolation.Rho_EtaMax = cms.double(2.5)
        process.p *= (process.pfiso * process.kt6PFJetsForIsolation)

	## ------------------------------------------------------------------------
	# Configure Taus
	process.load("Kappa.Skimming.KTaus_run2_cff")
	process.kappaTuple.active += cms.vstring('Taus')	                ## produce/save KappaTaus
	process.kappaTuple.Taus.minPt = cms.double(8.0)
	process.p *= process.makeKappaTaus

	# Reduced number of Tau discriminators
	# The blacklist is to some degree arbitrary to get below 64 binaty tau discriminators
	# - they may need to be changed as soon as 'official' discriminators for TauID 2014 will be published
	process.kappaTuple.Taus.taus.binaryDiscrBlacklist = cms.vstring("^shrinkingCone.*", ".*PFlow$", ".*raw.*", ".*Raw.*", "^hpsPFTauDiscriminationByVLoose.*", "^hpsPFTauDiscriminationByVTight.*", "^hpsPFTauDiscriminationByMedium.*")
	process.kappaTuple.Taus.taus.preselectOnDiscriminators = cms.vstring("hpsPFTauDiscriminationByDecayModeFindingNewDMs")

	## ------------------------------------------------------------------------
	## KappaJets
	process.load("Kappa.Skimming.KJets_run2_cff")
	process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')
	process.kappaTuple.Jets = process.kappaTupleJets
	process.kappaTuple.Jets.minPt = cms.double(10.0)

	## ------------------------------------------------------------------------

	# add kt6PFJets, needed for the PileupDensity
	from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
	process.kt6PFJets = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
	process.kt6PFJets.Rho_EtaMax = cms.double(2.5)

	#Check if working
	# Let Jets run
	process.p *= (
		process.makePFJets *
		process.makePFJetsCHS *
	#	process.makeQGTagging *
		process.makeBTagging *
		process.makePUJetID *
		process.kt6PFJets
	)

	## ------------------------------------------------------------------------
	## MET
	#process.load("Kappa.Skimming.KMET_run2_cff")
	#process.kappaTuple.active += cms.vstring('BasicMET')                  ## produce/save KappaMET
	#process.kappaTuple.active += cms.vstring('MET')                       ## produce/save KappaPFMET
	#process.p *= process.makeKappaMET
	
	if not data:
		process.load('PhysicsTools/JetMCAlgos/TauGenJets_cfi')
		process.load('PhysicsTools/JetMCAlgos/TauGenJetsDecayModeSelectorAllHadrons_cfi')
		process.p *= (process.tauGenJets+process.tauGenJetsSelectorAllHadrons)
		process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets")
		process.kappaTuple.active += cms.vstring('GenJets')
	
	# add python config to TreeInfo
	process.kappaTuple.TreeInfo.parameters.config = cms.string(process.dumpPython())
		
	# add repository revisions to TreeInfo
	for repo, rev in tools.get_repository_revisions().iteritems():
			setattr(process.kappaTuple.TreeInfo.parameters, repo, cms.string(rev))
	

	## ------------------------------------------------------------------------
	## And let it run
	process.p *= (
		process.kappaOut
	)
	## ------------------------------------------------------------------------
	## declare edm OutputModule (expects a path 'p'), uncommented if wanted

	#process.edmOut = cms.OutputModule(
		#"PoolOutputModule",
		#fileName = cms.untracked.string('dump.root'),				## name of output file
		#SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),	## save only events passing the full path
		#outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')	## save each edm object that has been produced by process KAPPA
		#)
	#process.ep = cms.EndPath(process.edmOut)

	return process

if __name__ == "__main__":
	if("@" in "@NICK@"): # run local skim by hand without replacements by grid-control

		# TauPlusX_Run2012B_22Jan2013_8TeV
		#process = getBaseConfig(globaltag="FT_53_V21_AN4::All", nickname="TauPlusX_Run2012B_22Jan2013_8TeV", testfile=cms.untracked.vstring("root://cms-xrd-global.cern.ch//store/data/Run2012B/TauPlusX/AOD/22Jan2013-v1/20000/0040CF04-8E74-E211-AD0C-00266CFFA344.root"))
		
		# DoubleMu_PFembedded_Run2012A_22Jan2013_mt_8TeV
		#process = getBaseConfig(globaltag="FT_53_V21_AN4::All", nickname="DoubleMu_PFembedded_Run2012A_22Jan2013_mt_8TeV", testfile=cms.untracked.vstring("root://cms-xrd-global.cern.ch//store/results/higgs/DoubleMu/StoreResults-Run2012A_22Jan2013_v1_PFembedded_trans1_tau116_ptmu1_16had1_18_v1-5ef1c0fd428eb740081f19333520fdc8/DoubleMu/USER/StoreResults-Run2012A_22Jan2013_v1_PFembedded_trans1_tau116_ptmu1_16had1_18_v1-5ef1c0fd428eb740081f19333520fdc8/0000/00F5125E-A3E4-E211-A54D-0023AEFDE638.root"))

		# DYJetsToLL_M_50_madgraph_8TeV
		#process = getBaseConfig(globaltag="START53_V15A::All", nickname="DYJetsToLL_M_50_madgraph_8TeV", testfile=cms.untracked.vstring("root://cms-xrd-global.cern.ch//store/mc/Summer12_DR53X/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/AODSIM/PU_S10_START53_V7A-v1/0000/00037C53-AAD1-E111-B1BE-003048D45F38.root"))
		
		# SM_VBFHToTauTau_M_125_powheg_pythia_8TeV
		#process = getBaseConfig(globaltag="START53_V15A::All", nickname="SM_VBFHToTauTau_M_125_powheg_pythia_8TeV", testfile=cms.untracked.vstring("root://cms-xrd-global.cern.ch//store/mc/Summer12_DR53X/VBF_HToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/004B56D8-AAED-E111-AB70-1CC1DE1CEDB2.root"))

		# SM_VBFHToTauTau_M_125_powheg_pythia_13TeV
		process = getBaseConfig(globaltag="PHYS14_25_V1::All", nickname="SM_VBFHToTauTau_M_125_powheg_pythia_13TeV", testfile=cms.untracked.vstring("file:///nfs/dust/cms/user/fcolombo/VBF_HToTauTau_M-125_13TeV-powheg-pythia6_PU20bx25_tsg_PHYS14_25_V1-v2_0ACE16B2-5677-E411-87FF-7845C4FC3A40.root"))

	## for grid-control:
	else:
		process = getBaseConfig("@GLOBALTAG@", nickname="@NICK@", kappaTag="@KAPPA_TAG@")

