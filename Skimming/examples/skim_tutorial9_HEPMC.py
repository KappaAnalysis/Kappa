import FWCore.ParameterSet.Config as cms

# This configuration loads a hepmc file and converts it to kappa skimmed file
# !!! This file does not run properly !!!

process = cms.Process('HepMCtoKappaSkim')

### ###
### Import HepMC file into CMSSW
### ###
# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic8TeVCollision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# process all events found in the hepMC
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source is hepMC file
process.source = cms.Source("MCFileSource",
	fileNames = cms.untracked.vstring(
		'file:///storage/6/stober/Sherpa/test/output_3500_0.7_300-600_Ahadic_Amisic_92',
	)
)

process.options = cms.untracked.PSet(
)

# Other statements
#process.genstepfilter.triggerConditions=cms.vstring("generation_step")
process.GlobalTag.globaltag = 'START53_V7A::All'

# get generator data from existing hepMC directly
process.generator = cms.EDProducer("HepMCCopy")

# Path and EndPath definitions
process.readsource_step = cms.Path(process.generator)
process.generation_step = cms.Path(process.pgen)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
#process.RECOSIMoutput_step = cms.EndPath(process.RECOSIMoutput)

### ###
### Skim data with Kappa
### ###

# Basic process setup ----------------------------------------------------------
#-------------------------------------------------------------------------------

# Configure tuple generation ---------------------------------------------------
process.load("Kappa.Producers.KTuple_cff")
process.kappatuple = cms.EDAnalyzer('KTuple',
	process.kappaTupleDefaultsBlock,
	outputFile = cms.string('skim.root'),
)
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring('Metadata', 'LV')
process.kappatuple.Info.l1Source = cms.InputTag("")
process.kappatuple.Info.hltSource = cms.InputTag("")
process.kappatuple.Info.noiseHCAL = cms.InputTag("")
process.kappatuple.Info.hlTrigger = cms.InputTag("")
process.kappatuple.Info.muonTriggerObjects = cms.vstring()
# workaround for error in HepMC loader
process.kappatuple.Info.overrideHLTCheck = cms.untracked.bool(True)

# Process schedule -------------------------------------------------------------
process.pathDAT = cms.Path(process.kappatuple)
process.schedule = cms.Schedule(process.pathDAT)
#-------------------------------------------------------------------------------

process.schedule = cms.Schedule(process.readsource_step,process.generation_step,process.pathDAT,process.endjob_step)
#process.schedule = cms.Schedule(process.readsource_step,process.generation_step,process.genfiltersummary_step,process.endjob_step,process.RECOSIMoutput_step)
