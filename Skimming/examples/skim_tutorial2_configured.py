#-# Copyright (c) 2013 - All Rights Reserved
#-#   Joram Berger <joram.berger@cern.ch>

import FWCore.ParameterSet.Config as cms


def getBaseConfig(globaltag, testfile="", maxevents=0, datatype='data'):
    """Testing config for Z+Jet skims with Kappa

       This is used in a cmssw config file via:
       import skim_base
       process = skim_base.getBaseConfig('START53_V12', "testfile.root")
    """
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

    # Reduce amount of messages -----------------------------------------------
    process.MessageLogger.default = cms.untracked.PSet(
        ERROR=cms.untracked.PSet(limit=cms.untracked.int32(5)))
    process.MessageLogger.cerr.FwkReport.reportEvery = 40

    # Produce PF muon isolation -----------------------------------------------
    from CommonTools.ParticleFlow.Isolation.tools_cfi import isoDepositReplace
    process.pfmuIsoDepositPFCandidates = isoDepositReplace('muons', 'particleFlow')
    process.pfMuonIso = cms.Path(process.pfmuIsoDepositPFCandidates)

    # Require two good muons --------------------------------------------------
    process.goodMuons = cms.EDFilter('CandViewSelector',
        src=cms.InputTag('muons'),
        cut=cms.string("pt > 12.0 & abs(eta) < 8.0 & isGlobalMuon()"),
    )
    process.twoGoodMuons = cms.EDFilter('CandViewCountFilter',
        src=cms.InputTag('goodMuons'),
        minNumber=cms.uint32(2),
    )

    # Configure tuple generation ----------------------------------------------
    process.load('Kappa.Producers.KTuple_cff')
    process.kappatuple = cms.EDAnalyzer('KTuple',
        process.kappaTupleDefaultsBlock,
        outputFile=cms.string("skim_" + datatype + ".root"),
    )
    process.kappatuple.verbose = cms.int32(0)
    process.kappatuple.profile = cms.bool(True)
    process.kappatuple.active = cms.vstring(
        'LV', 'Muons', 'TrackSummary', 'VertexSummary', 'BeamSpot',
        'MET', 'BasicJets',
    )
    if data:
        additional_actives = ['DataInfo']
    else:
        additional_actives = ['GenInfo', 'GenParticles']
    for active in additional_actives:
        process.kappatuple.active.append(active)

    # custom whitelist, otherwise the HLT trigger bits are not sufficient!
    process.kappatuple.Info.hltWhitelist = cms.vstring(
        # matches 'HLT_Mu17_Mu8_v7' etc.
        "^HLT_(Double)?Mu([0-9]+)_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",
        # matches 'HLT_DoubleMu7_v8' etc.
        "^HLT_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",
    )
    process.kappatuple.Info.tauDiscrProcessName = cms.untracked.string("XXXXXXXXX")
    process.kappatuple.GenParticles.genParticles.selectedStatus = cms.int32(31)

    process.pathKappa = cms.Path(
        process.goodMuons * process.twoGoodMuons * process.kappatuple
    )

    # Process schedule --------------------------------------------------------
    process.schedule = cms.Schedule(process.pfMuonIso, process.pathKappa)
    return process


if __name__ == "__main__":
    # for grid-control:
    # process = getBaseConfig('@GLOBALTAG@', datatype='@TYPE@')
    process = getBaseConfig('FT53_V21A_AN6', 'data')
