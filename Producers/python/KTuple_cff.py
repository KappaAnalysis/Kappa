import FWCore.ParameterSet.Config as cms

kappaTupleDefaultsBlock = cms.PSet(
	verbose = cms.int32(0),
	active = cms.vstring("Metadata"),

	Metadata = cms.PSet(
		genSource = cms.InputTag("generator"),

		l1Source = cms.InputTag("gtDigis"),
		hltSource = cms.InputTag("TriggerResults::HLT"),
		hltWhitelist = cms.vstring("^HLT_(L1|Di|Double|Triple|Quad)?(Jet)+(Ave)?", ".*Jet.*",
			"^HLT_MET[0-9]*", "^HLT_Activity.*", ".*(Bias|BSC).*", "^HLT_PhysicsDeclared", ".*Mu.*"),
		hltBlacklist = cms.vstring(),
		printHltList = cms.bool(True),

		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
		muonTriggerObjects = cms.vstring("hlt.*Mu.*"),
		noiseHCAL = cms.InputTag("hcalnoise"),
	),

	Muons = cms.PSet(
		maxN = cms.int32(-1),
		minPt = cms.double(-1),
		maxEta = cms.double(-1),
		muons = cms.PSet(
			src = cms.InputTag("muons"),
			srcMuonIsolation=cms.InputTag("muIsoDepositTk"),
			isoVetos=cms.vstring("0.01"),
		),
		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
		hltMaxdR = cms.double(0.05),
	),

	Tracks = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoTracks_generalTracks"),
		blacklist = cms.vstring(),

		rename = cms.vstring(),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),

		maxN = cms.int32(-1),
		minPt = cms.double(-1),
		maxEta = cms.double(-1),
	),
	TrackSummary = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoTracks_generalTracks"),
		blacklist = cms.vstring(),

		rename = cms.vstring(),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),

		maxN = cms.int32(-1),
		minPt = cms.double(-1),
		maxEta = cms.double(-1),
	),
	PFJets = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFJets_.*Jet"),
		blacklist = cms.vstring(),

		rename = cms.vstring(
			"(antikt)|(kt)|(siscone)|(iterativecone)|(icone)|(ak)([0-9]*) => (?1AK)(?2KT)(?3SC)(?4IC)(?5IC)(?6AK)$7"
		),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),

		maxN = cms.int32(-1),
		minPt = cms.double(-1),
		maxEta = cms.double(-1),
	),
	Vertex = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring(),
		blacklist = cms.vstring(),

		rename = cms.vstring(),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),

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

	LV = cms.PSet(
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

		maxN = cms.int32(-1),
		minPt = cms.double(-1),
		maxEta = cms.double(-1),
	),

	Tower = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("towerMaker"),
		blacklist = cms.vstring(),

		rename = cms.vstring("towerMaker => towers"),
		rename_whitelist = cms.vstring(),
		rename_blacklist = cms.vstring(),

		srcPVs = cms.InputTag("offlinePrimaryVertices"),

		maxN = cms.int32(-1),
		minPt = cms.double(-1),
		maxEta = cms.double(-1),
	),

	MET = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("reco.*MET"),
		blacklist = cms.vstring(),

		rename = cms.vstring(
			"(gen)?(pf)?(ht)?met => (?1Gen:Calo)MET(?2PF)(?3HT)",
		),
		rename_whitelist = cms.vstring("^(Calo|Gen)MET"),
		rename_blacklist = cms.vstring(),
	),
)
