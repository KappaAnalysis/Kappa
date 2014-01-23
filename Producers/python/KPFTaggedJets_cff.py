import FWCore.ParameterSet.Config as cms


## ------------------------------------------------------------------------
## Create good primary vertices to be used for PF association
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
from RecoJets.JetProducers.ak5PFJets_cfi import ak5PFJets
from RecoHI.HiJetAlgos.HiRecoPFJets_cff import ak7PFJets

goodOfflinePrimaryVertices = cms.EDFilter("PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices')
)
ak5PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
ak7PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')

## CHS Jets with the NoPU sequence
from CommonTools.ParticleFlow.PFBRECO_cff import *
pfPileUp.Vertices = cms.InputTag('goodOfflinePrimaryVertices')
pfPileUp.checkClosestZVertex = cms.bool(False)
ak5PFJetsCHS = ak5PFJets.clone( src = cms.InputTag('pfNoPileUp') )
ak7PFJetsCHS = ak7PFJets.clone( src = cms.InputTag('pfNoPileUp') )


## ------------------------------------------------------------------------
## Gluon tagging
## https://twiki.cern.ch/twiki/bin/viewauth/CMS/GluonTag
from QuarkGluonTagger.EightTeV.QGTagger_RecoJets_cff import *

QGTagger.srcJets = cms.InputTag("ak5PFJets")
AK5PFJetsQGTagger = QGTagger.clone()
AK5PFJetsCHSQGTagger = QGTagger.clone(
    srcJets = cms.InputTag("ak5PFJetsCHS"),
    useCHS = cms.untracked.bool(True)
    )
AK7PFJetsQGTagger = QGTagger.clone(
    srcJets = cms.InputTag("ak7PFJets")
    )
AK7PFJetsCHSQGTagger = QGTagger.clone(
        srcJets = cms.InputTag("ak7PFJetsCHS"),
        useCHS = cms.untracked.bool(True)
    )


## ------------------------------------------------------------------------
## B-tagging
## https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets
from RecoJets.JetAssociationProducers.ic5JetTracksAssociatorAtVertex_cfi import *
#from RecoJets.JetAssociationProducers.ak5JTA_cff import *
#from RecoBTag.Configuration.RecoBTag_cff import *
#from RecoBTag.SoftLepton.softLepton_cff import *
#from RecoBTag.ImpactParameter.impactParameter_cfi import impactParameterTagInfos
#from RecoBTag.ImpactParameter.trackCountingHighEffBJetTags_cfi import trackCountingHighEffBJetTags
#from RecoBTag.ImpactParameter.trackCountingHighPurBJetTags_cfi import trackCountingHighPurBJetTags
#from RecoBTag.ImpactParameter.jetProbabilityBJetTags_cfi import jetProbabilityBJetTags
#from RecoBTag.ImpactParameter.jetBProbabilityBJetTags_cfi import jetBProbabilityBJetTags
#from RecoBTag.Configuration.RecoBTag_cff import secondaryVertexTagInfos
#from RecoBTag.SecondaryVertex.secondaryVertex_cff import simpleSecondaryVertexBJetTags
#from RecoBTag.SecondaryVertex.combinedSecondaryVertexBJetTags_cfi import combinedSecondaryVertexBJetTags
#from RecoBTag.SecondaryVertex.combinedSecondaryVertexMVABJetTags_cfi import combinedSecondaryVertexMVABJetTags
#from RecoBTag.SoftLepton.softPFElectronTagInfos_cfi import softPFElectronsTagInfos
#from RecoBTag.SoftLepton.SoftLeptonByPt_cfi import softPFElectronByPtBJetTags
#from RecoBTag.SoftLepton.softMuonTagInfos_cfi import softMuonTagInfos
#from RecoBTag.SoftLepton.SoftLeptonByPt_cfi import softPFMuonByPtBJetTags
#from RecoBTag.SoftLepton.SoftLeptonByIP3d_cfi import softPFMuonByIP3dBJetTags

# create a ak5PF jets and tracks association


ak5PFJetTracksAssociatorAtVertex        = ic5JetTracksAssociatorAtVertex.clone()
#ak5PFJetTracksAssociatorAtVertex.jets   = "ak5PFJets"
#ak5PFJetTracksAssociatorAtVertex.tracks = "generalTracks"

## impact parameter b-tag
#ak5PFImpactParameterTagInfos           = impactParameterTagInfos.clone()
#ak5PFImpactParameterTagInfos.jetTracks = "ak5PFJetTracksAssociatorAtVertex"
#ak5PFTrackCountingHighEffBJetTags          = trackCountingHighEffBJetTags.clone()
#ak5PFTrackCountingHighEffBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
#ak5PFTrackCountingHighPurBJetTags          = trackCountingHighPurBJetTags.clone()
#ak5PFTrackCountingHighPurBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
#ak5PFJetProbabilityBJetTags          = jetProbabilityBJetTags.clone()
#ak5PFJetProbabilityBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))
#ak5PFJetBProbabilityBJetTags          = jetBProbabilityBJetTags.clone()
#ak5PFJetBProbabilityBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFImpactParameterTagInfos"))

## secondary vertex b-tag
#ak5PFSecondaryVertexTagInfos                 = secondaryVertexTagInfos.clone()
#ak5PFSecondaryVertexTagInfos.trackIPTagInfos = "ak5PFImpactParameterTagInfos"
#ak5PFSimpleSecondaryVertexBJetTags          = simpleSecondaryVertexBJetTags.clone()
#ak5PFSimpleSecondaryVertexBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFSecondaryVertexTagInfos"))
#ak5PFCombinedSecondaryVertexBJetTags          = combinedSecondaryVertexBJetTags.clone()
#ak5PFCombinedSecondaryVertexBJetTags.tagInfos = cms.VInputTag(
        #cms.InputTag("ak5PFImpactParameterTagInfos"),
        #cms.InputTag("ak5PFSecondaryVertexTagInfos"))
#ak5PFCombinedSecondaryVertexMVABJetTags          = combinedSecondaryVertexMVABJetTags.clone()
#ak5PFCombinedSecondaryVertexMVABJetTags.tagInfos = cms.VInputTag(
        #cms.InputTag("ak5PFImpactParameterTagInfos"),
        #cms.InputTag("ak5PFSecondaryVertexTagInfos"))

## soft electron b-tag
#ak5PFsoftPFElectronsTagInfos      = softPFElectronsTagInfos.clone()
#ak5PFsoftPFElectronsTagInfos.jets = "ak5PFJets"
#ak5PFSoftElectronBJetTags          = softPFElectronByPtBJetTags.clone()
#ak5PFSoftElectronBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFsoftPFElectronsTagInfos"))

## soft muon b-tag
#ak5PFSoftMuonTagInfos      = softMuonTagInfos.clone()
#ak5PFSoftMuonTagInfos.jets = "ak5PFJets"
#ak5PFSoftMuonBJetTags          = softPFMuonByPtBJetTags.clone()
#ak5PFSoftMuonBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFSoftMuonTagInfos"))
#ak5PFSoftMuonByIP3dBJetTags          = softPFMuonByIP3dBJetTags.clone()
#ak5PFSoftMuonByIP3dBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFSoftMuonTagInfos"))
#ak5PFSoftMuonByPtBJetTags          = softPFMuonByPtBJetTags.clone()
#ak5PFSoftMuonByPtBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFSoftMuonTagInfos"))

## prepare a sequence running the ak5PF modules
#ak5PFJetTracksAssociator = cms.Sequence(
    #ak5PFJetTracksAssociatorAtVertex
    #)

#ak5PFJetBtaggingIP = cms.Sequence(
    #ak5PFImpactParameterTagInfos * (
    #ak5PFTrackCountingHighEffBJetTags +
    #ak5PFTrackCountingHighPurBJetTags +
    #ak5PFJetProbabilityBJetTags +
    #ak5PFJetBProbabilityBJetTags
    #))

#ak5PFJetBtaggingSV = cms.Sequence(
    #ak5PFImpactParameterTagInfos *
    #ak5PFSecondaryVertexTagInfos * (
    #ak5PFSimpleSecondaryVertexBJetTags +
    #ak5PFCombinedSecondaryVertexBJetTags +
    #ak5PFCombinedSecondaryVertexMVABJetTags
    #))

#ak5PFJetBtaggingEle = cms.Sequence(
    #softPFElectronByPtBJetTags *
    #ak5PFsoftPFElectronsTagInfos *
    #ak5PFSoftElectronBJetTags
    #)

#ak5PFJetBtaggingMu = cms.Sequence(
    #ak5PFSoftMuonTagInfos * (
    #ak5PFSoftMuonBJetTags +
    #ak5PFSoftMuonByIP3dBJetTags +
    #ak5PFSoftMuonByPtBJetTags
    #))

#ak5PFJetBtagging = cms.Sequence(
    #ak5PFJetBtaggingIP +
    #ak5PFJetBtaggingSV +
    #ak5PFJetBtaggingEle +
    #ak5PFJetBtaggingMu
    #)


## AK5 CHS
## create a ak5PF jets and tracks association
#ak5PFCHSJetTracksAssociatorAtVertex        = ic5JetTracksAssociatorAtVertex.clone()
#ak5PFCHSJetTracksAssociatorAtVertex.jets   = "ak5PFJetsCHS"
#ak5PFCHSJetTracksAssociatorAtVertex.tracks = "generalTracks"

## impact parameter b-tag
#ak5PFCHSImpactParameterTagInfos           = impactParameterTagInfos.clone()
#ak5PFCHSImpactParameterTagInfos.jetTracks = "ak5PFCHSJetTracksAssociatorAtVertex"
#ak5PFCHSTrackCountingHighEffBJetTags          = trackCountingHighEffBJetTags.clone()
#ak5PFCHSTrackCountingHighEffBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
#ak5PFCHSTrackCountingHighPurBJetTags          = trackCountingHighPurBJetTags.clone()
#ak5PFCHSTrackCountingHighPurBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
#ak5PFCHSJetProbabilityBJetTags          = jetProbabilityBJetTags.clone()
#ak5PFCHSJetProbabilityBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))
#ak5PFCHSJetBProbabilityBJetTags          = jetBProbabilityBJetTags.clone()
#ak5PFCHSJetBProbabilityBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"))

## secondary vertex b-tag
#ak5PFCHSSecondaryVertexTagInfos                 = secondaryVertexTagInfos.clone()
#ak5PFCHSSecondaryVertexTagInfos.trackIPTagInfos = "ak5PFCHSImpactParameterTagInfos"
#ak5PFCHSSimpleSecondaryVertexBJetTags          = simpleSecondaryVertexBJetTags.clone()
#ak5PFCHSSimpleSecondaryVertexBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSSecondaryVertexTagInfos"))
#ak5PFCHSCombinedSecondaryVertexBJetTags          = combinedSecondaryVertexBJetTags.clone()
#ak5PFCHSCombinedSecondaryVertexBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"), cms.InputTag("ak5PFCHSSecondaryVertexTagInfos"))
#ak5PFCHSCombinedSecondaryVertexMVABJetTags          = combinedSecondaryVertexMVABJetTags.clone()
#ak5PFCHSCombinedSecondaryVertexMVABJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSImpactParameterTagInfos"), cms.InputTag("ak5PFCHSSecondaryVertexTagInfos"))

## soft electron b-tag
#ak5PFCHSsoftPFElectronsTagInfos      = softPFElectronsTagInfos.clone()
#ak5PFCHSsoftPFElectronsTagInfos.jets = "ak5PFJetsCHS"
#ak5PFCHSSoftElectronBJetTags          = softPFElectronByPtBJetTags.clone()
#ak5PFCHSSoftElectronBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSsoftPFElectronsTagInfos"))

## soft muon b-tag
#ak5PFCHSSoftMuonTagInfos      = softMuonTagInfos.clone()
#ak5PFCHSSoftMuonTagInfos.jets = "ak5PFJetsCHS"
#ak5PFCHSSoftMuonBJetTags          = softPFMuonByPtBJetTags.clone()
#ak5PFCHSSoftMuonBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSSoftMuonTagInfos"))
#ak5PFCHSSoftMuonByIP3dBJetTags          = softPFMuonByIP3dBJetTags.clone()
#ak5PFCHSSoftMuonByIP3dBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSSoftMuonTagInfos"))
#ak5PFCHSSoftMuonByPtBJetTags          = softPFMuonByPtBJetTags.clone()
#ak5PFCHSSoftMuonByPtBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak5PFCHSSoftMuonTagInfos"))

## prepare a sequence running the modules
#ak5PFCHSJetTracksAssociator = cms.Sequence(
    #ak5PFCHSJetTracksAssociatorAtVertex
    #)

#ak5PFCHSJetBtaggingIP = cms.Sequence(
    #ak5PFCHSImpactParameterTagInfos * (
    #ak5PFCHSTrackCountingHighEffBJetTags +
    #ak5PFCHSTrackCountingHighPurBJetTags +
    #ak5PFCHSJetProbabilityBJetTags +
    #ak5PFCHSJetBProbabilityBJetTags
    #))

#ak5PFCHSJetBtaggingSV = cms.Sequence(
    #ak5PFCHSImpactParameterTagInfos * 
    #ak5PFCHSSecondaryVertexTagInfos * (
    #ak5PFCHSSimpleSecondaryVertexBJetTags +
    #ak5PFCHSCombinedSecondaryVertexBJetTags +
    #ak5PFCHSCombinedSecondaryVertexMVABJetTags
    #))

#ak5PFCHSJetBtaggingEle = cms.Sequence(
    #softPFElectronByPtBJetTags *
    #ak5PFCHSsoftPFElectronsTagInfos *
    #ak5PFCHSSoftElectronBJetTags
    #)

#ak5PFCHSJetBtaggingMu = cms.Sequence(
    #ak5PFCHSSoftMuonTagInfos * (
    #ak5PFCHSSoftMuonBJetTags +
    #ak5PFCHSSoftMuonByIP3dBJetTags +
    #ak5PFCHSSoftMuonByPtBJetTags
    #))

#ak5PFCHSJetBtagging = cms.Sequence(
    #ak5PFCHSJetBtaggingIP +
    #ak5PFCHSJetBtaggingSV +
    #ak5PFCHSJetBtaggingEle +
    #ak5PFCHSJetBtaggingMu
    #)


## AK7
#ak7PFJetTracksAssociatorAtVertex        = ic5JetTracksAssociatorAtVertex.clone()
#ak7PFJetTracksAssociatorAtVertex.jets   = "ak7PFJets"
#ak7PFJetTracksAssociatorAtVertex.tracks = "generalTracks"

## impact parameter b-tag
#ak7PFImpactParameterTagInfos           = impactParameterTagInfos.clone()
#ak7PFImpactParameterTagInfos.jetTracks = "ak7PFJetTracksAssociatorAtVertex"
#ak7PFTrackCountingHighEffBJetTags          = trackCountingHighEffBJetTags.clone()
#ak7PFTrackCountingHighEffBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFImpactParameterTagInfos"))
#ak7PFTrackCountingHighPurBJetTags          = trackCountingHighPurBJetTags.clone()
#ak7PFTrackCountingHighPurBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFImpactParameterTagInfos"))
#ak7PFJetProbabilityBJetTags          = jetProbabilityBJetTags.clone()
#ak7PFJetProbabilityBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFImpactParameterTagInfos"))
#ak7PFJetBProbabilityBJetTags          = jetBProbabilityBJetTags.clone()
#ak7PFJetBProbabilityBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFImpactParameterTagInfos"))

## secondary vertex b-tag
#ak7PFSecondaryVertexTagInfos                 = secondaryVertexTagInfos.clone()
#ak7PFSecondaryVertexTagInfos.trackIPTagInfos = "ak7PFImpactParameterTagInfos"
#ak7PFSimpleSecondaryVertexBJetTags          = simpleSecondaryVertexBJetTags.clone()
#ak7PFSimpleSecondaryVertexBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFSecondaryVertexTagInfos"))
#ak7PFCombinedSecondaryVertexBJetTags          = combinedSecondaryVertexBJetTags.clone()
#ak7PFCombinedSecondaryVertexBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFImpactParameterTagInfos"), cms.InputTag("ak7PFSecondaryVertexTagInfos"))
#ak7PFCombinedSecondaryVertexMVABJetTags          = combinedSecondaryVertexMVABJetTags.clone()
#ak7PFCombinedSecondaryVertexMVABJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFImpactParameterTagInfos"), cms.InputTag("ak7PFSecondaryVertexTagInfos"))

## soft electron b-tag
#ak7PFsoftPFElectronsTagInfos      = softPFElectronsTagInfos.clone()
#ak7PFsoftPFElectronsTagInfos.jets = "ak7PFJets"
#ak7PFSoftElectronBJetTags          = softPFElectronByPtBJetTags.clone()
#ak7PFSoftElectronBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFsoftPFElectronsTagInfos"))

## soft muon b-tag
#ak7PFSoftMuonTagInfos      = softMuonTagInfos.clone()
#ak7PFSoftMuonTagInfos.jets = "ak7PFJets"
#ak7PFSoftMuonBJetTags          = softPFMuonByPtBJetTags.clone()
#ak7PFSoftMuonBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFSoftMuonTagInfos"))
#ak7PFSoftMuonByIP3dBJetTags          = softPFMuonByIP3dBJetTags.clone()
#ak7PFSoftMuonByIP3dBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFSoftMuonTagInfos"))
#ak7PFSoftMuonByPtBJetTags          = softPFMuonByPtBJetTags.clone()
#ak7PFSoftMuonByPtBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFSoftMuonTagInfos"))

## prepare a sequence running the ak7PF modules
#ak7PFJetTracksAssociator = cms.Sequence(
    #ak7PFJetTracksAssociatorAtVertex
    #)

#ak7PFJetBtaggingIP = cms.Sequence(
    #ak7PFImpactParameterTagInfos * (
    #ak7PFTrackCountingHighEffBJetTags +
    #ak7PFTrackCountingHighPurBJetTags +
    #ak7PFJetProbabilityBJetTags +
    #ak7PFJetBProbabilityBJetTags
    #))

#ak7PFJetBtaggingSV = cms.Sequence(
    #ak7PFImpactParameterTagInfos *
    #ak7PFSecondaryVertexTagInfos * (
    #ak7PFSimpleSecondaryVertexBJetTags +
    #ak7PFCombinedSecondaryVertexBJetTags +
    #ak7PFCombinedSecondaryVertexMVABJetTags
    #))

#ak7PFJetBtaggingEle = cms.Sequence(
    #softPFElectronByPtBJetTags *
    #ak7PFsoftPFElectronsTagInfos *
    #ak7PFSoftElectronBJetTags
    #)

#ak7PFJetBtaggingMu = cms.Sequence(
    #ak7PFSoftMuonTagInfos * (
    #ak7PFSoftMuonBJetTags +
    #ak7PFSoftMuonByIP3dBJetTags +
    #ak7PFSoftMuonByPtBJetTags
    #))

#ak7PFJetBtagging = cms.Sequence(
    #ak7PFJetBtaggingIP +
    #ak7PFJetBtaggingSV +
    #ak7PFJetBtaggingEle +
    #ak7PFJetBtaggingMu
    #)


## ak7 CHS
## create a ak7PF jets and tracks association
#ak7PFCHSJetTracksAssociatorAtVertex        = ic5JetTracksAssociatorAtVertex.clone()
#ak7PFCHSJetTracksAssociatorAtVertex.jets   = "ak7PFJetsCHS"
#ak7PFCHSJetTracksAssociatorAtVertex.tracks = "generalTracks"

## impact parameter b-tag
#ak7PFCHSImpactParameterTagInfos           = impactParameterTagInfos.clone()
#ak7PFCHSImpactParameterTagInfos.jetTracks = "ak7PFCHSJetTracksAssociatorAtVertex"
#ak7PFCHSTrackCountingHighEffBJetTags          = trackCountingHighEffBJetTags.clone()
#ak7PFCHSTrackCountingHighEffBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSImpactParameterTagInfos"))
#ak7PFCHSTrackCountingHighPurBJetTags          = trackCountingHighPurBJetTags.clone()
#ak7PFCHSTrackCountingHighPurBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSImpactParameterTagInfos"))
#ak7PFCHSJetProbabilityBJetTags          = jetProbabilityBJetTags.clone()
#ak7PFCHSJetProbabilityBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSImpactParameterTagInfos"))
#ak7PFCHSJetBProbabilityBJetTags          = jetBProbabilityBJetTags.clone()
#ak7PFCHSJetBProbabilityBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSImpactParameterTagInfos"))

## secondary vertex b-tag
#ak7PFCHSSecondaryVertexTagInfos                 = secondaryVertexTagInfos.clone()
#ak7PFCHSSecondaryVertexTagInfos.trackIPTagInfos = "ak7PFCHSImpactParameterTagInfos"
#ak7PFCHSSimpleSecondaryVertexBJetTags          = simpleSecondaryVertexBJetTags.clone()
#ak7PFCHSSimpleSecondaryVertexBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSSecondaryVertexTagInfos"))
#ak7PFCHSCombinedSecondaryVertexBJetTags          = combinedSecondaryVertexBJetTags.clone()
#ak7PFCHSCombinedSecondaryVertexBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSImpactParameterTagInfos"), cms.InputTag("ak7PFCHSSecondaryVertexTagInfos"))
#ak7PFCHSCombinedSecondaryVertexMVABJetTags          = combinedSecondaryVertexMVABJetTags.clone()
#ak7PFCHSCombinedSecondaryVertexMVABJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSImpactParameterTagInfos"), cms.InputTag("ak7PFCHSSecondaryVertexTagInfos"))

## soft electron b-tag
#ak7PFCHSsoftPFElectronsTagInfos      = softPFElectronsTagInfos.clone()
#ak7PFCHSsoftPFElectronsTagInfos.jets = "ak7PFJetsCHS"
#ak7PFCHSSoftElectronBJetTags          = softPFElectronByPtBJetTags.clone()
#ak7PFCHSSoftElectronBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSsoftPFElectronsTagInfos"))

## soft muon b-tag
#ak7PFCHSSoftMuonTagInfos      = softMuonTagInfos.clone()
#ak7PFCHSSoftMuonTagInfos.jets = "ak7PFJetsCHS"
#ak7PFCHSSoftMuonBJetTags          = softPFMuonByPtBJetTags.clone()
#ak7PFCHSSoftMuonBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSSoftMuonTagInfos"))
#ak7PFCHSSoftMuonByIP3dBJetTags          = softPFMuonByIP3dBJetTags.clone()
#ak7PFCHSSoftMuonByIP3dBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSSoftMuonTagInfos"))
#ak7PFCHSSoftMuonByPtBJetTags          = softPFMuonByPtBJetTags.clone()
#ak7PFCHSSoftMuonByPtBJetTags.tagInfos = cms.VInputTag(cms.InputTag("ak7PFCHSSoftMuonTagInfos"))

## prepare a sequence running the modules
#ak7PFCHSJetTracksAssociator = cms.Sequence(
    #ak7PFCHSJetTracksAssociatorAtVertex
    #)

#ak7PFCHSJetBtaggingIP = cms.Sequence(
    #ak7PFCHSImpactParameterTagInfos * (
    #ak7PFCHSTrackCountingHighEffBJetTags +
    #ak7PFCHSTrackCountingHighPurBJetTags +
    #ak7PFCHSJetProbabilityBJetTags +
    #ak7PFCHSJetBProbabilityBJetTags
    #))

#ak7PFCHSJetBtaggingSV = cms.Sequence(
    #ak7PFCHSImpactParameterTagInfos *
    #ak7PFCHSSecondaryVertexTagInfos * (
    #ak7PFCHSSimpleSecondaryVertexBJetTags +
    #ak7PFCHSCombinedSecondaryVertexBJetTags +
    #ak7PFCHSCombinedSecondaryVertexMVABJetTags
    #))

#ak7PFCHSJetBtaggingEle = cms.Sequence(
    #softPFElectronByPtBJetTags *
    #ak7PFCHSsoftPFElectronsTagInfos *
    #ak7PFCHSSoftElectronBJetTags
    #)

#ak7PFCHSJetBtaggingMu = cms.Sequence(
    #ak7PFCHSSoftMuonTagInfos * (
    #ak7PFCHSSoftMuonBJetTags +
    #ak7PFCHSSoftMuonByIP3dBJetTags +
    #ak7PFCHSSoftMuonByPtBJetTags
    #))

#ak7PFCHSJetBtagging = cms.Sequence(
    #ak7PFCHSJetBtaggingIP +
    #ak7PFCHSJetBtaggingSV +
    #ak7PFCHSJetBtaggingEle +
    #ak7PFCHSJetBtaggingMu
    #)


## ------------------------------------------------------------------------
## Pile-Up Jet ID
from CMGTools.External.pujetidsequence_cff import *

# AK5
ak5PFPuJetId = puJetId.clone(
    jets = cms.InputTag("ak5PFJets"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
)

ak5PFPuJetMva = puJetMva.clone(
    jets = cms.InputTag("ak5PFJets"),
    jetids = cms.InputTag("ak5PFPuJetId"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
)

# AK5 CHS
ak5PFCHSPuJetId = puJetIdChs.clone(
    jets = cms.InputTag("ak5PFJetsCHS"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
)

ak5PFCHSPuJetMva = puJetMvaChs.clone(
    jets = cms.InputTag("ak5PFJetsCHS"),
    jetids = cms.InputTag("ak5PFCHSPuJetId"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
)

# ak7
ak7PFPuJetId = puJetId.clone(
    jets = cms.InputTag("ak7PFJets"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
)

ak7PFPuJetMva = puJetMva.clone(
    jets = cms.InputTag("ak7PFJets"),
    jetids = cms.InputTag("ak7PFPuJetId"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
)

# ak7 CHS
ak7PFCHSPuJetId = puJetIdChs.clone(
    jets = cms.InputTag("ak7PFJetsCHS"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
)

ak7PFCHSPuJetMva = puJetMvaChs.clone(
    jets = cms.InputTag("ak7PFJetsCHS"),
    jetids = cms.InputTag("ak7PFCHSPuJetId"),
    applyJec = cms.bool(True),
    inputIsCorrected = cms.bool(False),
)


## ------------------------------------------------------------------------
## Definition of main sequences
makePfCHS = cms.Sequence(
    goodOfflinePrimaryVertices *
    PFBRECO
    )

makePFJets = cms.Sequence(
    ak5PFJets *
    ak7PFJets
    )

makePFJetsCHS = cms.Sequence(
    ak5PFJetsCHS *
    ak7PFJetsCHS
    )

makeQGTagging = cms.Sequence(
    QuarkGluonTagger *
    AK5PFJetsQGTagger *
    AK5PFJetsCHSQGTagger *
    AK7PFJetsQGTagger *
    AK7PFJetsCHSQGTagger
    )

makeBTagging = cms.Sequence(
    #ak5PFJetTracksAssociator
	    #ak5PFJetBtagging
    #ak5PFCHSJetTracksAssociator * ak5PFCHSJetBtagging *
    #ak7PFJetTracksAssociator * ak7PFJetBtagging *
    #ak7PFCHSJetTracksAssociator * ak7PFCHSJetBtagging
    )

makePUJetID = cms.Sequence(
    ak5PFPuJetId *
    ak5PFPuJetMva *
    ak5PFCHSPuJetId *
    ak5PFCHSPuJetMva *
    ak7PFPuJetId *
    ak7PFPuJetMva *
    ak7PFCHSPuJetId *
    ak7PFCHSPuJetMva
    )


makeKappaPFTaggedJets = cms.Sequence(
    makePfCHS *
    makePFJets *
    makePFJetsCHS *
    makeQGTagging *
    makeBTagging *
    makePUJetID
    )
