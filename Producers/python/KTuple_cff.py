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
	active = cms.vstring("Metadata"),

	Metadata = cms.PSet(
		forceLumi = cms.int32(-1),
		ignoreExtXSec = cms.bool(False),
		genSource = cms.InputTag("generator"),

		l1Source = cms.InputTag("gtDigis"),
		hltSource = cms.InputTag("TriggerResults"),
		hltWhitelist = cms.vstring(
			".*Jet.*",
			"^HLT_(L[123])?(Iso|Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",
			".*(Bias|BSC).*",
			"^HLT_MET[0-9]*",
			"^HLT_(Iso)?Mu([0-9]+)_PFTau([0-9]+)(_v[[:digit:]]+)?$",
		),
		hltBlacklist = cms.vstring(
			".*AlCa.*",
			"^HLT_BTagMu_.*",
			".*ForwardBackward.*",
			".*L1Tech.*",
			"^HLT_Mu([0357])(_v[[:digit:]]+)?$",
			"^HLT_MET[0-9]*_.*Jet.*",
			"^HLT_Mu([0-9]+)_Jet([0-9]+).*",
		),
		printHltList = cms.bool(True),

		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
		muonTriggerObjects = cms.vstring(
			# HLT_Mu7
			"hltL1sL1SingleMu5",
			"hltL1SingleMu5L1Filtered0",
			"hltSingleMu7L2Filtered5",
			"hltSingleMu7L3Filtered7",
			# HLT_Mu9
			"hltSingleMu9L3Filtered9",
			# path HLT_Mu11
			"hltSingleMu11L3Filtered11",
			# path HLT_Mu13_v1
			"hltSingleMu13L3Filtered13",
			# HLT_Mu15_v1
			"hltSingleMu15L3Filtered15",
			# HLT_Mu17_v1
			"hltSingleMu17L3Filtered17",
			# HLT_Mu19_v1
			"hltSingleMu19L3Filtered19",
			# HLT_Mu21_v1
			"hltSingleMu21L3Filtered21",
			# HLT_Mu25_v1
			"hltSingleMu21L3Filtered25",
			# HLT_IsoMu9
			"hltSingleMuIsoL3PreFiltered9",
			"hltSingleMuIsoL3IsoFiltered9",
			# HLT_IsoMu11_v1
			"hltL1sL1SingleMu7",
			"hltL1SingleMu7L1Filtered0",
			"hltL2Mu7L2Filtered7",
			"hltSingleMuIsoL2IsoFiltered7",
			"hltSingleMuIsoL3PreFiltered11",
			"hltSingleMuIsoL3IsoFiltered11",
			# HLT_IsoMu13_v1
			"hltSingleMuIsoL3PreFiltered13",
			"hltSingleMuIsoL3IsoFiltered13",
			# HLT_IsoMu15_v1
			"hltSingleMuIsoL3PreFiltered15",
			"hltSingleMuIsoL3IsoFiltered15",
			# HLT_IsoMu17_v1
			"hltSingleMuIsoL3PreFiltered17",
			"hltSingleMuIsoL3IsoFiltered17",
			# HLT_DoubleMu
			"hltL1sL1DoubleMuOpen",
			"hltL1sL1DoubleMu3",
			"hltDiMuonL1Filtered",
			"hltDiMuonL1Filtered0",
			"hltDiMuonL3PreFiltered0",
			"hltDiMuonL3PreFiltered",
			"hltDiMuonL3PreFiltered3",
			"hltDiMuonL3PreFiltered5",
			# andere
			"hltL1sL1SingleMu0",
			"hltL1sL1SingleMu3",
			"hltL1sL1SingleMu20",
			"hltL1SingleMu0L1Filtered0",
			"hltL1SingleMu3L1Filtered0",
			"hltL2Mu9L2Filtered9",
			"hltL2Mu11L2Filtered11",
			"hltSingleMu3L2Filtered3",
			"hltSingleMu5L2Filtered4",
			"hltSingleMu9L2Filtered7",
			"hltSingleMu3L3Filtered3",
			"hltSingleMu5L3Filtered5",
			"hltSingleMuIsoL3IsoFiltered3",
		),
		noiseHCAL = cms.InputTag("hcalnoise"),

		errorsAndWarnings = cms.InputTag("logErrorHarvester"),
		errorsAndWarningsAvoidCategories = cms.vstring(),
		printErrorsAndWarnings = cms.bool(False),
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
			# Cuts for PF isolation
			pfIsoVetoCone = cms.double(0.01),
			pfIsoVetoMinPt = cms.double(0.5),
		),
		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
		hltMaxdR = cms.double(0.2),
		hltMaxdPt_Pt = cms.double(1.),
		noPropagation = cms.bool(False),
	),

	CaloTaus = cms.PSet(kappaNoCut, kappaNoRegEx,
		caloRecoTaus = cms.PSet(
			src = cms.InputTag("caloRecoTauProducer"),
			discr = cms.vstring("caloRecoTau*")
		)
	),

	PFTaus = cms.PSet(kappaNoCut, kappaNoRegEx,
		shrinkingConePFTaus = cms.PSet(
			src = cms.InputTag("shrinkingConePFTauProducer"),
			discr = cms.vstring("shrinkingConePFTau*")
		),
		fixedConePFTaus = cms.PSet(
			src = cms.InputTag("fixedConePFTauProducer"),
			discr = cms.vstring("fixedConePFTau*")
		),
		hpsPFTaus = cms.PSet(
			src = cms.InputTag("hpsPFTauProducer"),
			discr = cms.vstring("hpsPFTau*")
		)
	),

	TriggerObjects = cms.PSet(
		kappaNoRegEx,
		hltTag = cms.InputTag("hltTriggerSummaryAOD"),
		triggerObjects = cms.vstring(
			# HLT_Mu7
			"hltL1sL1SingleMu5",
			"hltL1SingleMu5L1Filtered0",
			"hltSingleMu7L2Filtered5",
			"hltSingleMu7L3Filtered7",
			# HLT_Mu9
			"hltSingleMu9L3Filtered9",
			# path HLT_Mu11
			"hltSingleMu11L3Filtered11",
			# path HLT_Mu13_v1
			"hltSingleMu13L3Filtered13",
			# HLT_Mu15_v1
			"hltSingleMu15L3Filtered15",
			# HLT_Mu17_v1
			"hltSingleMu17L3Filtered17",
			# HLT_Mu19_v1
			"hltSingleMu19L3Filtered19",
			# HLT_Mu21_v1
			"hltSingleMu21L3Filtered21",
			# HLT_Mu25_v1
			"hltSingleMu21L3Filtered25",
			# HLT_IsoMu9
			"hltSingleMuIsoL3PreFiltered9",
			"hltSingleMuIsoL3IsoFiltered9",
			# HLT_IsoMu11_v1
			"hltL1sL1SingleMu7",
			"hltL1SingleMu7L1Filtered0",
			"hltL2Mu7L2Filtered7",
			"hltSingleMuIsoL2IsoFiltered7",
			"hltSingleMuIsoL3PreFiltered11",
			"hltSingleMuIsoL3IsoFiltered11",
			# HLT_IsoMu13_v1
			"hltSingleMuIsoL3PreFiltered13",
			"hltSingleMuIsoL3IsoFiltered13",
			# HLT_IsoMu15_v1
			"hltSingleMuIsoL3PreFiltered15",
			"hltSingleMuIsoL3IsoFiltered15",
			# HLT_IsoMu17_v1
			"hltSingleMuIsoL3PreFiltered17",
			"hltSingleMuIsoL3IsoFiltered17",
			# HLT_DoubleMu
			"hltL1sL1DoubleMuOpen",
			"hltL1sL1DoubleMu3",
			"hltDiMuonL1Filtered",
			"hltDiMuonL1Filtered0",
			"hltDiMuonL3PreFiltered0",
			"hltDiMuonL3PreFiltered",
			"hltDiMuonL3PreFiltered3",
			"hltDiMuonL3PreFiltered5",
			# andere
			"hltL1sL1SingleMu0",
			"hltL1sL1SingleMu3",
			"hltL1sL1SingleMu20",
			"hltL1SingleMu0L1Filtered0",
			"hltL1SingleMu3L1Filtered0",
			"hltL2Mu9L2Filtered9",
			"hltL2Mu11L2Filtered11",
			"hltSingleMu3L2Filtered3",
			"hltSingleMu5L2Filtered4",
			"hltSingleMu9L2Filtered7",
			"hltSingleMu3L3Filtered3",
			"hltSingleMu5L3Filtered5",
			"hltSingleMuIsoL3IsoFiltered3",
		),
	),

	Tracks = cms.PSet(kappaNoRename,
		maxN = cms.int32(-1),
		minPt = cms.double(10.),
		maxEta = cms.double(2.5),

		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoTracks_generalTracks"),
		blacklist = cms.vstring(),
	),

	Partons = cms.PSet(kappaNoCut, kappaNoRegEx,
		genParticles = cms.PSet(
			src = cms.InputTag("genParticles"),
			selectedStatus = cms.int32(8),      # select, if (1<<status & selectedStatus) or selectedStatus==0
			selectedParticles = cms.vint32(),   # empty = all pdgIds possible
		),
		genStableMuons = cms.PSet(
			src = cms.InputTag("genParticles"),
			selectedStatus = cms.int32(2),      # select, if (1<<status & selectedStatus) or selectedStatus==0
			selectedParticles = cms.vint32(13, -13),   # empty = all pdgIds possible
		),
	),

	GenTaus = cms.PSet(kappaNoCut, kappaNoRegEx,
		genTaus = cms.PSet(
			src = cms.InputTag("genParticles"),
			selectedStatus = cms.int32(0)       # select, if (1<<status & selectedStatus) or selectedStatus==0
		)
	),

	TrackSummary = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoTracks_generalTracks"),
		blacklist = cms.vstring(),

		rename = cms.vstring("$ => Summary"),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	PFJets = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFJets_.*Jet"),
		blacklist = cms.vstring(),

		rename = cms.vstring(
			"(antikt)|(kt)|(siscone)|(iterativecone)|(icone)|(ak)([0-9]*) => (?1AK)(?2KT)(?3SC)(?4IC)(?5IC)(?6AK)$7"
		),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	Vertex = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring(".*offlinePrimaryVertices.*"),
		blacklist = cms.vstring(),

		rename = cms.vstring(),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),
	),

	BeamSpot = cms.PSet(kappaNoRename,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoBeamSpot.*"),
		blacklist = cms.vstring(""),
	),

	LV = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("reco.*Jets_.*Jet"),
		blacklist = cms.vstring("recoCastor.*"),

		rename = cms.vstring(
			"JetPlusTrack(.*) => $1JPT",
			"(antikt)|(kt)|(siscone)|(iterativecone)|(icone)|(ak)([0-9]*) => (?1AK)(?2KT)(?3SC)(?4IC)(?5IC)(?6AK)$7",
			"((L2)(L3)?|(ZSP)(Jet)?)CorJet(..[0-9]*)(PF)?(JPT)?(Calo)? => $6(?3L3:(?2L2))(?4L0)(?7PF)(?8JPT)Jets",
		),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(".*CaloJets",".*PFJets"),
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

	MET = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("reco.*MET"),
		blacklist = cms.vstring("recoPFMET"),

		rename = cms.vstring(
			"(gen)?(ht)?met => (?1Gen:Calo)MET(?2HT)",
		),
		rename_whitelist = cms.vstring("^(Calo|Gen)MET"),
		rename_blacklist = cms.vstring(),
	),

	PFMET = cms.PSet(kappaNoRename,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFMET"),
		blacklist = cms.vstring(),
	),

	PFCandidates = cms.PSet(kappaNoRename, kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFCandidates_particleFlow"),
		blacklist = cms.vstring(),
	),

	L1Muons = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("l1extraL1MuonParticles_l1extraParticles"),
		blacklist = cms.vstring(),
		
		rename = cms.vstring(
			"l1extraParticles => l1muons",
		),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),
	),
)
