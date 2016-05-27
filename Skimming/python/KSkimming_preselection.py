import FWCore.ParameterSet.Config as cms

def do_preselection(process):
	process.selectedKappaTaus = cms.EDFilter("PATTauRefSelector", 
										src = cms.InputTag("slimmedTaus"),
										filter = cms.bool(False),
										cut = cms.string('pt > 20 && abs(eta) < 2.3') )
	process.selectedKappaMuons = cms.EDFilter("PATMuonRefSelector", 
										src = cms.InputTag("slimmedMuons"),
										filter = cms.bool(False),
										cut = cms.string('pt > 10 && abs(eta) < 2.4') )
	process.selectedKappaElectrons = cms.EDFilter("PATElectronRefSelector", 
										src = cms.InputTag("slimmedElectrons"),
										filter = cms.bool(False),
										cut = cms.string('pt > 13 && abs(eta) < 2.5 ') )
	process.allKappaLeptons = cms.EDProducer("CandViewMerger",
										src = cms.VInputTag("selectedKappaTaus", "selectedKappaMuons", "selectedKappaElectrons") )
	process.goodEventFilter = cms.EDFilter("CandViewCountFilter",
										src = cms.InputTag("allKappaLeptons"),
										minNumber = cms.uint32(2),
										filter = cms.bool(True) )
