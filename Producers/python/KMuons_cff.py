import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## Isodeposits for muons
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi import *
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi import *
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi import *

pfmuIsoDepositPFCandidates = cms.EDProducer(
    "CandIsoDepositProducer",
    src = cms.InputTag("muons"),
    MultipleDepositsFlag = cms.bool(False),
    trackType = cms.string('candidate'),
    ExtractorPSet = cms.PSet(
        Diff_z = cms.double(99999.99),
        ComponentName = cms.string('CandViewExtractor'),
        DR_Max = cms.double(1.0),
        Diff_r = cms.double(99999.99),
        inputCandView = cms.InputTag("particleFlow"),
        DR_Veto = cms.double(1e-05),
        DepositLabel = cms.untracked.string('')
        )
    )

## ------------------------------------------------------------------------
## Definition of sequences

## run this to create particle flow based isodeposits for muons, which are
## expected fro mthe KMuonProducer 
makeKappaMuons = cms.Sequence(
    pfmuIsoDepositPFCandidates
    )


