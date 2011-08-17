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
		lumiSource = cms.InputTag("lumiProducer"),
		pileUpInfoSource = cms.InputTag("addPileupInfo"),

		l1Source = cms.InputTag("gtDigis"),
		hltSource = cms.InputTag("TriggerResults"),
		hltWhitelist = cms.vstring(
			"^HLT_HT([0-9]+)(_v[[:digit:]]+)?$",
			".*Jet.*",
			".*PFTau.*",
			"^HLT_(L[123])?(Iso|Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",
			"^HLT_(L[123])?(Iso|Double)?Mu([0-9]+)_(L[123])?(Iso|Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",
			"^HLT_(Iso)?Mu([0-9]+)_PFTau([0-9]+)(_v[[:digit:]]+)?$",
			"^HLT_QuadJet([0-9]+)(_v[[:digit:]]+)?$",
		),
		hltBlacklist = cms.vstring(
			".*AlCa.*",
			".*NoBPTX.*",
			".*ForwardBackward.*",
			".*L1Tech.*",
			".*CentralJet.*",
			".*BTag.*",
			"^HLT_Mu([0-7])(_v[[:digit:]]+)?$",
			"^HLT_MET[0-9]*_.*Jet.*",
			"^HLT_Mu([0-9]+)_.*Jet([0-9]+).*",
			"^HLT_JetE30_NoBPTX.*",
			"^HLT_Ele25_CaloIdVT_TrkIdT_.*",
			".*_CaloIdL.*",
			".*_CaloIdT.*",
			".*_CaloIdVT.*",
			"^HLT_ExclDiJet60_.*",
			"^HLT_CentralJet80_MET.*",
			"^HLT_Mu*_HT",
			"^HLT_DiJet.*_PT.*",
			"^HLT_Mu([0-9]+)_(Di|Tri)CentralJet.*",
			"^HLT_(Iso|Double)?Mu.*_HT.*",
			".*HT.*_DoubleLooseIsoPFTau.*",
			".*HT.*_DoubleDisplacedJet.*",
			"^HLT_L[12].*",
			"^HLT_QuadJet.*_IsoPFTau.*",
			"^HLT_DiJet([0-9]+)_MET([0-9]+)_.*",
			"^HLT_EightJet.*",
			"^HLT_FatJetMass.*",
			"^HLT_.*DoubleIsoPFTau([0-9]+)_.*"
		),
		printHltList = cms.bool(False),

		hlTrigger = cms.InputTag("hltTriggerSummaryAOD"),
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
			"hltSingleMu3L2Filtered3",
			"hltSingleMu5L2Filtered4",
			"hltSingleMu9L2Filtered7",
			"hltSingleMu3L3Filtered3",
			"hltSingleMu5L3Filtered5",
			"hltSingleMuIsoL3IsoFiltered3",

			# Objekte aus DoubleMu
			"hltDiL3fL1sDoubleMu3p5L1f0L2f0L3Filtered45",
			"hltDiMuonL1Filtered0",
			"hltDiMuonL2PreFiltered0",
			"hltDiMuonL3p5PreFiltered8",
			"hltDiMuonL3PreFiltered5Eta2p15",
			"hltL1DoubleMu3L3TriMuFiltered5",
			"hltL2DoubleMu23NoVertexL2PreFiltered",
			"hltL2DoubleMu30NoVertexL2PreFiltered",
			"hltL2DoubleMu35NoVertexL2PreFiltered",
			"hltL3fL1sDiMu3p5L1f3p5L2f3p5L3f6",
			"hltL3Mu8Jet20L3Filtered8",
			"hltSingleL2MuOpenL2PreFilteredNoVtx",
			"hltTripleMu0L3TriMuFiltered5",
		),
		noiseHCAL = cms.InputTag("hcalnoise"),

		errorsAndWarnings = cms.InputTag("logErrorHarvester"),
		errorsAndWarningsAvoidCategories = cms.vstring(),
		printErrorsAndWarnings = cms.bool(False),
	),

	TriggerObjects = cms.PSet(
		kappaNoRegEx,
		hltTag = cms.InputTag("hltTriggerSummaryAOD"),
		triggerObjects = cms.vstring(
			# L1 (2010/2011)
			"hltL1sL1SingleMu7",
			"hltL1sL1SingleMu10",
			"hltL1sL1SingleMu12",

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

			# Objekte aus DoubleMu
			"hltDiL3fL1sDoubleMu3p5L1f0L2f0L3Filtered45",
			"hltDiMuonL1Filtered0",
			"hltDiMuonL2PreFiltered0",
			"hltDiMuonL3p5PreFiltered8",
			"hltDiMuonL3PreFiltered5Eta2p15",
			"hltL1DoubleMu3L3TriMuFiltered5",
			"hltL2DoubleMu23NoVertexL2PreFiltered",
			"hltL2DoubleMu30NoVertexL2PreFiltered",
			"hltL2DoubleMu35NoVertexL2PreFiltered",
			"hltL3fL1sDiMu3p5L1f3p5L2f3p5L3f6",
			"hltL3Mu8Jet20L3Filtered8",
			"hltSingleL2MuOpenL2PreFilteredNoVtx",
			"hltTripleMu0L3TriMuFiltered5",
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

		whitelist = cms.vstring(".*offlinePrimaryVertices.*"),
		blacklist = cms.vstring(),
	),

	VertexSummary = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring(".*offlinePrimaryVertices.*"),
		blacklist = cms.vstring(),

		rename = cms.vstring("$ => Summary"),
		rename_whitelist = cms.vstring(),
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
		blacklist = cms.vstring("Castor", "BasicJet"),

		rename = cms.vstring(
			"JetPlusTrack(.*) => $1JPT",
			"(antikt)|(kt)|(siscone)|(iterativecone)|(icone)|(ak)([0-9]*) => (?1AK)(?2KT)(?3SC)(?4IC)(?5IC)(?6AK)$7",
			"((L2)(L3)?|(ZSP)(Jet)?)CorJet(..[0-9]*)(PF)?(JPT)?(Calo)? => $6(?3L3:(?2L2))(?4L0)(?7PF)(?8JPT)Jets",
		),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(".*CaloJets", ".*PFJets"),
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

	PFMET = cms.PSet(
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFMET"),
		blacklist = cms.vstring(),

		rename = cms.vstring("pfMet => PFMET"),
		rename_whitelist= cms.vstring(),
		rename_blacklist = cms.vstring(),
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

	GenPhotons = cms.PSet(kappaNoCut, kappaNoRegEx,
		genPhotons = cms.PSet(
			src = cms.InputTag("genParticles"),
		),
	),

	PFCandidates = cms.PSet(kappaNoRename, kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFCandidates_particleFlow"),
		blacklist = cms.vstring(),
	),

	JetArea = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("kt6PFJetsRho_rho"),
		blacklist = cms.vstring(),

		rename = cms.vstring("kt6PFJetsRho => KT6Area"),
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
			# Cuts for PF isolation
			pfIsoVetoCone = cms.double(0.01),
			pfIsoVetoMinPt = cms.double(0.5),
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

	PFJets = cms.PSet(kappaNoCut,
		manual = cms.VInputTag(),

		whitelist = cms.vstring("recoPFJets_.*Jet"),
		blacklist = cms.vstring("Rho"),

		rename = cms.vstring(
			"(antikt)|(kt)|(siscone)|(iterativecone)|(icone)|(ak)([0-9]*) => (?1AK)(?2KT)(?3SC)(?4IC)(?5IC)(?6AK)$7"
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
		#fixedConePFTaus = cms.PSet(
		#	src = cms.InputTag("fixedConePFTauProducer"),
		#	discr = cms.vstring("fixedConePFTau*")
		#),
		hpsPFTaus = cms.PSet(
			src = cms.InputTag("hpsPFTauProducer"),
			discr = cms.vstring("hpsPFTau*")
		)
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
