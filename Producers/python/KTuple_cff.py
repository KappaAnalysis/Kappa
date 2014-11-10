# Copyright (c) 2010 - All Rights Reserved
#   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
#   Fred Stober <stober@cern.ch>
#   Joram Berger <joram.berger@cern.ch>
#   Manuel Zeise <zeise@cern.ch>
#

import FWCore.ParameterSet.Config as cms

kappaNoCut = cms.PSet(
	maxN = cms.int32(-1),
	minPt = cms.double(-1),
	maxEta = cms.double(-1),
)

kappaNoRename = cms.PSet(
	rename = cms.vstring(),
	rename_whitelist= cms.vstring(),
	rename_blacklist = cms.vstring(),
)

kappaNoRegEx = cms.PSet(kappaNoRename,
	manual = cms.VInputTag(),
	whitelist = cms.vstring(),
	blacklist = cms.vstring(".*"),
)

kappaTupleDefaultsBlock = cms.PSet(
	verbose = cms.int32(0),
	active = cms.vstring("Info"),
	profile = cms.bool(False),

	Info = cms.PSet(
		forceLumi = cms.int32(-1),
		forceXSec = cms.double(1),
		ignoreExtXSec = cms.bool(False),
		genSource = cms.InputTag("generator"),
		lumiSource = cms.InputTag("lumiProducer"),
		pileUpInfoSource = cms.InputTag("addPileupInfo"),
		isEmbedded = cms.bool(False),

		l1Source = cms.InputTag("gtDigis"),
		hltSource = cms.InputTag("TriggerResults"),
		hltWhitelist = cms.vstring(
			# jet trigger
			"^HLT_(PF)?Jet[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
			# 2011 jet trigger
			"^HLT_DiJetAve[0-9]+(U)?(_NoJetID)?(_v[[:digit:]]+)?$",
			# electron triggers
			# muon triggers
			"^HLT_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",  # matches 'HLT_DoubleMu7_v8' etc.
			"^HLT_(Double)?Mu([0-9]+)_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",  # matches 'HLT_Mu17_Mu8_v7' etc.
			# tau trigger
			"^HLT_(Iso)?Mu([0-9]+)_PFTau([0-9]+)(_v[[:digit:]]+)?$",
		),
		hltBlacklist = cms.vstring(
		),
		hltFailToleranceList = cms.vstring(
		),
		printHltList = cms.bool(False),

		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
		noiseHCAL = cms.InputTag("hcalnoise"),

		errorsAndWarnings = cms.InputTag("logErrorHarvester"),
		errorsAndWarningsAvoidCategories = cms.vstring(),
		printErrorsAndWarnings = cms.bool(False),
	),

	TreeInfo = cms.PSet(),

	HCALNoiseSummary = cms.PSet(kappaNoRename,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("hcalnoise"),
		blacklist = cms.vstring(),
	),

	FilterSummary = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("bool_.*Filter"),
		blacklist = cms.vstring(),

		rename = cms.vstring(
			"(.*)Filter => $1",
			"(EcalDeadCellTriggerPrimitive)|(EcalDeadCellBoundaryEnergy)|(ecalLaserCorr)|(eeBadSc)|(eeNoise)|" +
			"(hcalLaserEvent)|(greedyMuonPFCandidate)|(inconsistentMuonPFCandidate)" +
			" => (?1ecalDeadCellTrigger)(?2ecalDeadCellBoundary)(?3ecalLaser)(?4ecalSupercrystal)(?5ecalNoise)" +
			"(?6hcalLaser)(?7muonGreedy)(?8muonInconsistent)",
		),

		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	TriggerObjects = cms.PSet(kappaNoRegEx,
		hltTag = cms.InputTag("hltTriggerSummaryAOD"),
		triggerObjects = cms.vstring(),
	),

	Tracks = cms.PSet(kappaNoRename,
		maxN = cms.int32(-1),
		minPt = cms.double(10.),
		maxEta = cms.double(2.5),

		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoTracks_generalTracks"),
		blacklist = cms.vstring(),
	),

	TrackSummary = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoTracks_generalTracks"),
		blacklist = cms.vstring(),

		rename = cms.vstring("$ => Summary"),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	Vertex = cms.PSet(kappaNoCut, kappaNoRename,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("offlinePrimaryVertices"),
		blacklist = cms.vstring(),
	),

	VertexSummary = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("offlinePrimaryVertices"),
		blacklist = cms.vstring("Vertices(QG|WithBS)"),

		rename = cms.vstring("goodOfflinePrimaryVertices => primaryVertices","$ => Summary"),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	TaupairVerticesMap = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),
		rename = cms.vstring("$ => UnbiasedRefit"),
		whitelist = cms.vstring("offlinePrimaryVertices"),
		blacklist = cms.vstring(),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),

		deltaRThreshold = cms.double(0.0001),
		beamSpotSource = cms.InputTag("offlineBeamSpot"),
		src = cms.InputTag("hpsPFTauProducer"),
		fitMethod = cms.int32(0),
		includeOrginalPV = cms.bool(True),
	),


	BeamSpot = cms.PSet(kappaNoRename,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoBeamSpot.*"),
		blacklist = cms.vstring(""),
	),

	LV = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("reco.*Jets_.*Jet"),
		blacklist = cms.vstring("Castor", "BasicJet"),

		rename = cms.vstring(
			"JetPlusTrack(.*) => $1JPT",
			"(antikt)|(kt)|(siscone)|(iterativecone)|(icone)|(ak)|(ca)([0-9]*) => (?1ak)(?2kt)(?3sc)(?4ic)(?5ic)(?6ak)(?7ca)$8",
			"((L2)(L3)?|(ZSP)(Jet)?)CorJet(..[0-9]*)(PF)?(JPT)?(Calo)? => $6(?3L3:(?2L2))(?4L0)(?7PF)(?8JPT)Jets",
		),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(".*CaloJets", ".*PFJets", ".*JPTJets"),
	),

	Tower = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("towerMaker"),
		blacklist = cms.vstring(),

		rename = cms.vstring("towerMaker => towers"),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),

		srcPVs = cms.InputTag("offlinePrimaryVertices"),
	),

	BasicMET = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("reco(Calo|Gen)MET"),
		blacklist = cms.vstring("recoPFMET"),

		rename = cms.vstring(
			"(gen)?(ht)?met => (?1gen:calo)met(?2Ht)",
		),
		rename_whitelist = cms.vstring("^(Calo|Gen)MET(Calo|True)?$"),
		rename_blacklist = cms.vstring(),
	),

	MET = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFMET"),
		blacklist = cms.vstring(),

		rename = cms.vstring("pfMet => met"),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	GenParticles = cms.PSet(kappaNoCut, kappaNoRegEx,
		genParticles = cms.PSet(
			src = cms.InputTag("genParticles"),
			selectedStatus = cms.int32(0),      # select, if (1<<status & selectedStatus) or selectedStatus==0
			selectedParticles = cms.vint32(),   # empty = all pdgIds possible
		),
		#genStableMuons = cms.PSet(
		#	src = cms.InputTag("genParticles"),
		#	selectedStatus = cms.int32(2),      # select, if (1<<status & selectedStatus) or selectedStatus==0
		#	selectedParticles = cms.vint32(13, -13),   # empty = all pdgIds possible
		#),
	),

	GenPhotons = cms.PSet(kappaNoCut, kappaNoRegEx,
		genPhotons = cms.PSet(
			src = cms.InputTag("genParticles"),
		),
	),

	LHE = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("source"),
		blacklist = cms.vstring(),
		
		rename = cms.vstring("source => LHE"),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	PFCandidates = cms.PSet(kappaNoRename, kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFCandidates_particleFlow"),
		blacklist = cms.vstring(),
	),

	PileupDensity = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("kt6PFJetsRho_rho", "kt6PFJets_rho"),
		blacklist = cms.vstring(),

		rename = cms.vstring("kt6PFJetsRho => KT6AreaRho", "kt6PFJets => KT6Area"),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	Muons = cms.PSet(kappaNoCut, kappaNoRegEx,
		muons = cms.PSet(
			src = cms.InputTag("muons"),
			# track/ecal/hcal iso are directly taken from reco instead...
			#srcMuonIsolationTrack = cms.InputTag("muIsoDepositTk"),
			#srcMuonIsolationEcal = cms.InputTag("muIsoDepositCalByAssociatorTowers","ecal"),
			#srcMuonIsolationHcal = cms.InputTag("muIsoDepositCalByAssociatorTowers","hcal"),
			# Note: Needs to be produced in skimming config, see e.g. skim_MC_36x.py
			srcMuonIsolationPF = cms.InputTag("pfmuIsoDepositPFCandidates"),
			vertexcollection = cms.InputTag("offlinePrimaryVertices"),
			# Cuts for PF isolation
			pfIsoVetoCone = cms.double(0.01),
			pfIsoVetoMinPt = cms.double(0.5),
		),
		muonTriggerObjects = cms.vstring(
			# HLT_MuX (2010)
			"hltSingleMu7L2Filtered5",
			"hltSingleMu7L3Filtered7",
			"hltSingleMu7L3Filtered8",
			"hltSingleMu9L3Filtered9",
			"hltSingleMu11L3Filtered11",
			"hltSingleMu13L3Filtered13",
			"hltSingleMu15L3Filtered15",
			"hltSingleMu17L3Filtered17",
			"hltSingleMu19L3Filtered19",
			"hltSingleMu21L3Filtered21",
			"hltSingleMu21L3Filtered25",

			# HLT_MuX (2011)
			"hltSingleMu12L3Filtered12",
			"hltL3Muon15",					# no kidding, other version above
			"hltSingleMu20L3Filtered20",
			"hltSingleMu24L3Filtered24",
			"hltSingleMu30L3Filtered30",
			"hltSingleMu40L3Filtered40",
			"hltL3fL1sMu16Eta2p1L1f0L2f16QL3Filtered40",
			"hltSingleMuL3Filtered100",

			# HLT_IsoMuX (2010)
			"hltSingleMuIsoL3IsoFiltered9",
			"hltSingleMuIsoL3IsoFiltered11",
			"hltSingleMuIsoL3IsoFiltered13",
			"hltSingleMuIsoL3IsoFiltered15",
			"hltSingleMuIsoL3IsoFiltered17",

			# HLT_IsoMuX (2011)
			"hltSingleMuIsoL3IsoFiltered12",
			#"hltSingleMuIsoL3IsoFiltered15",
			#"hltSingleMuIsoL3IsoFiltered17",
			"hltSingleMuIsoL3IsoFiltered17Eta21",
			"hltSingleMuIsoL3IsoFiltered20Eta21",
			"hltSingleMuIsoL3IsoFiltered24",
			"hltSingleMuIsoL3IsoFiltered30",

			# HLT with quality criteria
			"hltSingleMu24L2QualL3Filtered24",
			"hltSingleMu30L2QualL3Filtered30",
			"hltSingleMu40L2QualL3Filtered40",
			"hltSingleMuL2QualIsoL3IsoFiltered17",
			"hltSingleMuL2QualIsoL3IsoFiltered20",
			"hltSingleMuL2QualIsoL3IsoFiltered24",

			# HLT_DoubleMu (2010+2011)
			"hltL1sL1DoubleMuOpen",
			"hltL1sL1DoubleMu0",
			"hltL1sL1DoubleMu3",
			"hltDiMuonL3PreFiltered0",
			"hltDiMuonL3PreFiltered",
			"hltDiMuonL3PreFiltered3",
			"hltDiMuonL3PreFiltered4",
			"hltDiMuonL3PreFiltered5",
			"hltDiMuonL3PreFiltered6",
			"hltDiMuonL3PreFiltered7",
			"hltDiMuonL3PreFiltered8",
			"hltDiMuonL3PreFiltered45",
			"hltDoubleMu4ExclL3PreFiltered",
			"hltDoubleMu5ExclL3PreFiltered",
			"hltDoubleMu6ExclL3PreFiltered",

			# andere
			"hltSingleMu3L3Filtered3",
			"hltSingleMu5L3Filtered5",
			"hltSingleMuIsoL3IsoFiltered3",

			# Objekte aus DoubleMu
			"hltSingleMu13L3Filtered17",
			"hltDiL3fL1sDoubleMu3p5L1f0L2f0L3Filtered45",
			"hltDiMuonL3p5PreFiltered8",
			"hltDiMuonL3PreFiltered5Eta2p15",
			"hltL1DoubleMu3L3TriMuFiltered5",
			"hltL2DoubleMu23NoVertexL2PreFiltered",
			"hltL2DoubleMu30NoVertexL2PreFiltered",
			"hltL2DoubleMu35NoVertexL2PreFiltered",
			"hltL3fL1sDiMu3p5L1f3p5L2f3p5L3f6",
			"hltL3Mu8Jet20L3Filtered8",
			"hltSingleL2MuOpenL2PreFilteredNoVtx",
		),
		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
		hltMaxdR = cms.double(0.2),
		hltMaxdPt_Pt = cms.double(1.),
		noPropagation = cms.bool(False),

		useSimpleGeometry = cms.bool(True),
		useTrack = cms.string("tracker"),
		useState = cms.string("atVertex"),
	),

	L1Muons = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring(
			"l1extraL1MuonParticles_l1extraParticles",
			"l1extraL1MuonParticles_hltL1extraParticles",
			),
		blacklist = cms.vstring(),

		rename = cms.vstring(
			"hltL1extraParticles => l1muons",
			"l1extraParticles => l1muons",
		),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	Electrons = cms.PSet(kappaNoCut,
		kappaNoRegEx,
		ids = cms.vstring(),
		electrons = cms.PSet(
			src = cms.InputTag("patElectrons"),
			allConversions = cms.InputTag("allConversions"),
			offlineBeamSpot = cms.InputTag("offlineBeamSpot"),
			vertexcollection = cms.InputTag("goodOfflinePrimaryVertices"),
			isoValInputTags = cms.VInputTag(
				cms.InputTag('elPFIsoValueCharged03PFIdPFIso'),
				cms.InputTag('elPFIsoValueGamma03PFIdPFIso'),
				cms.InputTag('elPFIsoValueNeutral03PFIdPFIso')),
			rhoIsoInputTag = cms.InputTag("kt6PFJetsForIsolation", "rho"),
		),
	),

	BasicJets = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFJets_ak5PFJets.*"),
		blacklist = cms.vstring(".*Tau.*", "recoPFJets_pfJets.*kappaSkim", "Jets(Iso)?QG"),

		rename = cms.vstring(
			"(antikt)|(kt)|(siscone)|(iterativecone)|(icone)|(ak)|(ca)([0-9]*) => (?1ak)(?2kt)(?3sc)(?4ic)(?5ic)(?6ak)(?7ca)$8"
		),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	GenTaus = cms.PSet(kappaNoCut, kappaNoRegEx,
		genTaus = cms.PSet(
			src = cms.InputTag("genParticles"),
			selectedStatus = cms.int32(0)       # select, if (1<<status & selectedStatus) or selectedStatus==0
		)
	),

	Taus = cms.PSet(kappaNoCut, kappaNoRegEx,
		#shrinkingConePFTaus = cms.PSet(
		#	src = cms.InputTag("shrinkingConePFTauProducer"),
		#	discrWhitelist = cms.vstring("shrinkingConePFTau*"),
		#	discrBlacklist = cms.vstring(".*PFlow$"),
		#),
		#fixedConePFTaus = cms.PSet(
		#	src = cms.InputTag("fixedConePFTauProducer"),
		#	discr = cms.vstring("fixedConePFTau*")
		#),
		taus = cms.PSet(
			src = cms.InputTag("hpsPFTauProducer"),
			preselectOnDiscriminators = cms.vstring("hpsPFTauDiscriminationByDecayModeFinding"), # no regex here!
			binaryDiscrWhitelist = cms.vstring("hpsPFTau.*"),
			binaryDiscrBlacklist = cms.vstring("^shrinkingCone.*", ".*PFlow$", "raw", "Raw"),
			floatDiscrWhitelist = cms.vstring("hpsPFTau.*raw.*", "hpsPFTau.*Raw.*"),
			floatDiscrBlacklist = cms.vstring("^shrinkingCone.*", ".*PFlow$"),
			tauDiscrProcessName = cms.string("KAPPA"),
		),
	),

	L2MuonTrajectorySeed = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),
		whitelist = cms.vstring("hltL2MuonSeeds"),
		blacklist = cms.vstring(),

		rename = cms.vstring(),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	L3MuonTrajectorySeed = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),
		whitelist = cms.vstring("hltL3TrajectorySeed"),
		blacklist = cms.vstring("hltL3TrajectorySeedNoVtx"),

		rename = cms.vstring(),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	MuonTriggerCandidates = cms.PSet(kappaNoCut, kappaNoRegEx,
		l2muon = cms.PSet(
			src = cms.InputTag("hltL2MuonCandidates"),
			srcIsolation = cms.InputTag("hltL2MuonIsolations"),
			isoDeltaR = cms.double(0.24),
		),
		l3muon = cms.PSet(
			src = cms.InputTag("hltL3MuonCandidates"),
			srcIsolation = cms.InputTag("hltL3MuonIsolations"),
			isoDeltaR = cms.double(0.24),
		),
	),
)
