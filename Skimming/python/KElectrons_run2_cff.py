#-# Copyright (c) 2014 - All Rights Reserved
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools

cmssw_version_number = tools.get_cmssw_version_number()

## ------------------------------------------------------------------------
## Electron ID for Run 2
## CutBased:
## https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedElectronIdentificationRun2
## MVA:
## https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2

## ------------------------------------------------------------------------
## PAT electorn configuration
##  - electron Id sources
##  - switch generator matches off
##  - switch embedding off (not needed and dangerous for conversion veto)
from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import *
from PhysicsTools.PatAlgos.producersLayer1.electronProducer_cfi import *

patElectrons.electronIDSources = cms.PSet(
	## cut based Id
	cutBasedElectronID_Spring15_25ns_V1_standalone_loose  = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-loose"),
	cutBasedElectronID_Spring15_25ns_V1_standalone_medium = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-medium"),
	cutBasedElectronID_Spring15_25ns_V1_standalone_tight  = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-tight"),
	cutBasedElectronID_Spring15_25ns_V1_standalone_veto  = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-veto"),
	## MVA based Id
	ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values = cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values"),
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


## Set up electron ID (VID framework)
from PhysicsTools.SelectorUtils.tools.vid_id_tools import setupAllVIDIdsInModule, setupVIDElectronSelection

# https://github.com/ikrav/EgammaWork/blob/v1/ElectronNtupler/test/runElectrons_VID_MVA_PHYS14_demo.py
from PhysicsTools.SelectorUtils.tools.vid_id_tools import switchOnVIDElectronIdProducer, DataFormat
from RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cff import *

def setupElectrons(process):
	switchOnVIDElectronIdProducer(process, DataFormat.AOD)
	my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Spring15_25ns_V1_cff',
			 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring15_25ns_nonTrig_V1_cff']
	for idmod in my_id_modules:
		setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)


## for electron iso
# https://github.com/ajgilbert/ICHiggsTauTau/blob/master/test/higgstautau_new_cfg.py#L349-L384
from CommonTools.ParticleFlow.Isolation.pfElectronIsolation_cff import *
elPFIsoValueCharged04PFIdPFIso = elPFIsoValueCharged04PFId.clone()
elPFIsoValueChargedAll04PFIdPFIso = elPFIsoValueChargedAll04PFId.clone()
elPFIsoValueGamma04PFIdPFIso = elPFIsoValueGamma04PFId.clone()
elPFIsoValueNeutral04PFIdPFIso = elPFIsoValueNeutral04PFId.clone()
elPFIsoValuePU04PFIdPFIso = elPFIsoValuePU04PFId.clone()

elPFIsoValueGamma04PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.08)','EcalBarrel:ConeVeto(0.08)'))
elPFIsoValueNeutral04PFIdPFIso.deposits[0].vetos = (cms.vstring())
elPFIsoValuePU04PFIdPFIso.deposits[0].vetos = (cms.vstring())
elPFIsoValueCharged04PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.015)'))
elPFIsoValueChargedAll04PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.015)','EcalBarrel:ConeVeto(0.01)'))

electronPFIsolationValuesSequence = cms.Sequence(
	elPFIsoValueCharged04PFIdPFIso+
	elPFIsoValueChargedAll04PFIdPFIso+
	elPFIsoValueGamma04PFIdPFIso+
	elPFIsoValueNeutral04PFIdPFIso+
	elPFIsoValuePU04PFIdPFIso
)
elPFIsoDepositCharged.src = cms.InputTag("patElectrons")
elPFIsoDepositChargedAll.src = cms.InputTag("patElectrons")
elPFIsoDepositNeutral.src = cms.InputTag("patElectrons")
elPFIsoDepositGamma.src = cms.InputTag("patElectrons")
elPFIsoDepositPU.src = cms.InputTag("patElectrons")

# electron/muon PF iso sequence
pfElectronIso = cms.Sequence(
	electronPFIsolationDepositsSequence +
	electronPFIsolationValuesSequence
)

# rho for electron iso
from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
kt6PFJetsForIsolation = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
kt6PFJetsForIsolation.Rho_EtaMax = cms.double(2.5)


## ------------------------------------------------------------------------
## Definition of sequences
## run this to produce patElectrons w/o generator match or trigger match
## and with MVA electron ID
makeKappaElectrons = cms.Sequence(
    egmGsfElectronIDSequence *
    patElectrons *
    pfElectronIso *
    kt6PFJetsForIsolation
    )

