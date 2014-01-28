## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *

## ------------------------------------------------------
#  NOTE: you can use a bunch of core tools of PAT to
#  taylor your PAT configuration; for a few examples
#  uncomment the lines below
## ------------------------------------------------------
from PhysicsTools.PatAlgos.tools.coreTools import *

#MVA ID stuff from PAT
process.load('EgammaAnalysis.ElectronTools.electronIdMVAProducer_cfi')
process.mvaID = cms.Sequence(  process.mvaTrigV0 +process.mvaTrigNoIPV0 + process.mvaNonTrigV0 ) #c# aus electronPOC twiki. Zugriff siehe HTauTau2ElecAnalysis53x.cc, z1778. Arbeitet auf pat electron level, nicht auf gsfElectron
process.patElectrons.electronIDSources = cms.PSet(
    #MVA
    mvaTrigV0 = cms.InputTag("mvaTrigV0"),
    mvaTrigNoIPV0 = cms.InputTag("mvaTrigNoIPV0"),
    mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0"),
)
#MVA ID stuff end

process.patseq = cms.Sequence(
	process.mvaID

)


## remove MC matching from the default sequence
removeMCMatching(process, ['Electrons'])
# runOnData(process)

## remove certain objects from the default sequence
removeAllPATObjectsBut(process, ['Electrons'])
# removeSpecificPATObjects(process, ['Electrons', 'Muons', 'Taus'])


## let it run
process.p = cms.Path(
    process.patseq*
    process.patDefaultSequence
    )

## ------------------------------------------------------
#  In addition you usually want to change the following
#  parameters:
## ------------------------------------------------------
#
#   process.GlobalTag.globaltag =  ...    ##  (according to https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideFrontierConditions)
#                                         ##
#from PhysicsTools.PatAlgos.patInputFiles_cff import filesRelValProdTTbarAODSIM
process.source.fileNames = cms.untracked.vstring('file:/storage/8/dhaitz/testfiles/mc11.root')
#                                         ##
process.maxEvents.input = 100
#                                         ##
#   process.out.outputCommands = [ ... ]  ##  (e.g. taken from PhysicsTools/PatAlgos/python/patEventContent_cff.py)
#                                         ##
process.out.fileName = 'patTuple_electrons.root'
#                                         ##
#   process.options.wantSummary = False   ##  (to suppress the long output at the end of the job)


# Kappa
process.load('Kappa.Producers.KTuple_cff')
process.kappatuple = cms.EDAnalyzer('KTuple',
        process.kappaTupleDefaultsBlock,
        outputFile = cms.string("skim.root"), )
process.kappatuple.verbose = cms.int32(0)
process.kappatuple.active = cms.vstring('Electrons')
process.kappatuple.Metadata.hltWhitelist = cms.vstring(
    # matches 'HLT_Mu17_Mu8_v7' etc.
    "^HLT_(Double)?Electron([0-9]+)_(Double)?Electron([0-9]+)(_v[[:digit:]]+)?$",
    # matches 'HLT_DoubleMu7_v8' etc.
    "^HLT_(Double)?Electron([0-9]+)(_v[[:digit:]]+)?$",
)
process.pathKappa = cms.Path( process.kappatuple )
