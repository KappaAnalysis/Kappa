#-# Copyright (c) 2014 - All Rights Reserved
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>

import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## POG recommended electron Id:
##  - works for patElectron level, not for gsfElectron

## Modification for new Electron ID for Run 2
## CutBased:
## https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedElectronIdentificationRun2
## MVA:
## https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
## Instructions for using new MVA-training:
## 1. download git repository as described at https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
## 2. run scramv1 b in src directory

from EgammaAnalysis.ElectronTools.electronIdMVAProducer_CSA14_cfi import *

electronIdMVA = cms.Sequence(
    mvaTrigV050nsCSA14+
    mvaTrigV025nsCSA14+
    mvaNonTrigV050nsCSA14+
    mvaNonTrigV025nsCSA14+
    mvaNonTrigV025nsPHYS14
    )

## ------------------------------------------------------------------------
## PAT electorn configuration
##  - electron Id sources
##  - switch generator matches off
##  - switch embedding off (not needed and dangerous for conversion veto)
from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import *
from PhysicsTools.PatAlgos.producersLayer1.electronProducer_cfi import *

patElectrons.electronIDSources = cms.PSet(
	## cut based Id
	cutBasedEleIdPHYS14Loose  = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-standalone-loose"),
	cutBasedEleIdPHYS14Medium = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-standalone-medium"),
	cutBasedEleIdPHYS14Tight  = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-standalone-tight"),
	cutBasedEleIdPHYS14Veto   = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-PHYS14-PU20bx25-V1-standalone-veto"),
	## MVA based Id
	mvaTrigV050nsCSA14        = cms.InputTag("mvaTrigV050nsCSA14"),
	mvaTrigV025nsCSA14        = cms.InputTag("mvaTrigV025nsCSA14"),
	mvaNonTrigV050nsCSA14     = cms.InputTag("mvaNonTrigV050nsCSA14"),
	mvaNonTrigV025nsCSA14     = cms.InputTag("mvaNonTrigV025nsCSA14"),
	mvaNonTrigV025nsPHYS14    = cms.InputTag("mvaNonTrigV025nsPHYS14"),
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

## for the Run 2 cutBased Id
# https://github.com/ikrav/ElectronWork/blob/master/ElectronNtupler/test/runIdDemoPrePHYS14AOD.py#L29-L56
from PhysicsTools.SelectorUtils.tools.vid_id_tools import setupAllVIDIdsInModule, setupVIDElectronSelection
from PhysicsTools.SelectorUtils.centralIDRegistry import central_id_registry
from RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cfi import *
egmGsfElectronIDSequence = cms.Sequence(egmGsfElectronIDs)
# Define which IDs we want to produce
# Each of these IDs contains all four standard cut-based ID working points 

def setupElectrons(process):
	my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_PHYS14_PU20bx25_V1_cff']
	for idmod in my_id_modules:
		setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)




makeKappaElectrons = cms.Sequence(
    egmGsfElectronIDSequence *
    electronIdMVA *
    patElectrons
    )

