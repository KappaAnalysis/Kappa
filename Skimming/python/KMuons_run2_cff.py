from Kappa.Skimming.KMuons_cff import *

from CommonTools.ParticleFlow.Isolation.pfMuonIsolation_cff import *

muPFIsoValueCharged04PFIso = muPFIsoValueCharged04.clone()
muPFIsoValueChargedAll04PFIso = muPFIsoValueChargedAll04.clone()
muPFIsoValueGamma04PFIso = muPFIsoValueGamma04.clone()
muPFIsoValueNeutral04PFIso = muPFIsoValueNeutral04.clone()
muPFIsoValuePU04PFIso = muPFIsoValuePU04.clone()

muonPFIsolationValuesSequence = cms.Sequence(
	muPFIsoValueCharged04PFIso+
	muPFIsoValueChargedAll04PFIso+
	muPFIsoValueGamma04PFIso+
	muPFIsoValueNeutral04PFIso+
	muPFIsoValuePU04PFIso
	)
muPFIsoDepositCharged.src = cms.InputTag("muons")
muPFIsoDepositChargedAll.src = cms.InputTag("muons")
muPFIsoDepositNeutral.src = cms.InputTag("muons")
muPFIsoDepositGamma.src = cms.InputTag("muons")
muPFIsoDepositPU.src = cms.InputTag("muons")

pfMuonIso = cms.Sequence( 
	muonPFIsolationDepositsSequence +
	muonPFIsolationValuesSequence
)

makeKappaMuons *= pfMuonIso

