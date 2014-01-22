import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0])) + "/Kappa/")

## ------------------------------------------------------------------------
## import skeleton process KAPPA
from Kappa.Producers.KSkimming_template_cfg import *

## test file for EKP
#process.source.fileNames     = cms.untracked.vstring('file:/storage/8/dhaitz/testfiles/mc11.root')
## test file for lxplus
process.source.fileNames      = cms.untracked.vstring('root://eoscms//eos/cms/store/relval/CMSSW_5_3_6-START53_V14/RelValProdTTbar/AODSIM/v2/00000/76ED0FA6-1E2A-E211-B8F1-001A92971B72.root')

process.maxEvents.input       = 100                                                                  ## number of events to be processed (-1 = all in file)
process.kappaTuple.outputFile = 'kappaTuple_electrons.root'                                          ## name of output file
process.kappaTuple.active     = cms.vstring('Electrons',                                              ## produce KappaElectrons,
                                            'VertexSummary',                                         ## produce Metadata,
                                            'BeamSpot')                                              ## save Beamspot,
process.kappaTuple.verbose    = cms.int32(0)                                                         ## verbosity level
#process.kappaTuple.Metadata.hltWhitelist = cms.vstring(                                             ## HLT preselection
#    # matches 'HLT_Mu17_Mu8_v7' etc.
#    "^HLT_(Double)?Electron([0-9]+)_(Double)?Electron([0-9]+)(_v[[:digit:]]+)?$",
#    # matches 'HLT_DoubleMu7_v8' etc.
#    "^HLT_(Double)?Electron([0-9]+)(_v[[:digit:]]+)?$",
#)

## ------------------------------------------------------------------------
## declare edm OutputModule (expects a path 'p'), uncommented if wanted

from RecoEgamma.EgammaPhotonProducers.allConversionSequence_cff import *

process.edmOut = cms.OutputModule("PoolOutputModule",
                               fileName = cms.untracked.string('patTuple_electrons.root'),           ## name of output file 
                               SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ), ## save only events passing the full path
                               outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')  ## save each edm object that has been produced by process KAPPA 
                               )
process.kappaOut+=process.edmOut

## ------------------------------------------------------------------------
## KappaElectrons 
process.load("Kappa.Producers.KElectrons_cff")

## And let it run
process.p = cms.Path(
    process.makeKappaElectrons
    )
