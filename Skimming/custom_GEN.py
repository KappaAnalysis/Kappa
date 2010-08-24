def customise(process):
	# Remove output modules
	process.schedule.remove(process.endjob_step)
	process.schedule.remove(process.out_step)

	# Logging options
	process.options.wantSummary = cms.untracked.bool(True)
	process.MessageLogger.cerr.FwkReport.reportEvery = 1000
#	process.genParticles.abortOnUnknownPDGCode = False

	# Seed random generator
	from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
	randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
	randSvc.populate()

	# Add kappa skim
	process.load("Kappa.Producers.KTuple_cff")
	process.kappatuple = cms.EDAnalyzer('KTuple',
		process.kappaTupleDefaultsBlock,
		outputFile = cms.string('skim.root'),
	)
	process.kappatuple.active = cms.vstring('GenMetadata', 'LV')
	process.kappatuple.Metadata.l1Source = cms.InputTag("")
	process.kappatuple.Metadata.hltSource = cms.InputTag("")
	process.kappatuple.Metadata.noiseHCAL = cms.InputTag("")
	process.kappatuple.Metadata.hlTrigger = cms.InputTag("")
	process.kappatuple.Metadata.muonTriggerObjects = cms.vstring()
	process.kappatuple.Metadata.noiseHCAL = cms.InputTag("")
	process.pathSkim = cms.Path(process.kappatuple)
	process.schedule += process.pathSkim

	return process
