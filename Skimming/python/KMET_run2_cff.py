#-# Copyright (c) 2014 - All Rights Reserved
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>
#-#   Thomas Mueller <tmuller@cern.ch>

import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## MVA MET following POG recommendations
##  - https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet#CMSSW_7_2_X_requires_slc6
##  - https://github.com/cms-met/cmssw/blob/72X-mvaMETForMiniAOD/RecoMET/METPUSubtraction/test/testMVAMetProducer.py
##  - MVA MET needs the calibrated jets and the selected leptons as close
##    in the selection as used for the final analysis. It is in the user's
##    responsibility to define those and to pass them on to the mvaMet
##    producer.

## conditions needed for the JEC applied inside the MVA MET
from JetMETCorrections.Configuration.JetCorrectionProducers_cff import *

## ------------------------------------------------------------------------
## calibrated jets and Type1 MET corrections as input for mvaMET producer
##  - NOTE: use "ak5PFL1FastL2L3" for MC / "ak5PFL1FastL2L3Residual" for
##    data

##  - NOTE: apparently "ak5PFL1FastL2L3" does not work
from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets

mvaMETJets = cms.EDProducer('PFJetCorrectionProducer',
    src = cms.InputTag('ak4PFJets'),
    correctors = cms.vstring("ak4PFL1FastL2L3")
    )

from RecoJets.JetProducers.pileupjetidproducer_cfi import pileupJetIdEvaluator
from RecoJets.JetProducers.PileupJetIDParams_cfi import JetIdParams
from RecoMET.METPUSubtraction.mvaPFMET_cff import calibratedAK4PFJetsForPFMVAMEt, puJetIdForPFMVAMEt
# the following two statements have been widely restricted and deactivated since they caused Kappa to crash
from JetMETCorrections.Type1MET.correctionTermsPfMetType1Type2_cff import corrPfMetType1
#from JetMETCorrections.Type1MET.correctedMet_cff import *

corrPfMetType1.jetCorrLabel = "ak4PFL1FastL2L3" 

## ------------------------------------------------------------------------
## muons as input for mvaMET producer
mvaMETMuons = cms.EDFilter("MuonSelector",
    src = cms.InputTag('muons'),
    cut = cms.string(
        "abs(eta)<2.1 & pt>15"                                      +
        ## muon ID
        "& isTrackerMuon"                                           +
        "& isPFMuon"                                                +
        "& globalTrack.isNonnull"                                   +
        "& innerTrack.hitPattern.numberOfValidPixelHits    >  0"    +
        "& innerTrack.normalizedChi2                       < 10"    +
        "& numberOfMatches                                 >  0"    +
        "& innerTrack.hitPattern.numberOfValidTrackerHits  >  5"    +
        "& globalTrack.hitPattern.numberOfValidHits        >  0"    +
        "& abs(innerTrack().dxy)                           <2.0"    +
        ## muon isolation (w/o deltaBeta, therefore weaker selection criteria)
        "& (pfIsolationR03.sumChargedHadronPt+pfIsolationR03.sumNeutralHadronEt+pfIsolationR03.sumPhotonEt)/pt < 0.3"
    ),
    filter = cms.bool(False)
    )

## ------------------------------------------------------------------------
## electrons as input for mvaMET producer
mvaMETElectrons = cms.EDFilter("GsfElectronSelector",
    src = cms.InputTag('gedGsfElectrons'),
    cut = cms.string(
        "abs(eta) < 2.3 && pt > 15"                                          +
        "&& gsfTrack.hitPattern().numberOfHits(\'MISSING_INNER_HITS\') == 0" + 
        ## electron ID for barrel electrons
        "&& ((abs(eta) < 1.4442  "                                           +
        "&& abs(deltaEtaSuperClusterTrackAtVtx)            < 0.007"          +
        "&& abs(deltaPhiSuperClusterTrackAtVtx)            < 0.8"            +
        "&& sigmaIetaIeta                                  < 0.01"           +
        "&& hcalOverEcal                                   < 0.15"           +
        "&& abs(1./superCluster.energy - 1./p)             < 0.05)"          +
        ## electron ID for endcap electrons
        "|| (abs(eta)  > 1.566 "                                             +
        "&& abs(deltaEtaSuperClusterTrackAtVtx)            < 0.009 "         +
        "&& abs(deltaPhiSuperClusterTrackAtVtx)            < 0.10"           +
        "&& sigmaIetaIeta                                  < 0.03"           +
        "&& hcalOverEcal                                   < 0.10"           +
        "&& abs(1./superCluster.energy - 1./p)             < 0.05))"         +
        ## electron isolation (w/o deltaBeta, therefore weaker selection criteria)
        "&& (pfIsolationVariables.sumChargedHadronPt+pfIsolationVariables.sumNeutralHadronEt)/et < 0.3"
        ),
    filter = cms.bool(False)
    )                                                

## ------------------------------------------------------------------------
## taus as input for mvaMET producer
##  - NOTE that the selection for taus depends on the final state
mvaMETTausET = cms.EDFilter("PFTauSelector",
    src = cms.InputTag('hpsPFTauProducer'),
    BooleanOperator = cms.string("and"),
    discriminators = cms.VPSet(              
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByDecayModeFinding"                       ), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByLooseCombinedIsolationDBSumPtCorr3Hits" ), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByLooseElectronRejection"                 ), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByLooseMuonRejection"                     ), selectionCut=cms.double(0.5)) 
        ),
    cut = cms.string("abs(eta) < 2.3 && pt > 20.0 "),
    filter = cms.bool(False)
    )

mvaMETTausMT = cms.EDFilter("PFTauSelector",
    src = cms.InputTag('hpsPFTauProducer'),
    BooleanOperator = cms.string("and"),
    discriminators = cms.VPSet(              
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByDecayModeFinding"                       ), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByLooseCombinedIsolationDBSumPtCorr3Hits" ), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByLooseElectronRejection"                 ), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByTightMuonRejection"                     ), selectionCut=cms.double(0.5)) 
        ),
    cut = cms.string("abs(eta) < 2.3 && pt > 20.0 "),
    filter = cms.bool(False)
    )

mvaMETTausTT = cms.EDFilter("PFTauSelector",
    src = cms.InputTag('hpsPFTauProducer'),
    BooleanOperator = cms.string("and"),
    discriminators = cms.VPSet(              
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByDecayModeFinding"                       ), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByMediumCombinedIsolationDBSumPtCorr3Hits"), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByLooseElectronRejection"                 ), selectionCut=cms.double(0.5)),
        cms.PSet( discriminator=cms.InputTag("hpsPFTauDiscriminationByLooseMuonRejection"                     ), selectionCut=cms.double(0.5)) 
        ),
    cut = cms.string("abs(eta) < 2.3 && pt > 20.0 "),
    filter = cms.bool(False)
    )

## ------------------------------------------------------------------------
## MVA MET
##  - srcLeptons nees a collectino of lepton as close as possible to the
##    leptons selected for the analysis.
##  - srcCorrJets/srcUncorrJets should correspond to the jets as used in
##    the analysis. 
from RecoJets.JetProducers.PileupJetIDParams_cfi import JetIdParams

from RecoMET.METPUSubtraction.mvaPFMET_cff import pfMVAMEt as pfMetMVA

pfMetMVA.inputFileNames = cms.PSet(
        U     = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru_7_4_X_miniAOD_50NS_July2015.root'),
        DPhi  = cms.FileInPath('RecoMET/METPUSubtraction/data/gbrphi_7_4_X_miniAOD_50NS_July2015.root'),
        CovU1 = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru1cov_7_4_X_miniAOD_50NS_July2015.root'),
        CovU2 = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru2cov_7_4_X_miniAOD_50NS_July2015.root') )

metMVAEM = cms.EDProducer('PFMETProducerMVATauTau', 
                             **pfMetMVA.parameters_())#pfMVAMEt.clone()
metMVAET = cms.EDProducer('PFMETProducerMVATauTau', 
                             **pfMetMVA.parameters_())#pfMVAMEt.clone()
metMVAMT = cms.EDProducer('PFMETProducerMVATauTau', 
                             **pfMetMVA.parameters_())#pfMVAMEt.clone()
metMVATT = cms.EDProducer('PFMETProducerMVATauTau', 
                             **pfMetMVA.parameters_())#pfMVAMEt.clone()

## specify the leptons similar to those used in the analysis (channel specific)
metMVAEM.srcLeptons = cms.VInputTag("mvaMETElectrons", "mvaMETMuons" )
metMVAEM.permuteLeptons = cms.bool(True)

metMVAET.srcLeptons = cms.VInputTag("mvaMETElectrons", "mvaMETTausET")
metMVAET.permuteLeptons = cms.bool(True)

metMVAMT.srcLeptons = cms.VInputTag("mvaMETMuons"    , "mvaMETMuons")
metMVAMT.permuteLeptons = cms.bool(True)

metMVATT.srcLeptons = cms.VInputTag("mvaMETTausTT"    , "mvaMETTausTT")
metMVATT.permuteLeptons = cms.bool(True)
## ------------------------------------------------------------------------
## Definition of sequences
makeKappaMET = cms.Sequence(
    ak4PFJets *
    calibratedAK4PFJetsForPFMVAMEt *
    mvaMETJets *
    puJetIdForPFMVAMEt *
    mvaMETMuons *
    mvaMETTausET *
    mvaMETTausMT *
    mvaMETTausTT *
    mvaMETElectrons *
    metMVAEM * 
    metMVAET *
    metMVAMT *
    metMVATT 
    )
