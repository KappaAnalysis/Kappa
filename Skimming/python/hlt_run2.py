import FWCore.ParameterSet.Config as cms
hltWhitelist = cms.vstring( ## HLT selection
	# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauWorking2015#Trigger_Information
	# can be tested at https://regex101.com

	"^HLT_.*Mu[0-9]+.*_v[0-9]+$",
	"^HLT_.*Ele[0-9]+.*_v[0-9]+$",
	"^HLT_.*Tau(HPS)?[0-9]+.*_v[0-9]+$",
)

hltBlacklist = cms.vstring(
	"^HLT_.*NoVtx.*_v[0-9]+$",
	"^HLT_PFMET.*_v[0-9]+$",
	"^HLT_MonoCentralPFJet.*_v[0-9]+$",
	"^HLT_HIL.*_v[0-9]+$",
	"^HLT_DiPFJet.*_v[0-9]+$"
)
