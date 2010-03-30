import FWCore.ParameterSet.Config as cms

'''
An example ntuple skimming with KAPPA
'''

# Metaconfig -------------------------------------------------------------------
ifiles=['file:///home/piparo/testFiles/Spring10_MinBias_GENSIMRECO_MC_3XY_V25_S09_preproduction-v2.root']
max_evts=1000
skip_evts=0
root_filename = 'Ktuple_test.root'
#active_KTuple_categories=['Metadata','Muons','Tracks','LV','Tower','MET']
active_KTuple_categories=['CaloJets']
#-------------------------------------------------------------------------------

process = cms.Process("KAPPAExample")

p = process # shortcut!

p.load('FWCore/MessageService/MessageLogger_cfi')

p.source = cms.Source("PoolSource",
                      skipEvents = cms.untracked.uint32(skip_evts),
                      fileNames = cms.untracked.vstring(ifiles),
                      duplicateCheckMode = cms.untracked.string("noDuplicateCheck")
                     )

# The max events number to process ---------------------------------------------
p.maxEvents=cms.untracked.PSet(input = cms.untracked.int32(max_evts))
#-------------------------------------------------------------------------------

## TFile Service ----------------------------------------------------------------
#p.TFileService = cms.Service("TFileService", 
                             #fileName = cms.string(root_filename))

##-------------------------------------------------------------------------------

# The KAPPA ntupliser ----------------------------------------------------------
p.load('Kappa/Producers/KTuple_cff')
p.kappaTupleDefaultsBlock.outputFile = cms.string(root_filename)
p.kappaTupleDefaultsBlock.active = active_KTuple_categories
p.ktuple = cms.EDAnalyzer('KTuple',
                          p.kappaTupleDefaultsBlock)

p.ktuplePath = cms.Path(p.ktuple)

#-------------------------------------------------------------------------------

# Schedule building ------------------------------------------------------------
p.schedule=cms.Schedule(p.ktuplePath)
#-------------------------------------------------------------------------------

# Configuration End |-----------------------------------------------------------
