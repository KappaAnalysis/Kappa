
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
	"WJetsToLN_madgraph" : {
		"dataset" : {
			7 : "/WJetsToLNu_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM",
		},
	},
	"W1JetsToLN_madgraph" : {
		"dataset" : {
			7 : "/W1Jet_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM",
		},
	},
	"W2JetsToLN_madgraph" : {
		"dataset" : {
			7 : "/W2Jets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM",
		},
	},
	"W3JetsToLN_madgraph" : {
		"dataset" : {
			7 : "/W3Jets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v2/AODSIM",
			8 : "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V19-v1/AODSIM",
		},
	},
	"W4JetsToLN_madgraph" : {
		"dataset" : {
			7 : "/W4Jets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	
	##### SM ggH->tautau #######################################################
	"SM_GluGluToHToTauTau_M_90_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-90_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-90_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_95_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-95_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-95_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_100_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-100_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-100_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_105_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-105_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-105_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_110_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-110_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-110_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_115_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-115_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-115_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_120_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-120_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-120_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_125_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-125_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_130_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-130_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-130_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_135_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-135_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-135_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_140_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-140_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-140_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_145_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-145_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-145_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_150_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-150_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-150_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_155_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-155_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-155_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_GluGluToHToTauTau_M_160_powheg_pythia" : {
		"dataset" : {
			7 : "/GluGluToHToTauTau_M-160_7TeV-powheg-pythia6/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/GluGluToHToTauTau_M-160_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	
	##### SM VBF H->tautau #####################################################
	"SM_VBFHToTauTau_M_90_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-90_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBFHToTauTau_M-90_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_95_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-95_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBFHToTauTau_M-95_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_100_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-100_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBFHToTauTau_M-100_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_105_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-105_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBFHToTauTau_M-105_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_110_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-110_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-110_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_115_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-115_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-115_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_120_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-120_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-120_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_125_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-125_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-125_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_130_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-130_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-130_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_135_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-135_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-135_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_140_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-140_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-140_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_145_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-145_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-145_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_150_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-150_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-150_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_155_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-155_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-155_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_VBFHToTauTau_M_160_powheg_pythia" : {
		"dataset" : {
			7 : "/VBF_HToTauTau_M-160_7TeV-powheg-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/VBF_HToTauTau_M-160_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_90_powheg_pythia" : {
		"dataset" : {
			7 : "",
			8 : "",
		},
	},
	
	##### SM (W/Z/tt)H->tautau #################################################
	"SM_WH_ZH_TTH_HToTauTau_M_90_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-90_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-90_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_95_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-95_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-95_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_100_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-100_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-100_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_105_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-105_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-105_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_110_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-110_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-110_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_115_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-115_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-115_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_120_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-120_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-120_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_125_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-125_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-125_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_130_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-130_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-130_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_135_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-135_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-135_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_140_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-140_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-140_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_145_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-145_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-145_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_150_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-150_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-150_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_155_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-155_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-155_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
		},
	},
	"SM_WH_ZH_TTH_HToTauTau_M_160_powheg_pythia" : {
		"dataset" : {
			7 : "/WH_ZH_TTH_HToTauTau_M-160_7TeV-pythia6-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM",
			8 : "/WH_ZH_TTH_HToTauTau_M-160_8TeV-pythia6-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
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
	"WJetsToLN_madgraph",
	"W1JetsToLN_madgraph",
	"W2JetsToLN_madgraph",
	"W3JetsToLN_madgraph",
	"W4JetsToLN_madgraph",
]

SM_GluGluToHToTauTau = ["SM_GluGluToHToTauTau_M_%d_powheg_pythia" % higgsMass for higgsMass in range(90, 161, 5)]
SM_VBFHToTauTau = ["SM_VBFHToTauTau_M_%d_powheg_pythia" % higgsMass for higgsMass in range(90, 161, 5)]
SM_WH_ZH_TTH_HToTauTau = ["SM_WH_ZH_TTH_HToTauTau_M_%d_powheg_pythia" % higgsMass for higgsMass in range(90, 161, 5)]

