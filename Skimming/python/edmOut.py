import FWCore.ParameterSet.Config as cms

edmOut = cms.OutputModule(
	"PoolOutputModule",
	fileName = cms.untracked.string('edmDump.root'),
	## save only events passing the full path
SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
	## save each edm object that has been produced by process KAPPA
	outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')
	)
ep = cms.EndPath(edmOut)
