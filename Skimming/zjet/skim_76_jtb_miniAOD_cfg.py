# Kappa test: CMSSW 7.6.3
# Kappa test: scram arch slc6_amd64_gcc493
# Kappa test: output skim76.root

import os
import FWCore.ParameterSet.Config as cms

## for local runs you can modify the next section
## also check if the global tag is up to date 
########### local setupu ##########
#input_files='file:/nfs/dust/cms/user/swayand/DO_MU_FILES/AOD/Madgraph.root'
#input_files='file:/nfs/dust/cms/user/swayand/DO_MU_FILES/AOD/DATARun2015D.root'
#input_files='file:///storage/b/fs6-mirror/fcolombo/kappatest/input/data_AOD_Run2015D.root' #do not remove: for Kappa test!
#input_files='file:///nfs/dust/cms/user/swayand/DO_MU_FILES/CMSSW80X/DYTOLLM50_mcantlo.root'
input_files='file:///storage/a/afriedel/zjets/mc_miniAOD.root' #do not remove: for Kappa test!
#input_files='file:///storage/a/afriedel/zjets/mc_miniAOD.root' #do not remove: for Kappa test!
#input_files='dcap://cmssrm-kit.gridka.de:22125/pnfs/gridka.de/cms/store/mc/RunIISpring16DR80/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/20000/1A054918-89FF-E511-B246-0CC47A4D76B2.root'

maxevents=100
outputfilename="skim76_jtb.root"
kappa_verbosity=0

#  Basic Process Setup  ############################################
process = cms.Process("KAPPA")
process.path = cms.Path()
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(maxevents))
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))
process.source = cms.Source("PoolSource",
			    fileNames=cms.untracked.vstring(input_files)
			    )
process.options.emptyRunLumiMode = cms.untracked.string('doNotHandleEmptyRunsAndLumis')

#data = @IS_DATA@
#globaltag= '@GLOBALTAG@'

data = False
#globaltag='76X_dataRun2_v15'
globaltag='76X_mcRun2_asymptotic_v12'

#  Config parameters  ##############################################
	## print information

print "\n------- CONFIGURATION 1 ---------"
print "input:          ", process.source.fileNames[0], "... (%d files)" % len(process.source.fileNames) if len(process.source.fileNames) > 1 else ""
print "file type:      ", "miniAOD"
print "data:           ", data
print "output:         ", outputfilename
print "global tag:     ", globaltag
print "max events:     ", (str(process.maxEvents.input)[20:-1])
print "cmssw version:  ", os.environ["CMSSW_VERSION"]
print "---------------------------------"
print

# message logger
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 50
process.MessageLogger.default = cms.untracked.PSet(
	ERROR=cms.untracked.PSet(limit=cms.untracked.int32(5))
	)

	## Geometry and Detector Conditions (needed for a few patTuple production steps)
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.GlobalTag.globaltag = cms.string(globaltag)

	#  Kappa  ##########################################################
process.load('Kappa.Producers.KTuple_cff')
process.kappaTuple = cms.EDAnalyzer('KTuple',
				    process.kappaTupleDefaultsBlock,
				    outputFile = cms.string(outputfilename),
				    )
###process.kappaTuple.Info.printHltList =  cms.bool(True)
process.kappaTuple.verbose = kappa_verbosity
process.kappaOut = cms.Sequence(process.kappaTuple)
process.kappaTuple.active = cms.vstring('VertexSummary', 'BeamSpot')
process.kappaTuple.Info.pileUpInfoSource = cms.InputTag("slimmedAddPileupInfo")
if data:
	process.kappaTuple.active += cms.vstring('DataInfo')
else:
	process.kappaTuple.active += cms.vstring('GenInfo', 'GenParticles')
	process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")

	
#process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)
#process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")


process.kappaTuple.active += cms.vstring('TriggerObjectStandalone')	
process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "RECO")
process.kappaTuple.Info.hltWhitelist = cms.vstring(
	# HLT regex selection can be tested at https://regex101.com (with gm options)
	# single muon triggers, e.g. HLT_Mu50_v1
	"^HLT_(Iso)?(Tk)?Mu[0-9]+(_eta2p1|_TrkIsoVVL)?_v[0-9]+$",
	# double muon triggers, e.g. HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v1
	"^HLT_Mu[0-9]+(_TrkIsoVVL)?_(Tk)?Mu[0-9]+(_TrkIsoVVL)?(_DZ)?_v[0-9]+$",
	# double electrons trigger 
	"^HLT_Ele[0-9]+_Ele[0-9]+(_CaloIdL)?(_TrackIdL)?(_IsoVL)?(_DZ)?_v[0-9]+$",
	)

# Primary Input Collections ###################################################

input_PFCandidates = 'packedPFCandidates'
input_PrimaryVertices = 'offlineSlimmedPrimaryVertices'


## in data few events don't have a valid pf collection. They get veto by the following lines
if data:
	process.pfFilter = cms.EDFilter('CandViewCountFilter',
					src = cms.InputTag(input_PFCandidates),
					minNumber = cms.uint32(1),
					filter = cms.bool(False) ## Add Filter option
					)
	process.path *= (process.pfFilter)



#  PFCandidates  ###################################################
	## Good offline PV selection:
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
						  filterParams = pvSelector.clone(maxZ = 24.0),  # ndof >= 4, rho <= 2
						  src=cms.InputTag(input_PrimaryVertices),
						  )

	## ------------------------------------------------------------------------
	## TopProjections from CommonTools/ParticleFlow:

process.load("Kappa.Skimming.KPFCandidates_miniAOD_cff")

process.pfNoPileUpIso = cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("packedPFCandidates"),
	cut = cms.string("fromPV > 1")
)
process.pfPileUpIso = cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("packedPFCandidates"),
	cut = cms.string("fromPV <= 1")
)
process.pfAllNeutralHadronsAndPhotons = cms.EDFilter("CandPtrSelector",
	src = cms.InputTag("pfNoPileUp"),
	cut = cms.string("abs(pdgId) = 111 | abs(pdgId) = 130 | " \
			 "abs(pdgId) = 310 | abs(pdgId) = 2112 | " \
			 "abs(pdgId) = 22")
)

process.path *= (
	process.goodOfflinePrimaryVertices
	*process.pfNoPileUpIso
	*process.pfPileUpIso
	*process.makeKappaPFCandidates
	*process.pfAllNeutralHadronsAndPhotons
	)
# Configure Muons
process.load("Kappa.Skimming.KMuons_miniAOD_cff")
process.kappaTuple.Muons.minPt = 8.0
process.kappaTuple.Muons.muons.src = cms.InputTag("slimmedMuons")
process.kappaTuple.Muons.muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
process.kappaTuple.Muons.muons.srcMuonIsolationPF = cms.InputTag("")
process.kappaTuple.Muons.doPfIsolation = cms.bool(False)
for src in [ "muPFIsoDepositCharged", "muPFIsoDepositChargedAll", "muPFIsoDepositNeutral", "muPFIsoDepositGamma", "muPFIsoDepositPU"]:
	setattr(getattr(process, src), "src", cms.InputTag("slimmedMuons"))
process.kappaTuple.active += cms.vstring('Muons')
process.kappaTuple.Muons.noPropagation = cms.bool(True)
process.path *= ( process.makeKappaMuons )

## ------------------------------------------------------------------------
# Configure Electrons
process.kappaTuple.active += cms.vstring('Electrons')
process.kappaTuple.Electrons.minPt = 8.0
process.load("Kappa.Skimming.KElectrons_miniAOD_cff")
process.kappaTuple.Electrons.electrons.src = cms.InputTag("slimmedElectrons")
process.kappaTuple.Electrons.electrons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
process.kappaTuple.Electrons.electrons.rhoIsoInputTag = cms.InputTag("slimmedJets", "rho")
from Kappa.Skimming.KElectrons_miniAOD_cff import setupElectrons
process.kappaTuple.Electrons.srcIds = cms.string("standalone");

process.kappaTuple.Electrons.ids = cms.vstring("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-veto",
				"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-loose",
				"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-medium",
				"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-tight",
				"electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values")


setupElectrons(process, "slimmedElectrons")
process.path *= ( process.makeKappaElectrons )

#  Jets  ###########################################################
# Kappa jet processing
process.kappaTuple.Jets.minPt = 5.0
process.kappaTuple.Jets.taggers = cms.vstring()

# containers for objects to process
kappa_jets = {}  # algoname: kappa jet config

# GenJets
if not data:
	process.kappaTuple.active += cms.vstring('LV')

#Run JetToolbox to get jet collections: https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetToolbox
from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox

jetSequence = 'sequence'
jetToolbox( process, 'ak4', jetSequence+'ak4CHS',  'out', miniAOD=True, runOnMC= not data, JETCorrPayload = "None", PUMethod='CHS',  addPruning=False, addSoftDrop=False , addPrunedSubjets=False,  addNsub=False, maxTau=6, addTrimming=False, addFiltering=False, addNsubSubjets=False, addPUJetID=True) 
process.path *= process.sequenceak4CHS
process.path *= process.AK4PFCHSpileupJetIdCalculator*process.AK4PFCHSpileupJetIdEvaluator
jetToolbox( process, 'ak4', jetSequence+'ak4Puppi',  'out', miniAOD=True, runOnMC= not data, JETCorrPayload = "None", PUMethod='Puppi',  addPruning=False, addSoftDrop=False , addPrunedSubjets=False,  addNsub=False, maxTau=6, addTrimming=False, addFiltering=False, addNsubSubjets=False) 
process.path *= process.sequenceak4Puppi
jetToolbox( process, 'ak4', jetSequence+'ak4',  'out', miniAOD=True, runOnMC= not data, JETCorrPayload = "None", PUMethod='None',  addPruning=False, addSoftDrop=False , addPrunedSubjets=False,  addNsub=False, maxTau=6, addTrimming=False, addFiltering=False, addNsubSubjets=False) 
process.path *= process.sequenceak4
jetToolbox( process, 'ak8', jetSequence+'ak8CHS',  'out', miniAOD=True, runOnMC= not data, JETCorrPayload = "None", PUMethod='CHS',  addPruning=False, addSoftDrop=False , addPrunedSubjets=False,  addNsub=False, maxTau=6, addTrimming=False, addFiltering=False, addNsubSubjets=False) 
process.path *= process.sequenceak8CHS
jetToolbox( process, 'ak8', jetSequence+'ak8Puppi',  'out', miniAOD=True, runOnMC= not data, JETCorrPayload = "None", PUMethod='Puppi',  addPruning=False, addSoftDrop=False , addPrunedSubjets=False,  addNsub=False, maxTau=6, addTrimming=False, addFiltering=False, addNsubSubjets=False) 
process.path *= process.sequenceak8Puppi
jetToolbox( process, 'ak8', jetSequence+'ak8',  'out', miniAOD=True, runOnMC= not data, JETCorrPayload = "None", PUMethod='None',  addPruning=False, addSoftDrop=False , addPrunedSubjets=False,  addNsub=False, maxTau=6, addTrimming=False, addFiltering=False, addNsubSubjets=False) 
process.path *= process.sequenceak8
from Kappa.Skimming.KPatJets_miniAOD_cff import setup_PatJets
patJets = setup_PatJets(process, data)
	# create Jet variants
for param in (4, 8):
	for algo in ["", "CHS", "Puppi"]:
		variant_name = "ak%dPFJets%s" % (param, algo)
		variant_patJet_name = "AK%dPF%s" % (param, algo)
		process.path *= patJets[variant_patJet_name]
		# Full Kappa jet definition
		kappa_jets[variant_name] = cms.PSet(
			src = cms.InputTag('selectedPatJets'+variant_patJet_name)
			)
		# GenJets
	if not data:
			variant_name = "ak%sGenJetsNoNu" % (param)
				# GenJets are just KLVs
			process.kappaTuple.LV.whitelist += cms.vstring(variant_name)
for name, pset in kappa_jets.iteritems():
	setattr(process.kappaTuple.PatJets, name, pset)
#setattr(process.kappaTuple.PatJets, 'bTag', cms.PSet(
#			src = cms.InputTag('pfCombinedSecondaryVertexV2BJetTagsAK4PFCHS')))

process.kappaTuple.active += cms.vstring('PatJets', 'PileupDensity')
process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")


	#  Kappa  Output ###########################################################
process.path *= (process.kappaOut)

process.kappaTuple.BeamSpot.offlineBeamSpot = cms.PSet(src=cms.InputTag("offlineBeamSpot"))
process.kappaTuple.VertexSummary.offlinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("offlineSlimmedPrimaryVertices"))
process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("goodOfflinePrimaryVertices"))

if not data:
	process.kappaTuple.LV.ak4GenJetsNoNu = cms.PSet(src=cms.InputTag("ak4GenJetsNoNu"))
	process.kappaTuple.LV.ak8GenJetsNoNu = cms.PSet(src=cms.InputTag("ak8GenJetsNoNu"))

process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAll"))

process.kappaTuple.active += cms.vstring('PatMET')
process.kappaTuple.PatMET.metCHS = cms.PSet(src=cms.InputTag("slimmedMETs"), uncorrected = cms.bool(True))
process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"), uncorrected = cms.bool(True))
process.kappaTuple.PatMET.uncorrected = cms.bool(True) #Uncorrect MET -> Correcting step in excalibur for calibration purpose
process.load("Kappa.CMSSW.EventWeightCountProducer_cff")
if not data:
		process.nEventsTotal.isMC = cms.bool(True)
		process.nNegEventsTotal.isMC = cms.bool(True)
		process.nEventsFiltered.isMC = cms.bool(True)
		process.nNegEventsFiltered.isMC = cms.bool(True)

process.path.insert(0,process.nEventsTotal+process.nNegEventsTotal)
process.path.insert(-1,process.nEventsFiltered+process.nNegEventsFiltered)
process.kappaTuple.active += cms.vstring('FilterSummary')

	# final information:
print "------- CONFIGURATION 2 ---------"
print "CMSSW producers:"
for p in str(process.path).split('+'):
	print "  %s" % p
print "Kappa producers:"
for p in sorted(process.kappaTuple.active):
	print "  %s" % p
print "---------------------------------"



