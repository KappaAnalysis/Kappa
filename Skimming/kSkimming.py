import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0])) + "/Kappa/")

from Kappa.Producers.KSkimming_template_cfg import *
## test file for EKP
#process.source.fileNames     = cms.untracked.vstring('file:/storage/8/dhaitz/testfiles/mc11.root')
## test file for lxplus
process.source.fileNames      = cms.untracked.vstring('root://eoscms//eos/cms/store/relval/CMSSW_5_3_6-START53_V14/RelValProdTTbar/AODSIM/v2/00000/76ED0FA6-1E2A-E211-B8F1-001A92971B72.root')
## test file for RWTH
#process.source.fileNames     = cms.untracked.vstring('file:/user/kargoll/testfiles/DYTauTau/DYTauTau_Summer12.root')


process.maxEvents.input			= 100											## number of events to be processed (-1 = all in file)
process.kappaTuple.outputFile	= 'kappaTuple.root'						## name of output file
process.kappaTuple.verbose		= cms.int32(0)								## verbosity level
datatype = 'mc'
data = (datatype == 'data')


## ------------------------------------------------------------------------
# General configuration

process.kappaTuple.active		= cms.vstring('VertexSummary')		## produce Metadata,
process.kappaTuple.active		+= cms.vstring('BeamSpot')				## save Beamspot,

if data:
	process.kappaTuple.active		+= cms.vstring('DataMetadata')		## produce Metadata,
else:
	process.kappaTuple.active		+= cms.vstring('GenMetadata')			## produce Metadata,
	process.kappaTuple.active		+= cms.vstring('GenParticles')		## produce Metadata,


## ------------------------------------------------------------------------
# Configure Electrons

process.kappaTuple.active		+= cms.vstring('Electrons')			## produce KappaElectrons,


from RecoEgamma.EgammaPhotonProducers.allConversionSequence_cff import *
process.load("Kappa.Producers.KElectrons_cff")

# configure PFCandidates and what to write out
process.kappaTuple.active		+= cms.vstring('PFCandidates')		## save PFCandidates for deltaBeta corrected isolation
process.kappaTuple.PFCandidates.whitelist = cms.vstring("pfNoPileUpChargedHadrons",
																			"pfNoPileUpNeutralHadrons",
																			"pfNoPileUpPhotons",
																			"pfPileUpChargedHadrons",
																			)

## ------------------------------------------------------------------------
# Configure Muons
process.kappaTuple.active			+= cms.vstring('Muons')				## save muons
process.load("Kappa.Producers.KMuons_cff")


## ------------------------------------------------------------------------
# Configure Taus
process.kappaTuple.active     += cms.vstring('PFTaus')					## produce KappaTaus
process.load("Kappa.Producers.KTaus_cff")


## ------------------------------------------------------------------------
# Configure Jets
process.kappaTuple.active += cms.vstring('JetArea')					## produce KappaPFJets
process.kappaTuple.active += cms.vstring('PFJets')
process.load("Kappa.Producers.KJets_cff")

## And let it run
process.p = cms.Path( 
	process.makeKappaElectrons *
	process.pfmuIsoDepositPFCandidates *
	process.makeKappaTaus *
	process.makePfCHS *
	process.makePFJetsCHS
	)

## ------------------------------------------------------------------------
## declare edm OutputModule (expects a path 'p'), uncommented if wanted

process.edmOut = cms.OutputModule("PoolOutputModule",
										fileName = cms.untracked.string('dump.root'),					## name of output file 
										SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),	## save only events passing the full path
										outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')		## save each edm object that has been produced by process KAPPA 
										)
process.kappaOut+=process.edmOut
