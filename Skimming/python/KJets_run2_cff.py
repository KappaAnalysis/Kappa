#-# Copyright (c) 2014 - All Rights Reserved
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>

import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
## Create ak5 jets from all pf candidates and from pfNoPileUp candidates
##  - note that this requires that goodOfflinePrimaryVertices and PFBRECO
##    has been run beforehand. e.g. using the sequence makePFBRECO from
##    KPFCandidates_cff.py
from RecoJets.JetProducers.ak5PFJets_cfi import ak5PFJets

ak5PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
ak5PFJetsCHS = ak5PFJets.clone( src = cms.InputTag('pfNoPileUp') )

### ------------------------------------------------------------------------
### Gluon tagging
###  - https://twiki.cern.ch/twiki/bin/viewauth/CMS/GluonTag
##from QuarkGluonTagger.EightTeV.QGTagger_RecoJets_cff import *

##QGTagger.srcJets     = cms.InputTag('ak5PFJets')
##AK5PFJetsQGTagger    = QGTagger.clone()
##AK5PFJetsCHSQGTagger = QGTagger.clone( srcJets = cms.InputTag('ak5PFJetsCHS'), useCHS = cms.untracked.bool(True) )

## ------------------------------------------------------------------------
## B-tagging (for ak5 jets)
##  - https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets
from RecoJets.JetAssociationProducers.ic5JetTracksAssociatorAtVertex_cfi import *
from RecoBTag.Configuration.RecoBTag_cff import *
from RecoBTag.SoftLepton.softPFElectronTagInfos_cfi import softPFElectronsTagInfos
from RecoBTag.SoftLepton.SoftLeptonByPt_cfi import softPFElectronByPtBJetTags
from RecoBTag.SoftLepton.softMuonTagInfos_cfi import softMuonTagInfos
from RecoBTag.SoftLepton.SoftLeptonByPt_cfi import softPFMuonByPtBJetTags
from RecoBTag.SoftLepton.SoftLeptonByIP3d_cfi import softPFMuonByIP3dBJetTags

## create a ak5PF jets and tracks association
ak5PFJetNewTracksAssociatorAtVertex           = ic5JetTracksAssociatorAtVertex.clone()
ak5PFJetNewTracksAssociatorAtVertex.jets      = "ak5PFJets"
ak5PFJetNewTracksAssociatorAtVertex.tracks    = "generalTracks"

## impact parameter b-tag
ak5PFImpactParameterTagInfos                  = impactParameterTagInfos.clone()
ak5PFImpactParameterTagInfos.jetTracks        = "ak5PFJetNewTracksAssociatorAtVertex"
ak5PFTrackCountingHighEffBJetTags             = trackCountingHighEffBJetTags.clone()
ak5PFTrackCountingHighEffBJetTags.tagInfos    = cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
ak5PFTrackCountingHighPurBJetTags             = trackCountingHighPurBJetTags.clone()
ak5PFTrackCountingHighPurBJetTags.tagInfos    = cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
ak5PFJetProbabilityBJetTags                   = jetProbabilityBJetTags.clone()
ak5PFJetProbabilityBJetTags.tagInfos          = cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
ak5PFJetBProbabilityBJetTags                  = jetBProbabilityBJetTags.clone()
ak5PFJetBProbabilityBJetTags.tagInfos         = cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))

## secondary vertex b-tag
ak5PFSecondaryVertexTagInfos                  = secondaryVertexTagInfos.clone()
ak5PFSecondaryVertexTagInfos.trackIPTagInfos  = "ak5PFImpactParameterTagInfos"
ak5PFSimpleSecondaryVertexBJetTags            = simpleSecondaryVertexBJetTags.clone()
ak5PFSimpleSecondaryVertexBJetTags.tagInfos   = cms.VInputTag(cms.InputTag("ak5PFSecondaryVertexTagInfos"))
ak5PFCombinedSecondaryVertexBJetTags          = combinedSecondaryVertexBJetTags.clone()
ak5PFCombinedSecondaryVertexBJetTags.tagInfos = cms.VInputTag(
    cms.InputTag("ak5PFImpactParameterTagInfos"),
    cms.InputTag("ak5PFSecondaryVertexTagInfos")
    )
ak5PFCombinedSecondaryVertexMVABJetTags       = combinedSecondaryVertexMVABJetTags.clone()
ak5PFCombinedSecondaryVertexMVABJetTags.tagInfos = cms.VInputTag(
    cms.InputTag("ak5PFImpactParameterTagInfos"),
    cms.InputTag("ak5PFSecondaryVertexTagInfos")
    )

## soft electron b-tag
ak5PFsoftPFElectronsTagInfos                  = softPFElectronsTagInfos.clone()
ak5PFsoftPFElectronsTagInfos.jets             = "ak5PFJets"
ak5PFSoftElectronBJetTags                     = softPFElectronByPtBJetTags.clone()
ak5PFSoftElectronBJetTags.tagInfos            = cms.VInputTag(cms.InputTag("ak5PFsoftPFElectronsTagInfos"))

## soft muon b-tag
ak5PFSoftMuonTagInfos                         = softMuonTagInfos.clone()
ak5PFSoftMuonTagInfos.jets                    = "ak5PFJets"
ak5PFSoftMuonBJetTags                         = softPFMuonByPtBJetTags.clone()
ak5PFSoftMuonBJetTags.tagInfos                = cms.VInputTag(cms.InputTag("ak5PFSoftMuonTagInfos"))
ak5PFSoftMuonByIP3dBJetTags                   = softPFMuonByIP3dBJetTags.clone()
ak5PFSoftMuonByIP3dBJetTags.tagInfos          = cms.VInputTag(cms.InputTag("ak5PFSoftMuonTagInfos"))
ak5PFSoftMuonByPtBJetTags                     = softPFMuonByPtBJetTags.clone()
ak5PFSoftMuonByPtBJetTags.tagInfos            = cms.VInputTag(cms.InputTag("ak5PFSoftMuonTagInfos"))

## ------------------------------------------------------------------------
## Definition of sequences

## run this to create track-jet associations needed for most b-taggers
ak5PFJetTracksAssociator = cms.Sequence(
    ak5PFJetNewTracksAssociatorAtVertex
    )

## run this to create all products needed for impact parameter based
## b-taggers
ak5PFJetBtaggingIP = cms.Sequence(
    ak5PFImpactParameterTagInfos * (
    ak5PFTrackCountingHighEffBJetTags +
    ak5PFTrackCountingHighPurBJetTags +
    ak5PFJetProbabilityBJetTags +
    ak5PFJetBProbabilityBJetTags
    ))

## run this to create all products needed for secondary vertex based
## b-taggers
ak5PFJetBtaggingSV = cms.Sequence(
    ak5PFImpactParameterTagInfos *
    ak5PFSecondaryVertexTagInfos * (
    ak5PFSimpleSecondaryVertexBJetTags +
    ak5PFCombinedSecondaryVertexBJetTags +
    ak5PFCombinedSecondaryVertexMVABJetTags
    ))

## run this to create all products needed for soft electron b-taggers
ak5PFJetBtaggingEle = cms.Sequence(
    ak5PFsoftPFElectronsTagInfos *
    ak5PFSoftElectronBJetTags
    )

## run this to create all objects needed to soft muon b-taggers
ak5PFJetBtaggingMu = cms.Sequence(
    ak5PFSoftMuonTagInfos * (
    ak5PFSoftMuonBJetTags +
    ak5PFSoftMuonByIP3dBJetTags +
    ak5PFSoftMuonByPtBJetTags
    ))

## combine all sequences to create all objects needed for all available
## b-taggers
ak5PFJetBtagging = cms.Sequence(
    ak5PFJetBtaggingIP +
    ak5PFJetBtaggingSV +
    ak5PFJetBtaggingEle +
    ak5PFJetBtaggingMu
    )

## ------------------------------------------------------------------------
## B-tagging for (ak5 CHS jets)
##  - https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets

## create a ak5PF jets and tracks association
ak5PFCHSNewJetTracksAssociatorAtVertex        = ic5JetTracksAssociatorAtVertex.clone()
ak5PFCHSNewJetTracksAssociatorAtVertex.jets   = "ak5PFJetsCHS"
ak5PFCHSNewJetTracksAssociatorAtVertex.tracks = "generalTracks"

## impact parameter b-tag
ak5PFCHSImpactParameterTagInfos               = impactParameterTagInfos.clone()
ak5PFCHSImpactParameterTagInfos.jetTracks     = "ak5PFCHSNewJetTracksAssociatorAtVertex"
ak5PFCHSTrackCountingHighEffBJetTags          = trackCountingHighEffBJetTags.clone()
ak5PFCHSTrackCountingHighEffBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
ak5PFCHSTrackCountingHighPurBJetTags          = trackCountingHighPurBJetTags.clone()
ak5PFCHSTrackCountingHighPurBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
ak5PFCHSJetProbabilityBJetTags                = jetProbabilityBJetTags.clone()
ak5PFCHSJetProbabilityBJetTags.tagInfos       = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
ak5PFCHSJetBProbabilityBJetTags               = jetBProbabilityBJetTags.clone()
ak5PFCHSJetBProbabilityBJetTags.tagInfos      = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))

## secondary vertex b-tag
ak5PFCHSSecondaryVertexTagInfos                  = secondaryVertexTagInfos.clone()
ak5PFCHSSecondaryVertexTagInfos.trackIPTagInfos  = "ak5PFCHSImpactParameterTagInfos"
ak5PFCHSSimpleSecondaryVertexBJetTags            = simpleSecondaryVertexBJetTags.clone()
ak5PFCHSSimpleSecondaryVertexBJetTags.tagInfos   = cms.VInputTag(cms.InputTag("ak5PFCHSSecondaryVertexTagInfos"))
ak5PFCHSCombinedSecondaryVertexBJetTags          = combinedSecondaryVertexBJetTags.clone()
ak5PFCHSCombinedSecondaryVertexBJetTags.tagInfos = cms.VInputTag(
    cms.InputTag("ak5PFCHSImpactParameterTagInfos"),
    cms.InputTag("ak5PFCHSSecondaryVertexTagInfos")
    )
ak5PFCHSCombinedSecondaryVertexMVABJetTags       = combinedSecondaryVertexMVABJetTags.clone()
ak5PFCHSCombinedSecondaryVertexMVABJetTags.tagInfos = cms.VInputTag(
    cms.InputTag("ak5PFCHSImpactParameterTagInfos"),
    cms.InputTag("ak5PFCHSSecondaryVertexTagInfos")
    )

## soft electron b-tag
ak5PFCHSsoftPFElectronsTagInfos               = softPFElectronsTagInfos.clone()
ak5PFCHSsoftPFElectronsTagInfos.jets          = "ak5PFJetsCHS"
ak5PFCHSSoftElectronBJetTags                  = softPFElectronByPtBJetTags.clone()
ak5PFCHSSoftElectronBJetTags.tagInfos         = cms.VInputTag(cms.InputTag("ak5PFCHSsoftPFElectronsTagInfos"))

## soft muon b-tag
ak5PFCHSSoftMuonTagInfos                      = softMuonTagInfos.clone()
ak5PFCHSSoftMuonTagInfos.jets                 = "ak5PFJetsCHS"
ak5PFCHSSoftMuonBJetTags                      = softPFMuonByPtBJetTags.clone()
ak5PFCHSSoftMuonBJetTags.tagInfos             = cms.VInputTag(cms.InputTag("ak5PFCHSSoftMuonTagInfos"))
ak5PFCHSSoftMuonByIP3dBJetTags                = softPFMuonByIP3dBJetTags.clone()
ak5PFCHSSoftMuonByIP3dBJetTags.tagInfos       = cms.VInputTag(cms.InputTag("ak5PFCHSSoftMuonTagInfos"))
ak5PFCHSSoftMuonByPtBJetTags                  = softPFMuonByPtBJetTags.clone()
ak5PFCHSSoftMuonByPtBJetTags.tagInfos         = cms.VInputTag(cms.InputTag("ak5PFCHSSoftMuonTagInfos"))

## ------------------------------------------------------------------------
## Definition of sequences

## run this to create track-jet associations needed for most b-taggers
ak5PFCHSJetTracksAssociator = cms.Sequence(
    ak5PFCHSNewJetTracksAssociatorAtVertex
    )

## run this to create all products needed for impact parameter based
## b-taggers
ak5PFCHSJetBtaggingIP = cms.Sequence(
    ak5PFCHSImpactParameterTagInfos * (
    ak5PFCHSTrackCountingHighEffBJetTags +
    ak5PFCHSTrackCountingHighPurBJetTags +
    ak5PFCHSJetProbabilityBJetTags +
    ak5PFCHSJetBProbabilityBJetTags
    ))

## run this to create all products needed for secondary vertex based
## b-taggers
ak5PFCHSJetBtaggingSV = cms.Sequence(
    ak5PFCHSImpactParameterTagInfos * 
    ak5PFCHSSecondaryVertexTagInfos * (
    ak5PFCHSSimpleSecondaryVertexBJetTags +
    ak5PFCHSCombinedSecondaryVertexBJetTags +
    ak5PFCHSCombinedSecondaryVertexMVABJetTags
    ))

## run this to create all products needed for soft electron b-taggers
ak5PFCHSJetBtaggingEle = cms.Sequence(
    ak5PFCHSsoftPFElectronsTagInfos *
    ak5PFCHSSoftElectronBJetTags
    )

## run this to create all objects needed to soft muon b-taggers
ak5PFCHSJetBtaggingMu = cms.Sequence(
    ak5PFCHSSoftMuonTagInfos * (
    ak5PFCHSSoftMuonBJetTags +
    ak5PFCHSSoftMuonByIP3dBJetTags +
    ak5PFCHSSoftMuonByPtBJetTags
    ))

## combine all sequences to create all objects needed for all available
## b-taggers
ak5PFCHSJetBtagging = cms.Sequence(
    ak5PFCHSJetBtaggingIP +
    ak5PFCHSJetBtaggingSV +
    ak5PFCHSJetBtaggingEle +
    ak5PFCHSJetBtaggingMu
    )

## ------------------------------------------------------------------------
## Pile-Up Jet ID
from RecoJets.JetProducers.PileupJetIDCutParams_cfi import full_5x_wp, full_5x_chs_wp

full_53x = cms.PSet(
    impactParTkThreshold = cms.double(1.) ,
    cutBased = cms.bool(False),
    tmvaWeights = cms.string("CondFormats/JetMETObjects/data/TMVAClassificationCategory_JetID_53X_Dec2012.weights.xml"),
    tmvaMethod = cms.string("JetIDMVAHighPt"),
    version = cms.int32(-1),
    tmvaVariables = cms.vstring(
        "nvtx",
        "dZ",
        "beta",
        "betaStar",
        "nCharged",
        "nNeutrals",
        "dR2Mean",
        "ptD",
        "frac01",
        "frac02",
        "frac03",
        "frac04",
        "frac05",
    ),
    tmvaSpectators = cms.vstring(
        "jetPt",
        "jetEta",
        "jetPhi"
    ),
    JetIdParams = full_5x_wp,
    label = cms.string("full")
    )

full_53x_chs = cms.PSet(
    impactParTkThreshold = cms.double(1.) ,
    cutBased = cms.bool(False),
    tmvaWeights = cms.string("CondFormats/JetMETObjects/data/TMVAClassificationCategory_JetID_53X_chs_Dec2012.weights.xml"),
    tmvaMethod = cms.string("JetIDMVAHighPt"),
    version = cms.int32(-1),
    tmvaVariables = cms.vstring(
        "nvtx",
        "dZ",
        "beta",
        "betaStar",
        "nCharged",
        "nNeutrals",
        "dR2Mean",
        "ptD",
        "frac01",
        "frac02",
        "frac03",
        "frac04",
        "frac05",
    ),
    tmvaSpectators = cms.vstring(
        "jetPt",
        "jetEta",
        "jetPhi"
    ),
    JetIdParams = full_5x_chs_wp,
    label = cms.string("full")
    )

pileupJetIdProducer = cms.EDProducer('PileupJetIdProducer',
                         produceJetIds = cms.bool(True),
                         jetids = cms.InputTag(""),
                         runMvas = cms.bool(True),
                         jets = cms.InputTag("ak5PFJets"),
                         vertexes = cms.InputTag("offlinePrimaryVertices"),
                         algos = cms.VPSet(cms.VPSet(full_53x)),                                     
                         rho     = cms.InputTag("fixedGridRhoFastjetAll"), ## TODO: change to "kt6PFJets"
                         jec     = cms.string("AK5PF"),
                         applyJec = cms.bool(True),
                         inputIsCorrected = cms.bool(False),                                     
                         residualsFromTxt = cms.bool(False),
                         residualsTxt     = cms.FileInPath("RecoJets/JetProducers/BuildFile.xml"),
    )

pileupJetIdProducerChs = pileupJetIdProducer.clone(
                         algos = cms.VPSet(cms.VPSet(full_53x_chs)),
                         jec     = cms.string("AK5PFchs"),
    )

ak5PFPuJetId = pileupJetIdProducer.clone(
    jets = cms.InputTag("ak5PFJets"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
    residualsTxt     = cms.FileInPath("RecoJets/JetProducers/BuildFile.xml"),
    )

ak5PFPuJetMva = pileupJetIdProducer.clone(
    jets = cms.InputTag("ak5PFJets"),
    jetids = cms.InputTag("ak5PFPuJetId"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
    residualsTxt     = cms.FileInPath("RecoJets/JetProducers/BuildFile.xml"),
    )

ak5PFCHSPuJetId = pileupJetIdProducerChs.clone(
    jets = cms.InputTag("ak5PFJetsCHS"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
    residualsTxt     = cms.FileInPath("RecoJets/JetProducers/BuildFile.xml"),
    )

ak5PFCHSPuJetMva = pileupJetIdProducerChs.clone(
    jets = cms.InputTag("ak5PFJetsCHS"),
    jetids = cms.InputTag("ak5PFCHSPuJetId"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
    residualsTxt     = cms.FileInPath("RecoJets/JetProducers/BuildFile.xml"),
    )

## ------------------------------------------------------------------------
## Definition of sequences

## run this to create ak5PF jets from goodOfflinePrimaryVertices collection 
makePFJets = cms.Sequence(
    ak5PFJets
    )

## run this to create ak5PF CHS jets from goodOfflinePrimaryVertices
## collection 
makePFJetsCHS = cms.Sequence(
    ak5PFJetsCHS
    )

### run this to create Quark-Gluon tag
##makeQGTagging = cms.Sequence(
    ##QuarkGluonTagger *
    ##AK5PFJetsQGTagger *
    ##AK5PFJetsCHSQGTagger
    ##)

## run this to create b-tags
makeBTagging = cms.Sequence(
    ak5PFJetTracksAssociator *
    ak5PFJetBtagging *
    ak5PFCHSJetTracksAssociator *
    ak5PFCHSJetBtagging
    )

## run this to create PU jet ID
makePUJetID = cms.Sequence(
    ak5PFPuJetId *
    ak5PFPuJetMva *
    ak5PFCHSPuJetId *
    ak5PFCHSPuJetMva
    )
