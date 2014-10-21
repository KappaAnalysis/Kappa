import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## POG recommended MVA based electron Id:
##  - from electron POG TWiki. Check access from HTauTau2ElecAnalysis53x.cc,
##    l1778.
##  - works for patElectron level, not for gsfElectron

## Modification for new MVA Electron ID for Run 2
## https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
## Instructions for using new MVA-training:
## 1. download git repository as described at https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
## 2. run scramv1 b in src directory

from EgammaAnalysis.ElectronTools.electronIdMVAProducer_CSA14_cfi import *
from EgammaAnalysis.ElectronTools.egmGsfElectronIDs_cff import *
electronIdMVA = cms.Sequence(
    egmGsfElectronIDSequence+
    mvaTrigV050nsCSA14+
    mvaTrigV025nsCSA14+
    mvaNonTrigV050nsCSA14+
    mvaNonTrigV025nsCSA14
    )

## ------------------------------------------------------------------------
## PAT electorn configuration
##  - electron Id sources
##  - switch generator matches off
##  - switch embedding off (not needed and dangerous for conversion veto)
from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import *
from PhysicsTools.PatAlgos.producersLayer1.electronProducer_cfi import *

patElectrons.electronIDSources = cms.PSet(
	## default cut based Id
	eidRobustLoose      = cms.InputTag("eidRobustLoose"     ),
	eidRobustTight      = cms.InputTag("eidRobustTight"     ),
	eidLoose            = cms.InputTag("eidLoose"           ),
	eidTight            = cms.InputTag("eidTight"           ),
	eidRobustHighEnergy = cms.InputTag("eidRobustHighEnergy"),
	## MVA based Id
	mvaTrigV050nsCSA14  = cms.InputTag("mvaTrigV050nsCSA14"          ),
	mvaTrigV025nsCSA14  = cms.InputTag("mvaTrigV025nsCSA14"          ),
	mvaNonTrigV050nsCSA14 = cms.InputTag("mvaNonTrigV050nsCSA14"     ),
	mvaNonTrigV025nsCSA14 = cms.InputTag("mvaNonTrigV025nsCSA14"     ),
)
patElectrons.addGenMatch                   = False
patElectrons.embedGenMatch                 = False
patElectrons.genParticleMatch              = ""
patElectrons.embedGsfElectronCore          = False
patElectrons.embedGsfTrack                 = False
patElectrons.embedSuperCluster             = False
patElectrons.embedPflowSuperCluster        = False
patElectrons.embedSeedCluster              = False
patElectrons.embedBasicClusters            = False
patElectrons.embedPreshowerClusters        = False
patElectrons.embedPflowBasicClusters       = False
patElectrons.embedPflowPreshowerClusters   = False
patElectrons.embedPFCandidate              = False
patElectrons.embedTrack                    = False
patElectrons.embedRecHits                  = False
patElectrons.embedHighLevelSelection.pvSrc = "goodOfflinePrimaryVertices"

## ------------------------------------------------------------------------
## Definition of sequences
## run this to produce patElectrons w/o generator match or trigger match
## and with MVA electron ID

makeKappaElectrons = cms.Sequence(
    electronIdMVA *
    patElectrons
    )
