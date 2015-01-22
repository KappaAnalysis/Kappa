
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
	process.kappaTuple.active										= cms.vstring('TreeInfo')
	process.kappaTuple.TreeInfo.parameters = cms.PSet(
		dataset						= cms.string(datasetsHelper.getDatasetName(nickname)),
		generator					= cms.string(datasetsHelper.getGenerator(nickname)),
		productionProcess			= cms.string(datasetsHelper.getProcess(nickname)),
		globalTag					= cms.string(globaltag),
		prodCampaignGlobalTag	= cms.string(datasetsHelper.getProductionCampaignGlobalTag(nickname, centerOfMassEnergy)),
		runPeriod					= cms.string(datasetsHelper.getRunPeriod(nickname)),
		kappaTag						= cms.string(kappaTag),
		isEmbedded					= cms.bool(isEmbedded),
		jetMultiplicity			= cms.int32(datasetsHelper.getJetMultiplicity(nickname)),
		centerOfMassEnergy		= cms.int32(centerOfMassEnergy),
		puScenario					= cms.string(datasetsHelper.getPuScenario(nickname, centerOfMassEnergy)),
		isData						= cms.bool(data)
		)


	## ------------------------------------------------------------------------
	# General configuration

	process.kappaTuple.active += cms.vstring('VertexSummary')	## save VertexSummary,
	process.kappaTuple.active += cms.vstring('BeamSpot')		## save Beamspot,
	process.kappaTuple.active += cms.vstring('TriggerObjects')

	if not isEmbedded:
		if data:
			process.kappaTuple.active+= cms.vstring('DataInfo')		## produce Metadata for data,
		else:
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
	
	process.kappaTuple.Info.hltWhitelist = cms.vstring(			## HLT selection
		# https://github.com/cms-analysis/HiggsAnalysis-KITHiggsToTauTau/blob/master/data/triggerTables-2011-2012.txt
		# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauWorkingSummer2013
		# can be tested at http://regexpal.com
		# e
		"^HLT_Ele[0-9]+_CaloIdVT(_CaloIsoT)?_TrkIdT(_TrkIsoT)?_v[0-9]+$",
		"^HLT_Ele[0-9]+_WP[0-9]+_v[0-9]+$",
		# m
		"^HLT_(Iso)?Mu[0-9]+(_eta2p1)?_v[0-9]+$",
		# ee
		"^HLT_Ele[0-9]+_CaloId(L|T)(_TrkIdVL)?_CaloIsoVL(_TrkIdVL)?(_TrkIsoVL)?" +
			"_Ele[0-9]+_CaloId(L|T)(_TrkIdVL)?_CaloIsoVL(_TrkIdVL)?(_TrkIsoVL)?_v[0-9]+$",
		"^HLT_Ele[0-9]+_Ele[0-9]+_CaloId(L|T)_CaloIsoVL(_TrkIdVL_TrkIsoVL)?_v[0-9]+$",
		# mm
		"^HLT_(Double)?Mu[0-9]+(_(Mu|Jet)[0-9]+)?_v[0-9]+$",
		# em
		"^HLT_Mu[0-9]+_(Ele|Photon)[0-9]+_CaloId(L|T|VT)(_CaloIsoVL|_IsoT)?(_TrkIdVL_TrkIsoVL)?_v[0-9]+$",
		# et
		"^HLT_Ele[0-9]+_CaloIdVT(_Calo(IsoRho|Iso)T)?_TrkIdT(_TrkIsoT)?_(Loose|Medium|Tight)IsoPFTau[0-9]+_v[0-9]+$",
		"^HLT_Ele[0-9]+_eta2p1_WP[0-9]+(Rho|NoIso)_LooseIsoPFTau[0-9]+_v[0-9]+$",
		# mt
		"^HLT_(Iso)?Mu[0-9]+(_eta2p1)?_(Loose|Medium|Tight)IsoPFTau[0-9]+(_Trk[0-9]_eta2p1)?_v[0-9]+$",
		# tt
		"^HLT_Double(Medium)?IsoPFTau[0-9]+_Trk(1|5)_eta2p1_(Jet[0-9]+|Prong[0-9])?_v[0-9]+$",
		"^HLT_Double(Medium)?IsoPFTau[0-9]+_Trk(1|5)(_eta2p1)?_v[0-9]+$",
		# specials (possible generalization: Mu15, L1ETM20, Photon20, Ele8)
		"^HLT_Ele[0-9]+_CaloId(L|T|VT)_CaloIso(VL|T|VT)(_TrkIdT)?(_TrkIsoVT)?_(SC|Ele)[0-9](_Mass[0-9]+)?_v[0-9]+$",
		"^HLT_Ele8_v[0-9]+$",
		"^HLT_IsoMu15(_eta2p1)?_L1ETM20_v[0-9]+$",
		"^HLT_Photon20_CaloIdVT_IsoT_Ele8_CaloIdL_CaloIsoVL_v[0-9]+$",
		# specials for tag and probe and em fakerate studies could be added if enough bits are ensured
		#"^HLT_Ele[0-9]+_CaloId(L|T|VT)_CaloIso(VL|T|VT)(_TrkIdT_TrkIso(T|VT))?_(SC|Ele)[0-9]+(_Mass[0-9]+)?_v[0-9]+$",
		#"^HLT_Mu[0-9]+_Photon[0-9]+_CaloIdVT_IsoT_v[0-9]+$",
		#"^HLT_Ele[0-9]+_CaloId(L|T)(_TrkIdVL)?_CaloIsoVL(_TrkIdVL_TrkIsoVL)?(_TrkIsoVL)?(_Jet[0-9]+|)?_v[0-9]+$",
		)
	
	process.kappaTuple.Info.hltBlacklist = cms.vstring(
		"HLT_Mu13_Mu8", # v21 gives errors for the trigger objects
		)

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
	#process.kappaTuple.Electrons.ids = cms.vstring("mvaTrigV050nsCSA14",
						  #"mvaTrigV025nsCSA14",
						  #"mvaNonTrigV050nsCSA14",
						  #"mvaNonTrigV025nsCSA14")
	process.kappaTuple.Electrons.minPt = cms.double(8.0)
	process.p *= process.makeKappaElectrons
	
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
	process.p *= (process.pfiso)

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

	## ------------------------------------------------------------------------
	## KappaJets
	process.load("Kappa.Skimming.KJets_cff")
	process.kappaTuple.active += cms.vstring('Jets')
	process.kappaTuple.Jets = cms.PSet(
		process.kappaNoCut,
		process.kappaNoRegEx,
		taggers = cms.vstring(
	#		"QGlikelihood",
	#		"QGmlp",
			"TrackCountingHighEffBJetTags",
			"TrackCountingHighPurBJetTags",
			"JetProbabilityBJetTags",
			"JetBProbabilityBJetTags",
			"SoftElectronBJetTags",
			"SoftMuonBJetTags",
			"SoftMuonByIP3dBJetTags",
			"SoftMuonByPtBJetTags",
			"SimpleSecondaryVertexBJetTags",
			"CombinedSecondaryVertexBJetTags",
			"CombinedSecondaryVertexMVABJetTags",
			"puJetIDFullDiscriminant",
			"puJetIDFullLoose",
			"puJetIDFullMedium",
			"puJetIDFullTight",
			#"puJetIDCutbasedDiscriminant",
			#"puJetIDCutbasedLoose",
			#"puJetIDCutbasedMedium",
			#"puJetIDCutbasedTight"
			),
		AK5PFTaggedJets = cms.PSet(
			src = cms.InputTag("ak5PFJets"),
			#QGtagger = cms.InputTag("AK5PFJetsQGTagger"),
			QGtagger = cms.InputTag(""),
			Btagger  = cms.InputTag("ak5PF"),
			PUJetID  = cms.InputTag("ak5PFPuJetMva"),
			PUJetID_full = cms.InputTag("full"),
			),
		AK5PFTaggedJetsCHS = cms.PSet(
			src = cms.InputTag("ak5PFJetsCHS"),
			#QGtagger = cms.InputTag("AK5PFJetsCHSQGTagger"),
			QGtagger = cms.InputTag(""),
			Btagger  = cms.InputTag("ak5PFCHS"),
			PUJetID  = cms.InputTag("ak5PFCHSPuJetMva"),
			PUJetID_full = cms.InputTag("full"),
			),
		)
	process.kappaTuple.Jets.minPt = cms.double(10.0)
	process.kappaTuple.active += cms.vstring('PileupDensity')

	## ------------------------------------------------------------------------
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
		process.kappaTuple.Info.isEmbedded = cms.bool(True)

	#Check if working
	# Let Jets run
	process.p *= (
		process.makePFJets *
		process.makePFJetsCHS *
	#	process.makeQGTagging *
		process.makeBTagging *
		process.makePUJetID
	)

	## ------------------------------------------------------------------------
	## MET - not yet supported in CMSSW_7
	#process.load("Kappa.Skimming.KMET_cff")
	#process.kappaTuple.active += cms.vstring('BasicMET')                         ## produce/save KappaMET
	#process.kappaTuple.active += cms.vstring('MET')                       ## produce/save KappaPFMET
	#process.p *= process.makeKappaMET
	
	#Check if working and needed in CMSSW_7
	#process.load('PhysicsTools/JetMCAlgos/TauGenJets_cfi')
	#process.load('PhysicsTools/JetMCAlgos/TauGenJetsDecayModeSelectorAllHadrons_cfi')
	#process.p *= (process.tauGenJets+process.tauGenJetsSelectorAllHadrons)
	#process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets")
	#process.kappaTuple.active += cms.vstring('GenJets')
	#
	## add python config to TreeInfo
	#process.kappaTuple.TreeInfo.parameters.config = cms.string(process.dumpPython())
	#	
	## add repository revisions to TreeInfo
	#for repo, rev in tools.get_repository_revisions().iteritems():
	#		setattr(process.kappaTuple.TreeInfo.parameters, repo, cms.string(rev))
	

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
		process = getBaseConfig(globaltag="START72_V1::All", nickname="SM_VBFHToTauTau_M_125_powheg_pythia_13TeV", testfile=cms.untracked.vstring("file:///nfs/dust/cms/user/fcolombo/VBF_HToTauTau_M-125_13TeV-powheg-pythia6_PU40bx25_PHYS14_25_V1-v1_00E63918-3A70-E411-A246-7845C4FC35F3.root"))

	## for grid-control:
	else:
		process = getBaseConfig("@GLOBALTAG@", nickname="@NICK@", kappaTag="@KAPPA_TAG@")

