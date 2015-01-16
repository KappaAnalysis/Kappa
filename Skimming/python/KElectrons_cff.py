import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## POG recommended MVA based electron Id:
##  - from electron POG TWiki. Check access from HTauTau2ElecAnalysis53x.cc,
##    l1778.
##  - works for patElectron level, not for gsfElectron
from EgammaAnalysis.ElectronTools.electronIdMVAProducer_cfi import *

electronIdMVA = cms.Sequence(
	mvaTrigV0+
	mvaTrigNoIPV0+
	mvaNonTrigV0
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
	mvaTrigV0           = cms.InputTag("mvaTrigV0"          ),
	mvaTrigNoIPV0       = cms.InputTag("mvaTrigNoIPV0"      ),
	mvaNonTrigV0        = cms.InputTag("mvaNonTrigV0"       ),
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
