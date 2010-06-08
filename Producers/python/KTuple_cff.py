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

kappaTupleDefaultsBlock = cms.PSet(
	verbose = cms.int32(0),
	active = cms.vstring("Metadata"),

	Metadata = cms.PSet(
		forceLumi = cms.int32(-1),
		genSource = cms.InputTag("generator"),

		l1Source = cms.InputTag("gtDigis"),
		hltSource = cms.InputTag("TriggerResults::HLT"),
		hltWhitelist = cms.vstring(
			".*Jet.*",
			"^HLT_MET[0-9]*",
			"^HLT_Activity.*", ".*(Bias|BSC).*",
			"HLT_L1Mu20", "HLT_L1Mu14_L1SingleJet6U",
			"^HLT_L1MuOpen$","^HLT_L1Mu$",
			"^HLT_L2Mu0$", "^HLT_L2Mu3$", "^HLT_L2Mu5$", "^HLT_L2Mu9$", "^HLT_L2Mu11$",
			"^HLT_Mu3", "^HLT_IsoMu3$", "^HLT_Mu5$", "^HLT_Mu9", "^HLT_Mu11",
			"^HLT_DoubleMu0$", "^HLT_DoubleMu3$"
			# "^HLT_(L1|Di|Double|Triple|Quad)?(Jet)+(Ave)?",
			# "HLT_L2DoubleMu0", "HLT_L1DoubleMuOpen", "HLT_L1Mu14_L1SingleEG10",
			# "HLT_L1Mu14_L1ETM30", "HLT_Mu0_L1MuOpen", "HLT_Mu0_Track0_Jpsi",
			# "HLT_Mu3_L1MuOpen", "HLT_Mu3_Track0_Jpsi", "HLT_Mu5_L1MuOpen",
			# "HLT_Mu5_Track0_Jpsi", "HLT_Mu0_L2Mu0", "HLT_Mu3_L2Mu0", "HLT_Mu5_L2Mu0"
		),
		hltBlacklist = cms.vstring(),
		printHltList = cms.bool(True),

		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
		muonTriggerObjects = cms.vstring(
			"hltSingleMu[0-9]*L[123]Filtered[0-9]*","hltL2Mu0L2Filtered0",
			"hlt.*SingleMu.*",
			"hlt.*DiMuon.*",
			"hltSingleMu.*",
			"hltMu.*",
			"hltL2Mu9L2Filtered9",
			"hltL2Mu11L2Filtered11",
			"hltPreL1Mu14L1SingleJet6U"
		),
		noiseHCAL = cms.InputTag("hcalnoise"),

		errorsAndWarnings = cms.InputTag("logErrorHarvester"),
		errorsAndWarningsAvoidCategories = cms.vstring(),
		printErrorsAndWarnings = cms.bool(False),
	),

	Muons = cms.PSet(kappaNoCut,
		muons = cms.PSet(
			src = cms.InputTag("muons"),
			srcMuonIsolation=cms.InputTag("muIsoDepositTk"),
			isoVetos=cms.vstring("0.01"),
		),
		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
		hltMaxdR = cms.double(0.3),
		hltMaxdPt_Pt = cms.double(1.),
	),

	Tracks = cms.PSet(kappaNoRename,
		maxN = cms.int32(-1),
		minPt = cms.double(10.),
		maxEta = cms.double(2.5),

		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoTracks_generalTracks"),
		blacklist = cms.vstring(),
	),

	Partons = cms.PSet(kappaNoCut,
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

	Vertex = cms.PSet(kappaNoRename,
		manual = cms.VInputTag(),

		whitelist = cms.vstring(),
		blacklist = cms.vstring(),

		maxN = cms.int32(-1),

		offlinePrimaryVertices = cms.PSet(
			src = cms.InputTag("offlinePrimaryVertices")
		),
		offlinePrimaryVerticesWithBS = cms.PSet(
			src = cms.InputTag("offlinePrimaryVerticesWithBS")
		),
		pixelVertices = cms.PSet(
			src = cms.InputTag("pixelVertices")
		),
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
)
