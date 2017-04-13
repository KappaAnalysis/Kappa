import FWCore.ParameterSet.Config as cms

nEventsTotal = cms.EDProducer("EventWeightCountProducer",
                         srcGenEventInfo = cms.InputTag("generator"),
                         isMC = cms.bool(False),
                         countNegWeightsOnly = cms.bool(False)
                        )
nNegEventsTotal = cms.EDProducer("EventWeightCountProducer",
                         srcGenEventInfo = cms.InputTag("generator"),
                         isMC = cms.bool(False),
                         countNegWeightsOnly = cms.bool(True)
                        )

nEventsFiltered = cms.EDProducer("EventWeightCountProducer",
                         srcGenEventInfo = cms.InputTag("generator"),
                         isMC = cms.bool(False),
                         countNegWeightsOnly = cms.bool(False)
                        )
nNegEventsFiltered = cms.EDProducer("EventWeightCountProducer",
                         srcGenEventInfo = cms.InputTag("generator"),
                         isMC = cms.bool(False),
                         countNegWeightsOnly = cms.bool(True)
                        )
