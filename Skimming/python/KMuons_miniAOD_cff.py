import FWCore.ParameterSet.Config as cms

## Isodeposits for muons
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi import *
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi import *
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi import *

from CommonTools.ParticleFlow.Isolation.pfMuonIsolation_cff import *

muPFIsoValueCharged03PFIso = muPFIsoValueCharged03.clone()
muPFIsoValueChargedAll03PFIso = muPFIsoValueChargedAll03.clone()
muPFIsoValueGamma03PFIso = muPFIsoValueGamma03.clone()
muPFIsoValueNeutral03PFIso = muPFIsoValueNeutral03.clone()
muPFIsoValuePU03PFIso = muPFIsoValuePU03.clone()

muonPFIsolationValuesSequence = cms.Sequence(
	muPFIsoValueCharged03PFIso+
	muPFIsoValueChargedAll03PFIso+
	muPFIsoValueGamma03PFIso+
	muPFIsoValueNeutral03PFIso+
	muPFIsoValuePU03PFIso
	)
muPFIsoDepositCharged.src = cms.InputTag("slimmedMuons")
muPFIsoDepositChargedAll.src = cms.InputTag("slimmedMuons")
muPFIsoDepositNeutral.src = cms.InputTag("slimmedMuons")
muPFIsoDepositGamma.src = cms.InputTag("slimmedMuons")
muPFIsoDepositPU.src = cms.InputTag("slimmedMuons")

makeKappaMuons = cms.Sequence( 
	#muonPFIsolationDepositsSequence +
	#muonPFIsolationValuesSequence
)

