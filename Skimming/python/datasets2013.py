queries = {
	"Data" : {
		"data" : True,
		"embedded" : False,
		"energy" : "13"
	},
	"DYJets": {
		"process" : "^DYJetsToLL",
		"energy" : "13"
	},
	"Dibosons": {
		"process" : "(W|Z)(W|Z)JetsTo",
		"energy" : "13"
	},

	"SM_GluGluToHToTauTau": {
		"process" : "GluGluToHToTauTau",
		"energy" : "13"
	},
	"SM_VBFHToTauTau": {
		"process" : "VBF_HToTauTau",
		"energy" : "13"
	},
	"SM_WH_ZH_TTH_HToTauTau": {
		"process" : "WH_ZH_TTH_HToTauTau",
		"energy" : "13"
	},
	"TTJets": {
		"process" : "^TTJets|^Tbar|^T_tW",
		"energy" : "13"
	},
	"WJets": {
		"process" : "^W(\d)Jet|^WJets",
		"energy" : "13"
	},
	"Phys14_miniAOD": {
		"energy" : "13",
		"scenario" : "PU20bx25",
		"format" : "MINIAODSIM"
	},
	"Phys14_AOD": {
		"energy" : "13",
		"scenario" : "PU20bx25",
		"format" : "^AODSIM"
	},
}
