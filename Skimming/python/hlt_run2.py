import FWCore.ParameterSet.Config as cms
hltWhitelist = cms.vstring( ## HLT selection
	# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauWorking2015#Trigger_Information
	# can be tested at https://regex101.com
	
	"^HLT_.*Mu[0-9]+.*$",
	"^HLT_.*Ele[0-9]+.*$",
	"^HLT_.*Tau[0-9]+.*$",
)

hltBlacklist = cms.vstring(
	"^HLT_.*Photon.*$",
	"^HLT_.*photon.*$",
	"^HLT_.*Jet.*$",
	"^HLT_.*jet.*$",
	"^HLT_.*MET.*$",
	"^HLT_.*Psi.*$",
	"^HLT_.*Mass.*$",
	"^HLT_.*HT[0-9]+.*$",
	"^HLT_L1.*$",
	"^HLT_L2.*$",
	"^HLT_L1L2.*$",
	"^HLT_.*SameSign.*$",
	"^HLT_.*NoVertex.*$",
	"^HLT_.*NoVtx.*$",
	"^HLT_.*NoFilters.*$",
	"^HLT_.*SaveObjects.*$",
	"^HLT_.*_Di.*$",
	"^HLT_.*_Double.*$",
	"^HLT_.*_Bs.*$",
	"^HLT_.*_DZ.*$",
	"^HLT_.*Onia.*$",
)
