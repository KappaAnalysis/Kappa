queries = {
	"Data" : {
		"data" : True,
		"embedded" : False,
		"energy" : "8"
	},
	"DataMuEG" : {
		"data" : True,
		"embedded" : False,
		"energy" : "8",
		"process" : "MuEG"
	},
	"DataTauMuEG" : {
		"data" : True,
		"embedded" : False,
		"energy" : "8",
		"process" : "MuEG"
	},
	"DYJets": {
		"process" : "(^DY\d{0,1}JetsToLL_M50|VBF_ZToLL)",
		"generator" : "^((?!tauPolarOff).)*$",
		"energy" : "8"
	},
	"Embedded": {
		"embedded" : True,
		"data" : True,
		"energy" : "8",
		"scenario" : "^((?!RHembedded).)*$"
	},
	"Dibosons": {
		"process" : "(W|Z)(W|Z)",
		"energy" : "8"
	},

	"SM_GluGluToHToTauTau": {
		"process" : "GluGluToHToTauTau",
		"generator" : "^((?!tauPolarOff).)*$",
		"energy" : "8"
	},
	"SM_GluGluToHToTauTau_110-145_GeV": {
		"process" : "GluGluToHToTauTau_M1[1-4][0,5]",
		"generator" : "^((?!tauPolarOff).)*$",
		"energy" : "8"
	},
	"SM_VBFHToTauTau": {
		"process" : "VBF_?HToTauTau",
		"generator" : "^((?!tauPolarOff).)*$",
		"energy" : "8"
	},
	"SM_VBFHToTauTau_110-145_GeV": {
		"process" : "VBF_?HToTauTau_M1[1-4][0,5]",
		"generator" : "^((?!tauPolarOff).)*$",
		"energy" : "8"
	},
	"SM_WH_ZH_TTH_HToTauTau": {
		"process" : "WH_ZH_TTH_HToTauTau",
		"energy" : "8"
	},
	"SM_WH_ZH_TTH_HToTauTau-125_GeV": {
		"process" : "WH_ZH_TTH_HToTauTau_M125",
		"energy" : "8"
	},
	"TTJets": {
		"embedded" : False,
		"process" : "^TTJets|^Tbar|^T_tW",
		"energy" : "8"
	},
	"WJets": {
		"process" : "^W(\d)Jet|^WJets",
		"energy" : "8"
	}
}
