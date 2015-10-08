import FWCore.ParameterSet.Config as cms

edmOut = cms.OutputModule(
	"PoolOutputModule",
	fileName = cms.untracked.string('edmDump.root'),
	## save only events passing the full path
SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
	## save each edm object that has been produced by process KAPPA
	#outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')
    outputCommands = cms.untracked.vstring( #"keep *_slimmedMETs_*_*",
                                            "keep *_slimmedMETsNoHF_*_*",
                                            #"keep *_patPFMetT1Txy_*_*",
                                            #"keep patMETs*_*_*_*")
		)
	)
ep = cms.EndPath(edmOut)
