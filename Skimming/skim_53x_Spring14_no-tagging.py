import FWCore.ParameterSet.Config as cms


def getBaseConfig(globaltag, testfile="", maxevents=0, datatype='data'):
    """Default config for Z+jet skims with Kappa

       This is used in a cmssw config file via:
       import skim_base
       process = skim_base.getBaseConfig('START53_V12', "testfile.root")
    """
    # Set the globalt tag and datatype for testing or by grid-control ---------
    data = (datatype == 'data')
    if data:
        testfile = 'file:/storage/8/dhaitz/testfiles/data_AOD_2012A.root'
        if '@' in globaltag: globaltag = 'FT53_V21A_AN6'
        maxevents = maxevents or 100
    else:
        testfile = 'file:/storage/8/dhaitz/testfiles/rundepMC.root'
        if '@' in globaltag: globaltag = 'START53_V19F'
        maxevents = maxevents or 100
        datatype = 'mc'
    print "GT:", globaltag, "| TYPE:", datatype, "| maxevents:", maxevents, "| file:", testfile

    # Basic process setup -----------------------------------------------------
    process = cms.Process('kappaSkim')
    process.source = cms.Source('PoolSource',
        fileNames = cms.untracked.vstring(testfile))
    process.maxEvents = cms.untracked.PSet(
        input = cms.untracked.int32(maxevents))

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
        ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5)))
    process.MessageLogger.cerr.FwkReport.reportEvery = 40

    # Produce PF muon isolation -----------------------------------------------
    from CommonTools.ParticleFlow.Isolation.tools_cfi import isoDepositReplace
    process.pfmuIsoDepositPFCandidates = isoDepositReplace('muons', 'particleFlow')
    process.pfMuonIso = cms.Path(process.pfmuIsoDepositPFCandidates)

    # Create good primary vertices to be used for PF association --------------
    from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
    process.goodOfflinePrimaryVertices = cms.EDFilter("PrimaryVertexObjectFilter",
        filterParams = pvSelector.clone(minNdof = cms.double(4.0), maxZ = cms.double(24.0)),
        src=cms.InputTag('offlinePrimaryVertices')
    )
    process.ak5PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
    process.ak7PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
    process.kt4PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')
    process.kt6PFJets.srcPVs = cms.InputTag('goodOfflinePrimaryVertices')


    # CHS Jets with the NoPU sequence -----------------------------------------
    process.load('CommonTools.ParticleFlow.PFBRECO_cff')
    process.pfPileUp.Vertices = cms.InputTag('goodOfflinePrimaryVertices')
    process.pfPileUp.checkClosestZVertex = cms.bool(False)
    process.pfCHS = cms.Path(process.goodOfflinePrimaryVertices * process.PFBRECO)
    process.ak5PFJetsCHS = process.ak5PFJets.clone(src = cms.InputTag('pfNoPileUp'))
    process.ak7PFJetsCHS = process.ak7PFJets.clone(src = cms.InputTag('pfNoPileUp'))
    process.kt4PFJetsCHS = process.kt4PFJets.clone(src = cms.InputTag('pfNoPileUp'))
    process.kt6PFJetsCHS = process.kt6PFJets.clone(src = cms.InputTag('pfNoPileUp'))

    # Gen Jets without neutrinos ----------------------------------------------
    if datatype == 'mc':
        process.load('RecoJets.JetProducers.ak5GenJets_cfi')
        process.NoNuGenJets = cms.Path(process.genParticlesForJetsNoNu *
            process.genParticlesForJets *
            process.ak5GenJetsNoNu * process.ak7GenJetsNoNu *
            process.kt4GenJetsNoNu * process.kt4GenJets *
            process.kt6GenJetsNoNu * process.kt6GenJets
        )

    # Path to Redo all Jets ---------------------------------------------------
    process.jetsRedo = cms.Path(
        process.ak5PFJets * process.ak7PFJets * process.kt4PFJets * process.kt6PFJets *
        process.ak5PFJetsCHS * process.ak7PFJetsCHS * process.kt4PFJetsCHS * process.kt6PFJetsCHS
    )

    # MET filters -------------------------------------------------------------
    process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi')
    # Create good vertices for the trackingFailure MET filter
    process.goodVertices = cms.EDFilter("VertexSelector",
        filter = cms.bool(False),
        src = cms.InputTag("offlinePrimaryVertices"),
        cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2"),
    )
    # The good primary vertex filter for other MET filters
    process.primaryVertexFilter = cms.EDFilter("VertexSelector",
        filter = cms.bool(True),
        src = cms.InputTag("offlinePrimaryVertices"),
        cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.Rho <= 2"),
    )
    process.noscraping = cms.EDFilter("FilterOutScraping",
        applyfilter = cms.untracked.bool(True),
        debugOn = cms.untracked.bool(False),
        numtrack = cms.untracked.uint32(10),
        thresh = cms.untracked.double(0.25)
    )
    process.load('CommonTools.RecoAlgos.HBHENoiseFilter_cfi')
    process.load('RecoMET.METAnalyzers.CSCHaloFilter_cfi')
    process.load('RecoMET.METFilters.hcalLaserEventFilter_cfi')
    process.hcalLaserEventFilter.vetoByRunEventNumber = cms.untracked.bool(False)
    process.hcalLaserEventFilter.vetoByHBHEOccupancy = cms.untracked.bool(True)
    process.load('RecoMET.METFilters.EcalDeadCellTriggerPrimitiveFilter_cfi')
    process.EcalDeadCellTriggerPrimitiveFilter.tpDigiCollection = cms.InputTag("ecalTPSkimNA")
    process.load('RecoMET.METFilters.EcalDeadCellBoundaryEnergyFilter_cfi')
    process.load('RecoMET.METFilters.eeBadScFilter_cfi')
    process.load('RecoMET.METFilters.eeNoiseFilter_cfi')
    process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi')
    process.load('RecoMET.METFilters.trackingFailureFilter_cfi')
    process.load('RecoMET.METFilters.inconsistentMuonPFCandidateFilter_cfi')
    process.load('RecoMET.METFilters.greedyMuonPFCandidateFilter_cfi')

    process.hcalLaserEventFilter.taggingMode = cms.bool(True)
    process.EcalDeadCellTriggerPrimitiveFilter.taggingMode = cms.bool(True)
    process.EcalDeadCellBoundaryEnergyFilter.taggingMode = cms.bool(True)
    process.trackingFailureFilter.taggingMode = cms.bool(True)
    process.eeBadScFilter.taggingMode = cms.bool(True)
    process.eeNoiseFilter.taggingMode = cms.bool(True)
    process.ecalLaserCorrFilter.taggingMode = cms.bool(True)
    process.trackingFailureFilter.taggingMode = cms.bool(True)
    process.inconsistentMuonPFCandidateFilter.taggingMode = cms.bool(True)
    process.greedyMuonPFCandidateFilter.taggingMode = cms.bool(True)
    process.beamScrapingFilter = process.inconsistentMuonPFCandidateFilter.clone(
        ptMin = cms.double(5000.0)
    )
    process.hcalNoiseFilter = process.beamScrapingFilter.clone()
    process.beamHaloFilter = process.beamScrapingFilter.clone()
    process.filtersSeq = cms.Sequence(
        process.primaryVertexFilter *
        process.hcalLaserEventFilter +
        process.EcalDeadCellTriggerPrimitiveFilter +
        process.EcalDeadCellBoundaryEnergyFilter +
        process.eeBadScFilter +
        process.eeNoiseFilter +
        process.ecalLaserCorrFilter +
        process.goodVertices * process.trackingFailureFilter +
        process.inconsistentMuonPFCandidateFilter +
        process.greedyMuonPFCandidateFilter +
        process.noscraping * process.beamScrapingFilter +
        process.HBHENoiseFilter * process.hcalNoiseFilter +
        process.CSCTightHaloFilter * process.beamHaloFilter
    )
    process.metFilters = cms.Path(process.filtersSeq)

    # MET correction ----------------------------------------------------------
    process.load("JetMETCorrections.Type1MET.pfMETCorrections_cff")
    process.pfchsMETcorr.src = cms.InputTag('goodOfflinePrimaryVertices')
    # Type-0
    process.pfMETCHS = process.pfType1CorrectedMet.clone(
        applyType1Corrections = cms.bool(False),
        applyType0Corrections = cms.bool(True)
    )
    # MET Path
    process.metCorrections = cms.Path(
            process.producePFMETCorrections * process.pfMETCHS
    )

    # Require two good muons --------------------------------------------------
    process.goodMuons = cms.EDFilter('CandViewSelector',
        src = cms.InputTag('muons'),
        cut = cms.string("pt > 12.0 & abs(eta) < 8.0 & isGlobalMuon()"),
    )
    process.twoGoodMuons = cms.EDFilter('CandViewCountFilter',
        src = cms.InputTag('goodMuons'),
        minNumber = cms.uint32(2),
    )

    # Configure tuple generation ----------------------------------------------
    process.load('Kappa.Producers.KTuple_cff')
    process.kappatuple = cms.EDAnalyzer('KTuple',
        process.kappaTupleDefaultsBlock,
        outputFile = cms.string("skim_" + datatype + "_no-tagging.root"),
    )

    process.kappatuple.verbose = cms.int32(0)
    process.kappatuple.active = cms.vstring(
        'LV', 'Muons', 'TrackSummary', 'VertexSummary', 'BeamSpot',
        'JetArea', 'PFMET', 'PFJets',
        'FilterSummary',
    )
    if data:
        additional_actives = ['DataMetadata']
    else:
        additional_actives = ['GenMetadata', 'GenParticles']
    for active in additional_actives:
        process.kappatuple.active.append(active)

    # custom whitelist, otherwise the HLT trigger bits are not sufficient!
    process.kappatuple.Metadata.hltWhitelist = cms.vstring(
        # matches 'HLT_Mu17_Mu8_v7' etc.
        "^HLT_(Double)?Mu([0-9]+)_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",
        # matches 'HLT_DoubleMu7_v8' etc.
        "^HLT_(Double)?Mu([0-9]+)(_v[[:digit:]]+)?$",
    )
    process.kappatuple.Metadata.tauDiscrProcessName = cms.untracked.string("XXXXXXXXX")
    process.kappatuple.GenParticles.genParticles.selectedStatus = cms.int32(31)

    # use the good objects not temporary ones
    process.kappatuple.VertexSummary.whitelist = cms.vstring(".*fflinePrimaryVertices")
    process.kappatuple.VertexSummary.blacklist += cms.vstring(".*QG.*")
    process.kappatuple.LV.whitelist += cms.vstring("recoCaloJets.*")
    process.kappatuple.LV.blacklist += cms.vstring("AK5TrackJets", ".*KT.*")
    process.kappatuple.PFJets.whitelist = cms.vstring("recoPFJets.*kappaSkim")
    process.kappatuple.PFMET.blacklist = cms.vstring("pfType1.*CorrectedMet")
    process.kappatuple.PFJets.blacklist = cms.vstring(".*Tau.*", "recoPFJets_pfJets.*kappaSkim", ".*QG.*", ".*KT.*")
    del process.kappatuple.GenParticles.genStableMuons

    process.pathKappa = cms.Path(
        process.goodMuons * process.twoGoodMuons * process.kappatuple
    )

    # Process schedule --------------------------------------------------------
    process.schedule = cms.Schedule(
        process.metFilters,
        process.pfCHS,
        process.jetsRedo,
        process.pfMuonIso,
        process.metCorrections,
        process.pathKappa,
    )
    if not data:
        process.schedule.insert(0, process.NoNuGenJets)

    return process


def addOutputModule(process, filename="test_out.root"):
    """Additional output file for testing.

       Do not use for a full skim, only for a few 100 events.
       Usage in cmssw config: process = base.addOutputModule(process)
    """
    process.Out = cms.OutputModule("PoolOutputModule",
         fileName = cms.untracked.string(filename)
    )
    process.end = cms.EndPath(process.Out)
    process.schedule.append(process.end)
    return process

if __name__ == "__main__":
    process = getBaseConfig('@GLOBALTAG@', datatype='@TYPE@')
