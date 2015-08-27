import FWCore.ParameterSet.Config as cms

hltWhitelist = cms.vstring( ## HLT selection
	# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauWorking2015#Trigger_Information
	# can be tested at https://regex101.com
	
	# m
	"^HLT_(Iso)?Mu[0-9]+(_TrkIsoVVL)?(_eta2p1)?_v[0-9]+$"
	
	# mm
	"^HLT_(Iso)?Mu[0-9]+(_TrkIsoVVL)?(_eta2p1)?_(Iso)?Mu[0-9]+(_TrkIsoVVL)?(_eta2p1)?_v[0-9]+$"
	
	# e
	"^HLT_Ele[0-9]+(_CaloIdL)?(_TrackIdL)?(_IsoVL)?(_eta2p1)?(_WP([0-9]+)?(Loose|Medium|Tight)?)?(_Gsf)?_v[0-9]+$",
	
	# ee
	"^HLT_DoubleEle[0-9]+(_CaloIdL)?(_IsoVL)?(_eta2p1)?(_WP([0-9]+)?(Loose|Medium|Tight)?)?(_GsfTrkIdVL)?(_MW)?_v[0-9]+$",
	"^HLT_Ele[0-9]+(_CaloIdL)?(_TrackIdL)?(_IsoVL)?(_eta2p1)?(_WP([0-9]+)?(Loose|Medium|Tight)?)?(_Gsf)?_^HLT_Ele[0-9]+(_CaloIdL)?(_TrackIdL)?(_IsoVL)?(_eta2p1)?(_WP([0-9]+)?(Loose|Medium|Tight)?)?(_Gsf)?_v[0-9]+$",
	
	# em
	"^HLT_Mu[0-9]+(_TrkIsoVVL)_(Ele)[0-9]+(_Gsf)?_CaloId(L)?_TrackId(L)?_Iso(VL)?(_MediumWP)?_v[0-9]+$",
	
	# et
	"^HLT_Ele[0-9]+(_CaloIdL)?(_TrackIdL)?(_IsoVL)?(_eta2p1)?(_WP([0-9]+)?(Loose|Medium|Tight)?)?(_Gsf)?_(Loose|Medium|Tight)?IsoPFTau[0-9]+_v[0-9]+$"
	
	# mt
	"^HLT_(Iso)?Mu[0-9]+(_eta2p1)?_IterTrk[0-9]+_v[0-9]+$",
	"^HLT_(Iso)?Mu[0-9]+(_eta2p1)?_(Loose|Medium|Tight)IsoPFTau[0-9]+(_Trk[0-9])?(_eta2p1)?(_Reg)?_v[0-9]+$",
	
	# tt
	"^HLT_Double(Loose|Medium|Tight)?IsoPFTau[0-9]+(_Trk[0-9])?+(_eta2p1)?(_Reg)?_v[0-9]+$",
	
	# t
	"^HLT_(Loose|Medium|Tight)?IsoPFTau[0-9]+(_Trk[0-9]+)?(_eta2p1)?(_Reg)?_v[0-9]+$"
	
	# specials (possible generalization: Mu15, L1ETM20, Photon20, Ele8)
	"^HLT_(Loose|Medium)?IsoPFTau[0-9]+_Trk[0-9]+(_eta2p1)?_MET[0-9]+_v[0-9]+$",
)

hltBlacklist = cms.vstring()

