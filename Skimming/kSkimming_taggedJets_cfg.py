import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0])) + "/Kappa/")

## ------------------------------------------------------------------------
## import skeleton process KAPPA
from Kappa.Producers.KSkimming_template_cfg import *

## test file for EKP
process.source.fileNames     = cms.untracked.vstring('file:///storage/6/fcolombo/TTH_Inclusive_M-125_8TeV_pythia6_AODSIM_PU_S10_START53_V7A-v1_0009E1F7-FD09-E211-8955-001E673986B0.root')
## test file for lxplus
#process.source.fileNames      = cms.untracked.vstring('')

process.maxEvents.input       = 100                             ## number of events to be processed (-1 = all in file)
process.kappaTuple.outputFile = 'kappaTuple_taggedJets.root'    ## name of output file
process.kappaTuple.active     = cms.vstring('PFTaggedJets')     ## produce KappaPFTaggedJets
process.kappaTuple.verbose    = cms.int32(0)                    ## verbosity level
process.kappaTuple.PFTaggedJets = cms.PSet(
                     process.kappaNoCut,
                     process.kappaNoRegEx,
                     taggers = cms.vstring(
                         "QGlikelihood", "QGmlp",
                         "TrackCountingHighEffBJetTags", "TrackCountingHighPurBJetTags", 
                         "JetProbabilityBJetTags", "JetBProbabilityBJetTags", 
                         "SoftElectronBJetTags", "SoftMuonBJetTags", "SoftMuonByIP3dBJetTags", "SoftMuonByPtBJetTags",
                         "SimpleSecondaryVertexBJetTags", 
                         "CombinedSecondaryVertexBJetTags", "CombinedSecondaryVertexMVABJetTags",
                         "puJetIDFullLoose", "puJetIDFullMedium", "puJetIDFullTight",
                         "puJetIDCutbasedLoose", "puJetIDCutbasedMedium", "puJetIDCutbasedTight" 
                     ),
                     AK5PFTaggedJets = cms.PSet(
                         src = cms.InputTag("ak5PFJets"),
                         QGtagger = cms.InputTag("AK5PFJetsQGTagger"),
                         Btagger = cms.InputTag("ak5PF"),
                         PUJetID = cms.InputTag("ak5PFPuJetMva"),
                         PUJetID_full = cms.InputTag("full"),
                     ),
                     AK5PFTaggedJetsCHS = cms.PSet(
                         src = cms.InputTag("ak5PFJetsCHS"),
                         QGtagger = cms.InputTag("AK5PFJetsCHSQGTagger"),
                         Btagger = cms.InputTag("ak5PFCHS"),
                         PUJetID = cms.InputTag("ak5PFCHSPuJetMva"),
                         PUJetID_full = cms.InputTag("full"),
                     ),
                  )

## ------------------------------------------------------------------------
## declare edm OutputModule (expects a path 'p'), uncommented if wanted
process.edmOut = cms.OutputModule("PoolOutputModule",
                               fileName = cms.untracked.string('patTuple_taggedJets.root'),          ## name of output file 
                               SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ), ## save only events passing the full path
                               outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')  ## save each edm object that has been produced by process KAPPA 
                               )
process.kappaOut+=process.edmOut

## ------------------------------------------------------------------------
## KappaPFTaggedJets
process.load("Kappa.Producers.KPFTaggedJets_cff")
process.load("Kappa.Producers.KPFCandidates_cff")

## And let it run
process.p = cms.Path(
    process.makePFBRECO *
    process.makePFJets *
    process.makePFJetsCHS *
    process.makeQGTagging *
    process.makeBTagging *
    process.makePUJetID
    )

