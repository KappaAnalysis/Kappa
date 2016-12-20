#-# Copyright (c) 2013 - All Rights Reserved
#-#   Joram Berger <joram.berger@cern.ch>

# Kappa test: CMSSW 5.3.22, 7.2.2, 7.4.14
# Kappa test: scram arch slc6_amd64_gcc472, slc6_amd64_gcc481, slc6_amd64_gcc491
# Kappa test: checkout script scripts/checkoutTauRefit.sh, scripts/checkoutTauRefit.sh, scripts/checkoutTauRefit.sh

import FWCore.ParameterSet.Config as cms

testfile = 'file:///storage/6/fcolombo/kappatest/input/mc11.root'
globaltag = 'START53_V27::All'
maxevents = 100
print "GT:", globaltag, "| maxevents:", maxevents, "| file:", testfile

# Basic process setup -----------------------------------------------------
process = cms.Process('KAPPA')
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(testfile))
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(maxevents))
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.Geometry.GeometryIdeal_cff')
process.load('Configuration.Geometry.GeometryPilot2_cff')
process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi')
process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi')
process.load('TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi')
process.load('RecoMuon.DetLayers.muonDetLayerGeometry_cfi')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.GlobalTag.globaltag = globaltag

# Configure Kappa ---------------------------------------------------------
process.load('Kappa.Producers.KTuple_cff')
process.kappatuple = cms.EDAnalyzer('KTuple',
    process.kappaTupleDefaultsBlock,
    outputFile=cms.string("kappa.root"),
)
process.kappatuple.active = cms.vstring(
    'LV', 'TrackSummary', 'VertexSummary', 'BeamSpot',
    'MET', 'BasicJets', 'GenInfo', 'GenParticles', 'Jets' #Muons
)
process.pathKappa = cms.Path(process.kappatuple)
