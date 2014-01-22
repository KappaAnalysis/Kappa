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

process.maxEvents.input       = 100                                       ## number of events to be processed (-1 = all in file)
process.kappaTuple.outputFile = 'kappaTuple_jets.root'                    ## name of output file
process.kappaTuple.active     = cms.vstring('JetArea',
					    'PFJets',
					   )                              ## produce KappaPFJets
process.kappaTuple.verbose    = cms.int32(0)                              ## verbosity level
#process.kappaTuple.Metadata.hltWhitelist = cms.vstring(                  ## HLT preselection
#    # matches 'HLT_Mu17_Mu8_v7' etc.
#    "^HLT_(Double)?Electron([0-9]+)_(Double)?Electron([0-9]+)(_v[[:digit:]]+)?$",
#    # matches 'HLT_DoubleMu7_v8' etc.
#    "^HLT_(Double)?Electron([0-9]+)(_v[[:digit:]]+)?$",
#)

## ------------------------------------------------------------------------
## declare edm OutputModule (expects a path 'p'), uncommented if wanted
process.edmOut = cms.OutputModule("PoolOutputModule",
                               fileName = cms.untracked.string('patTuple_jets.root'),          ## name of output file 
                               SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ), ## save only events passing the full path
                               outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')  ## save each edm object that has been produced by process KAPPA 
                               )
process.kappaOut+=process.edmOut

## ------------------------------------------------------------------------
## KappaJets
process.load("Kappa.Producers.KJets_cff")

## And let it run
process.p = cms.Path(
    process.makePfCHS *
    process.makePFJets *
    process.makePFJetsCHS
    )

## !!! temporary: this will later go in the highest-level cfg !!!
datatype = 'mc'

if datatype == 'mc':
	process.p.insert(0, process.makeNoNuGenJets)
