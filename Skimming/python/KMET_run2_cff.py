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
        U     = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru_7_4_X_miniAOD_25NS_July2015.root'),
        DPhi  = cms.FileInPath('RecoMET/METPUSubtraction/data/gbrphi_7_4_X_miniAOD_25NS_July2015.root'),
        CovU1 = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru1cov_7_4_X_miniAOD_25NS_July2015.root'),
        CovU2 = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru2cov_7_4_X_miniAOD_25NS_July2015.root') )

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

metMVAMT.srcLeptons = cms.VInputTag("mvaMETMuons", "mvaMETTausMT")
metMVAMT.permuteLeptons = cms.bool(True)

metMVATT.srcLeptons = cms.VInputTag("mvaMETTausTT", "mvaMETTausTT")
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

def configureMVAMetForAOD(process):
		process.kappaTuple.active += cms.vstring('BasicMET')                  ## produce/save KappaMET
		process.kappaTuple.active += cms.vstring('MET')                       ## produce/save KappaPFMET and MVA MET
		process.ak4PFJets.src = cms.InputTag("particleFlow")
		process.ak4PFJets.doAreaFastjet = cms.bool(True)
		process.pfMetMVA.srcVertices = cms.InputTag("offlinePrimaryVertices")
		process.puJetIdForPFMVAMEt.jec =  cms.string('AK4PF')
		process.puJetIdForPFMVAMEt.vertexes = cms.InputTag("offlinePrimaryVertices")
		process.puJetIdForPFMVAMEt.rho = cms.InputTag("fixedGridRhoFastjetAll")
		# Todo for miniAOD: find a selector that works in pat Taus and slimmedElectrons
		process.metMVAEM.srcLeptons = cms.VInputTag("gedGsfElectrons", "muons" )
		process.metMVAET.srcLeptons = cms.VInputTag("gedGsfElectrons", "hpsPFTauProducer")
		process.metMVAMT.srcLeptons = cms.VInputTag("muons"    , "hpsPFTauProducer")
		process.metMVATT.srcLeptons = cms.VInputTag("hpsPFTauProducer"     , "hpsPFTauProducer")
		process.metMVAEM.srcVertices = cms.InputTag("offlinePrimaryVertices")
		process.metMVAET.srcVertices = cms.InputTag("offlinePrimaryVertices")
		process.metMVAMT.srcVertices = cms.InputTag("offlinePrimaryVertices")
		process.metMVATT.srcVertices = cms.InputTag("offlinePrimaryVertices")
		process.metMVAEM.srcPFCandidates = cms.InputTag("particleFlow")
		process.metMVAET.srcPFCandidates = cms.InputTag("particleFlow")
		process.metMVAMT.srcPFCandidates = cms.InputTag("particleFlow")
		process.metMVATT.srcPFCandidates = cms.InputTag("particleFlow")
		process.makeKappaMET = cms.Sequence( 
		                process.ak4PFJets * 
		                process.calibratedAK4PFJetsForPFMVAMEt * 
		                process.mvaMETJets * 
		                process.puJetIdForPFMVAMEt * 
		                process.metMVAEM * 
		                process.metMVAET * 
		                process.metMVAMT * 
		                process.metMVATT )

		## Standard MET and GenMet from pat::MET
		#process.kappaTuple.active += cms.vstring('PatMET')
		## Write MVA MET to KMETs. To check what happens on AOD
		kappaTuple.active += cms.vstring('PatMETs')
		kappaTuple.PatMETs.whitelist = cms.vstring(
		                                                   "metMVAEM",
		                                                   "metMVAET",
		                                                   "metMVAMT",
		                                                   "metMVATT"
		                                                    )
	
def configureMVAMetForMiniAOD(process):
		process.ak4PFJets.src = cms.InputTag("packedPFCandidates")
		process.ak4PFJets.doAreaFastjet = cms.bool(True)
		process.pfMetMVA.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.puJetIdForPFMVAMEt.jec =  cms.string('AK4PF')
		process.puJetIdForPFMVAMEt.vertexes = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.puJetIdForPFMVAMEt.rho = cms.InputTag("fixedGridRhoFastjetAll")
		# Todo for miniAOD: find a selector that works in pat Taus and slimmedElectrons
		process.metMVAEM.srcLeptons = cms.VInputTag("slimmedElectrons", "slimmedMuons" )
		process.metMVAET.srcLeptons = cms.VInputTag("slimmedElectrons", "slimmedTaus")
		process.metMVAMT.srcLeptons = cms.VInputTag("slimmedMuons"    , "slimmedTaus")
		process.metMVATT.srcLeptons = cms.VInputTag("slimmedTaus"     , "slimmedTaus")
		process.metMVAEM.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.metMVAET.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.metMVAMT.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.metMVATT.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
		process.metMVAEM.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.metMVAET.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.metMVAMT.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.metMVATT.srcPFCandidates = cms.InputTag("packedPFCandidates")
		process.makeKappaMET = cms.Sequence( 
		                process.ak4PFJets *
		                process.calibratedAK4PFJetsForPFMVAMEt * 
		                process.mvaMETJets * 
		                process.puJetIdForPFMVAMEt * 
		                process.metMVAEM * 
		                process.metMVAET * 
		                process.metMVAMT * 
		                process.metMVATT )


def configurePFMetForMiniAOD(process, data=False):

	# do produce pfMet and No-HF pfMet, both raw and T1 corrected
	from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
	jecUncertaintyFile="PhysicsTools/PatUtils/data/Summer15_50nsV4_DATA_UncertaintySources_AK4PFchs.txt"

	runMetCorAndUncFromMiniAOD(process, isData=data, jecUncFile=jecUncertaintyFile )
	process.noHFCands = cms.EDFilter("CandPtrSelector", src=cms.InputTag("packedPFCandidates"), cut=cms.string("abs(pdgId)!=1 && abs(pdgId)!=2 && abs(eta)<3.0") )
	runMetCorAndUncFromMiniAOD(process, isData=data, pfCandColl=cms.InputTag("noHFCands"), jecUncFile=jecUncertaintyFile,  postfix="NoHF" )

	process.patPFMet.computeMETSignificance = cms.bool(True)
	process.patPFMetNoHF.computeMETSignificance = cms.bool(True)
	process.pfMet.calculateSignificance = cms.bool(True)
	process.pfMetNoHF.calculateSignificance = cms.bool(True)
	from RecoMET.METProducers.METSignificanceParams_cfi import METSignificanceParams
	process.pfMet.parameters = METSignificanceParams
	process.pfMet.srcMet = cms.InputTag("pfMet")
	process.pfMet.srcJets = cms.InputTag("slimmedJets")
	process.pfMet.srcLeptons = cms.VInputTag("slimmedTaus", "slimmedElectrons", "slimmedMuons")
	process.pfMetNoHF.parameters = METSignificanceParams
	process.pfMetNoHF.srcMet = cms.InputTag("pfMetNoHF")
	process.pfMetNoHF.srcJets = cms.InputTag("slimmedJets")
	process.pfMetNoHF.srcLeptons = cms.VInputTag("slimmedTaus", "slimmedElectrons", "slimmedMuons")
	process.pfMetNoHF.srcCandidates = cms.InputTag("noHFCands")

	# temporary fix from Missing ET mailing list
	process.patMETs.addGenMET  = cms.bool(False)
	process.patJets.addGenJetMatch = cms.bool(False)
	process.patJets.addGenPartonMatch = cms.bool(False)
	process.patJets.addPartonJetMatch = cms.bool(False)
	process.makePFMET = cms.Sequence( 
		                process.ak4PFJets *
		                process.pfCHS *
		                process.ak4PFJetsCHS *
		                process.pfMet *
		                process.genMetExtractor *
		                process.patJetCorrFactors *
		                process.patJets *
		                process.patPFMetT1T2Corr *
		                process.patPFMetTxyCorr *
		                process.noHFCands *
		                process.pfCHSNoHF *
		                process.pfMetNoHF *
		                process.patPFMetNoHF *
		                process.ak4PFJetsCHSNoHF *
		                process.patJetCorrFactorsNoHF *
		                process.patJetsNoHF *
		                process.patPFMetT1T2CorrNoHF *
		                process.patPFMetTxyCorrNoHF *
		                process.patPFMetT1NoHF
		)
