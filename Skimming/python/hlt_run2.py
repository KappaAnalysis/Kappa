import FWCore.ParameterSet.Config as cms
hltWhitelist = cms.vstring( ## HLT selection
	# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauWorking2015#Trigger_Information
	# can be tested at https://regex101.com
	# em
	"^HLT_Mu[0-9]+(_TrkIsoVVL)_(Ele)[0-9]+_Gsf_CaloId_TrackId_Iso_MediumWP_v[0-9]+$",
	# et
	"^HLT_Ele[0-9]+_eta2p1_WP[0-9]+_Gsf(_LooseIsoPFTau[0-9]+)?_v[0-9]+$",
	# mt
	"^HLT_(Iso)?Mu[0-9]+(_eta2p1)?_(Loose|Medium|Tight)IsoPFTau[0-9]+(_Trk[0-9]_eta2p1)?_v[0-9]+$",
	"^HLT_(Iso)?Mu[0-9]+(_eta2p1)?_IterTrk[0-9]+_v[0-9]+$",
	# tt
	"^HLT_Double(Medium)?IsoPFTau[0-9]+_Trk(1|5)(_eta2p1)?_Reg_v[0-9]+$",
	# specials (possible generalization: Mu15, L1ETM20, Photon20, Ele8)
	"^HLT_(Loose|Medium)?IsoPFTau[0-9]+_Trk[0-9]+(_eta2p1)?_MET[0-9]+_v[0-9]+$",
	)

hltBlacklist = cms.vstring(
	"HLT_Mu13_Mu8", # v21 gives errors for the trigger objects
	)
