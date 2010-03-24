import FWCore.ParameterSet.Config as cms

kappaTupleDefaultsBlock = cms.PSet(
	verbose = cms.int32(0),
	active = cms.vstring("Metadata"),

	Metadata = cms.PSet(
		genSource = cms.InputTag("generator"),

		l1Source = cms.InputTag("gtDigis"),
		hltSource = cms.InputTag("TriggerResults::HLT"),
		hltFilter = cms.string("^HLT_(((L1|Di|Double|Triple|Quad)?(Jet)+(Ave)?|MET)[0-9]*|Activity_.*|.*(Bias|BSC).*)$"),

		noiseHCAL = cms.InputTag("hcalnoise"),
		srcPVs = cms.InputTag("offlinePrimaryVertices"),
	),

	Tracks = cms.PSet(
		manual = cms.VInputTag(),
		filter = cms.string("recoTracks_generalTracks"),
		rename = cms.vstring(),
		renameFilter = cms.string(""),
		maxN = cms.int32(-1),
		minPt = cms.double(-1),
	),

	Jets = cms.PSet(
		manual = cms.VInputTag(),
		filter = cms.string("reco.*Jets_.*Jet"),
		rename = cms.vstring(
			"JetPlusTrack(.*) => $1JPT",
			"(antikt)|(kt)|(siscone)|(iterativecone)|(icone)|(ak)([0-9]*) => (?1AK)(?2KT)(?3SC)(?4IC)(?5IC)(?6AK)$7",
			"((L2)(L3)?|(ZSP)(Jet)?)CorJet(..[0-9]*)(PF)?(JPT)?(Calo)? => $6(?3L3:(?2L2))(?4L0)(?7PF)(?8JPT)Jets",
		),
		renameFilter = cms.string(""),
		maxN = cms.int32(-1),
		minPt = cms.double(-1),
	),

	Tower = cms.PSet(
		manual = cms.VInputTag(),
		filter = cms.string("towerMaker"),
		srcPVs = cms.InputTag("offlinePrimaryVertices"),
		rename = cms.vstring("towerMaker => towers"),
		renameFilter = cms.string(""),
		maxN = cms.int32(-1),
		minPt = cms.double(-1),
	),

	MET = cms.PSet(
		manual = cms.VInputTag(),
		filter = cms.string("reco.*MET"),
		rename = cms.vstring(
			"(gen)?(pf)?(ht)?met => (?1Gen:Calo)MET(?2PF)(?3HT)",
		),
		renameFilter = cms.string("^(Calo|Gen)MET"),
	),
)
