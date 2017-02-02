#-# Copyright (c) 2014 - All Rights Reserved
#-#   Bastian Kargoll <bastian.kargoll@cern.ch>
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>

import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
##  rerun tau reconstruction sequence following POG recommendation:
##  https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Rerunning_of_the_tau_ID_on_MiniA


## since we run in the unscheduled mode the normal import fails. Maybe a customizer would also be helpfull.

from RecoTauTag.RecoTau.TauDiscriminatorTools import noPrediscriminants
from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import patDiscriminationByIsolationMVArun2v1raw as rerunDiscriminationByIsolationMVArun2v1raw
from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import patDiscriminationByIsolationMVArun2v1VLoose as rerunDiscriminationByIsolationMVArun2v1VLoose


rerunDiscriminationByIsolationMVArun2v1raw.PATTauProducer = cms.InputTag('slimmedTaus')
rerunDiscriminationByIsolationMVArun2v1raw.Prediscriminants = noPrediscriminants
rerunDiscriminationByIsolationMVArun2v1raw.loadMVAfromDB = cms.bool(True)
rerunDiscriminationByIsolationMVArun2v1raw.mvaName = cms.string("RecoTauTag_tauIdMVADBoldDMwLTv1")
rerunDiscriminationByIsolationMVArun2v1raw.mvaOpt = cms.string("DBoldDMwLT")
rerunDiscriminationByIsolationMVArun2v1raw.requireDecayMode = cms.bool(True)
rerunDiscriminationByIsolationMVArun2v1raw.verbosity = cms.int32(0)





rerunDiscriminationByIsolationMVArun2v1VLoose.PATTauProducer = cms.InputTag('slimmedTaus')
rerunDiscriminationByIsolationMVArun2v1VLoose.Prediscriminants = noPrediscriminants
rerunDiscriminationByIsolationMVArun2v1VLoose.toMultiplex = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1raw')
rerunDiscriminationByIsolationMVArun2v1VLoose.key = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1raw:category')
rerunDiscriminationByIsolationMVArun2v1VLoose.loadMVAfromDB = cms.bool(True)
rerunDiscriminationByIsolationMVArun2v1VLoose.mvaOutput_normalization = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_mvaOutput_normalization")
rerunDiscriminationByIsolationMVArun2v1VLoose.mapping = cms.VPSet(
			cms.PSet(
			category = cms.uint32(0),
			cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff90"),
			variable = cms.string("pt"),
		)
	)

rerunDiscriminationByIsolationMVArun2v1Loose = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
rerunDiscriminationByIsolationMVArun2v1Loose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff80")
rerunDiscriminationByIsolationMVArun2v1Medium = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
rerunDiscriminationByIsolationMVArun2v1Medium.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff70")
rerunDiscriminationByIsolationMVArun2v1Tight = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
rerunDiscriminationByIsolationMVArun2v1Tight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff60")
rerunDiscriminationByIsolationMVArun2v1VTight = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
rerunDiscriminationByIsolationMVArun2v1VTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff50")
rerunDiscriminationByIsolationMVArun2v1VVTight = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
rerunDiscriminationByIsolationMVArun2v1VVTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff40")



newslimmedTaus = cms.EDProducer("PATTauIdUpdater",
				  src = cms.InputTag("slimmedTaus"),
				  update_PATTauDiscriminators = cms.VInputTag(
				    cms.InputTag("rerunDiscriminationByIsolationMVArun2v1raw"),
				    cms.InputTag("rerunDiscriminationByIsolationMVArun2v1VLoose"),
				    cms.InputTag("rerunDiscriminationByIsolationMVArun2v1Loose"),
				    cms.InputTag("rerunDiscriminationByIsolationMVArun2v1Medium"),
				    cms.InputTag("rerunDiscriminationByIsolationMVArun2v1Tight"),
				    cms.InputTag("rerunDiscriminationByIsolationMVArun2v1VTight"),
				    cms.InputTag("rerunDiscriminationByIsolationMVArun2v1VVTight")
				   )
				  
				  
				  )




## ------------------------------------------------------------------------
## Definition of sequences

## run this to get latest greatest HPS taus
makeKappaTaus = cms.Sequence(
  rerunDiscriminationByIsolationMVArun2v1raw +
  rerunDiscriminationByIsolationMVArun2v1VLoose +
  rerunDiscriminationByIsolationMVArun2v1Loose +
  rerunDiscriminationByIsolationMVArun2v1Medium +
  rerunDiscriminationByIsolationMVArun2v1Tight +
  rerunDiscriminationByIsolationMVArun2v1VTight +
  rerunDiscriminationByIsolationMVArun2v1VVTight +
  newslimmedTaus
    )
