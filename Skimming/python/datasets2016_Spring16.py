queries = {
	"Spring16_Data": {
		"data" : True,
		"scenario" : "PromptRecov2",
		"energy" : "13"
	},
	"Spring16_DYJets": {
		"process" : "^DY([0-9])?JetsTo(LL|TauTau)",
		"campaign" : "RunIISpring16MiniAODv2",
		"energy" : "13"
	},
	"Spring16_Dibosons": {
		"process" : "(W|Z|V)(W|Z|V)(Jets)?(To)?",
		"campaign" : "RunIISpring16MiniAODv2",
		"energy" : "13"
	},
    "Spring16_SUSY_Sync": {
            "process" : "SUSYGluGluToHToTauTau_M160$",
            "campaign" : "RunIISpring16MiniAODv.*",
            "energy" : "13"
    },
    "Spring16_SUSY": {
            "process" : "SUSY",
            "campaign" : "RunIISpring16MiniAODv(1|2)$",
            "energy" : "13"
    },
    "Spring16_SM_Higgs": {
            "process" : "((GluGlu|VBF|Wplus|Wminus|Z)HToTauTau)|(ttHJetToTT)",
            "campaign" : "RunIISpring16MiniAOD.*reHLT",
            "energy" : "13"
    },
	"Spring16_QCD": {
		"process" : "^QCD",
		"campaign" : "RunIISpring16MiniAODv2",
		"energy" : "13"
	},
	"Spring16_TTJets": {
		"process" : "^TTJets|^Tbar|^T_tW|^TT|(^ST.*)$",
		"campaign" : "RunIISpring16MiniAODv2",
		"energy" : "13"
	},
	"Spring16_WJets": {
		"process" : "(^W(\d)Jets|^WJets)ToLNu",
		"campaign" : "RunIISpring16MiniAODv2",
		"energy" : "13"
	},
	"Spring16_EWK": {
		"process" : "^EWK(WMinus|WPlus|Z)2Jets",
		"campaign" : "RunIISpring16MiniAODv2",
		"energy" : "13"
	},
	"Spring16_reHLT": {
		"campaign" : "RunIISpring16MiniAODv.*reHLT",
		"energy" : "13"
	}
}
