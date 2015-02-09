#-# Copyright (c) 2013 - All Rights Reserved
#-#   Joram Berger <joram.berger@cern.ch>

# Kappa test: CMSSW 5.3.22
# Kappa test: scram arch slc5_amd64_gcc462
# Kappa test: checkout nix

import FWCore.ParameterSet.Config as cms


def getBaseConfig(globaltag, testfile="", maxevents=0, datatype='data'):
    """Testing config for skims with Kappa"""
    # Set the global tag and datatype for testing or by grid-control ---------
    data = (datatype == 'data')
    if data:
        testfile = 'file:/storage/8/dhaitz/testfiles/data_AOD_2012A.root'
        if '@' in globaltag:
            globaltag = 'FT53_V21A_AN6'
        maxevents = maxevents or 1000
    else:
        testfile = 'file:/storage/8/dhaitz/testfiles/mc11.root'
        if '@' in globaltag:
            globaltag = 'START53_V27'
        maxevents = maxevents or 1000
        datatype = 'mc'
    print "GT:", globaltag, "| TYPE:", datatype, "| maxevents:", maxevents, "| file:", testfile

    # Basic process setup -----------------------------------------------------
    process = cms.Process('kappaSkim')
    process.source = cms.Source('PoolSource',
        fileNames=cms.untracked.vstring(testfile))
    process.maxEvents = cms.untracked.PSet(
        input=cms.untracked.int32(maxevents))

    # Includes + Global Tag ---------------------------------------------------
    process.load('FWCore.MessageService.MessageLogger_cfi')
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
    process.GlobalTag.globaltag = globaltag + '::All'

    # Configure tuple generation ----------------------------------------------
    process.load('Kappa.Producers.KTuple_cff')
    process.kappatuple = cms.EDAnalyzer('KTuple',
        process.kappaTupleDefaultsBlock,
        outputFile=cms.string("kappa_" + datatype + ".root"),
    )
    process.kappatuple.active = cms.vstring(
        'LV', 'TrackSummary', 'VertexSummary', 'BeamSpot',
        'MET', 'BasicJets',
    )
    if data:
        process.kappatuple.active += ['DataInfo']
    else:
        process.kappatuple.active += ['GenInfo', 'GenParticles']

    process.pathKappa = cms.Path(process.kappatuple)

    # Process schedule --------------------------------------------------------
    process.schedule = cms.Schedule(process.pathKappa)
    return process


if __name__ == "__main__":
    process = getBaseConfig('@GLOBALTAG@', datatype='@TYPE@')  # for grid-control
