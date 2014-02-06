
# -*- coding: utf-8 -*-


# https://cmsweb.cern.ch/das/request?input=...

datasets = {

	##### DY + Jets (8 TeV) ####################################################
	"DYJetsToLL_M_50_madgraph" : {
		"dataset" : {
			7 : "/DYJetsToLL_TuneZ2_M-50_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"DY1JetsToLL_M_50_madgraph" : {
		"dataset" : {
			7 : None,
			8 : "/DY1JetsToLL_M-50_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"DY2JetsToLL_M_50_madgraph" : {
		"dataset" : {
			7 : None,
			8 : "/DY2JetsToLL_M-50_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"DY3JetsToLL_M_50_madgraph" : {
		"dataset" : {
			7 : None,
			8 : "/DY3JetsToLL_M-50_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"DY4JetsToLL_M_50_madgraph" : {
		"dataset" : {
			7 : None,
			8 : "/DY4JetsToLL_M-50_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	
	"DYJetsToLL_M_10To50_madgraph" : {
		"dataset" : {
			7 : "/DYJetsToLL_M-10To50_TuneZ2_7TeV-madgraph/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/DYJetsToLL_M-10To50filter_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"DY1JetsToLL_M_10To50_madgraph" : {
		"dataset" : {
			7 : None,
			8 : "/DY1JetsToLL_M-10To50_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"DY2JetsToLL_M_10To50_madgraph" : {
		"dataset" : {
			7 : None,
			8 : "/DY2JetsToLL_TuneZ2star_M-10To50_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	
	"VBFZToLL_VBFNLO_pythia" : {
		"dataset" : {
			7 : None,
			8 : "/VBF_ZToLL_VBFNLO_pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	
	##### ttbar + Jets #########################################################
	"TTJets_madgraph_tauola" : {
		"dataset" : {
			7 : "/TTJets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v2/AODSIM",
			8 : "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM",
		},
	},
	"TTJetsToLL_madgraph_tauola" : {
		"dataset" : {
			7 : None,
			8 : "/TTJets_FullLeptMGDecays_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v2/AODSIM",
		},
	},
	"TTJetsToLH_madgraph_tauola" : {
		"dataset" : {
			7 : None,
			8 : "/TTJets_SemiLeptMGDecays_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"TTJetsToHH_madgraph_tauola" : {
		"dataset" : {
			7 : None,
			8 : "/TTJets_HadronicMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A_ext-v1/AODSIM",
		},
	},
	"TbarW_powheg_tauola" : {
		"dataset" : {
			7 : "/Tbar_TuneZ2_tW-channel-DR_7TeV-powheg-tauola/Fall11-PU_S6_START42_V14B-v2/AODSIM",
			8 : "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"TW_powheg_tauola" : {
		"dataset" : {
			7 : "/T_TuneZ2_tW-channel-DR_7TeV-powheg-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	
	##### WW, WZ, ZZ ###########################################################
	"WWJetsToLLNN_madgraph_tauola" : {
		"dataset" : {
			7 : "/WWJetsTo2L2Nu_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WWJetsTo2L2Nu_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"WZJetsToLLHH_madgraph_tauola" : {
		"dataset" : {
			7 : "/WZJetsTo2L2Q_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WZJetsTo2L2Q_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"WZJetsToLLLN_madgraph_tauola" : {
		"dataset" : {
			7 : "/WZJetsTo3LNu_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WZJetsTo3LNu_TuneZ2_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"ZZJetsToLLLL_madgraph_tauola" : {
		"dataset" : {
			7 : "/ZZJetsTo4L_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/ZZJetsTo4L_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"ZZJetsToLLNN_madgraph_tauola" : {
		"dataset" : {
			7 : "/ZZJetsTo2L2Nu_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/ZZJetsTo2L2Nu_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"ZZJetsToLLQQ_madgraph_tauola" : {
		"dataset" : {
			7 : "/ZZJetsTo2L2Q_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/ZZJetsTo2L2Q_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"WW_pythia_tauola" : {
		"dataset" : {
			7 : None,
			8 : "/WW_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"WZ_pythia_tauola" : {
		"dataset" : {
			7 : None,
			8 : "/WZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	
	"ZZ_pythia_tauola" : {
		"dataset" : {
			7 : None,
			8 : "/ZZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	
	##### W + Jets #############################################################
	"WJetsToLN_madgraph_tauola" : {
		"dataset" : {
			7 : "/WJetsToLNu_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM",
		},
	},
	"W1JetsToLN_madgraph_tauola" : {
		"dataset" : {
			7 : "/W1Jet_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM",
		},
	},
	"W2JetsToLN_madgraph_tauola" : {
		"dataset" : {
			7 : "/W2Jets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM",
		},
	},
	"W3JetsToLN_madgraph_tauola" : {
		"dataset" : {
			7 : "/W3Jets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v2/AODSIM",
			8 : "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM",
		},
	},
	"W4JetsToLN_madgraph_tauola" : {
		"dataset" : {
			7 : "/W4Jets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
}

DYJets = [
	"DYJetsToLL_M_50_madgraph",
	"DY1JetsToLL_M_50_madgraph",
	"DY2JetsToLL_M_50_madgraph",
	"DY3JetsToLL_M_50_madgraph",
	"DY4JetsToLL_M_50_madgraph",
	"DYJetsToLL_M_10To50_madgraph",
	"DY1JetsToLL_M_10To50_madgraph",
	"DY2JetsToLL_M_10To50_madgraph",
	"VBFZToLL_VBFNLO_pythia",
]

TTJets = [
	"TTJets_madgraph_tauola",
	"TTJetsToLL_madgraph_tauola",
	"TTJetsToLH_madgraph_tauola",
	"TTJetsToHH_madgraph_tauola",
	"TbarW_powheg_tauola",
	"TW_powheg_tauola",
]

Dibosons = [
	"WWJetsToLLNN_madgraph_tauola",
	"WZJetsToLLHH_madgraph_tauola",
	"WZJetsToLLLN_madgraph_tauola",
	"ZZJetsToLLLL_madgraph_tauola",
	"ZZJetsToLLNN_madgraph_tauola",
	"ZZJetsToLLQQ_madgraph_tauola",
	"WW_pythia_tauola",
	"WZ_pythia_tauola",
	"ZZ_pythia_tauola",
]

WJets = [
	"WJetsToLN_madgraph_tauola",
	"W1JetsToLN_madgraph_tauola",
	"W2JetsToLN_madgraph_tauola",
	"W3JetsToLN_madgraph_tauola",
	"W4JetsToLN_madgraph_tauola",
]

