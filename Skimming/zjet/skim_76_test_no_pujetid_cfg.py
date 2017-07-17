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
input_files='file:///storage/b/fs6-mirror/fcolombo/kappatest/input/data_AOD_Run2015D.root' #do not remove: for Kappa test!
#input_files='dcap://cmssrm-kit.gridka.de:22125/pnfs/gridka.de/cms/store/mc/RunIISpring16DR80/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/20000/1A054918-89FF-E511-B246-0CC47A4D76B2.root'

maxevents=10
outputfilename="skim76.root"
miniaod = False ## not implemented yet 
kappa_verbosity=0




#  Basic Process Setup  ############################################
process = cms.Process("KAPPA")
process.path = cms.Path()
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(maxevents))
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))
process.source = cms.Source("PoolSource",
			    fileNames=cms.untracked.vstring(input_files)
			    )

#data = @IS_DATA@
#globaltag= '@GLOBALTAG@'

data = True
globaltag='76X_dataRun2_v15'


# With the lates JEC correction to be tested: 76X_mcRun2_asymptotic_RunIIFall15DR76_v1 and  76X_dataRun2_16Dec2015_v0

#  Config parameters  ##############################################
	## print information

print "\n------- CONFIGURATION 1 ---------"
print "input:          ", process.source.fileNames[0], "... (%d files)" % len(process.source.fileNames) if len(process.source.fileNames) > 1 else ""
print "file type:      ", "miniAOD" if miniaod else "AOD"
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
if data:
	process.kappaTuple.active += cms.vstring('DataInfo')
else:
	process.kappaTuple.active += cms.vstring('GenInfo', 'GenParticles')

	
process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)
process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")


	
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
	## miniAOD has NOT been tested, I'm just guessing names - MF@20150907
	## lets skip the miniAOD test (for leptons it will work, but not sure for the jets SW@20160303
	#	if miniaod:
	#		input_PFCandidates = 'packedPFCandidates'
	#		input_PFCandidatePtrs = 'packedPFCandidatesPtrs'
	#		input_PrimaryVertices = 'offlineSlimmedPrimaryVertices'

input_PFCandidates = 'particleFlow'
input_PFCandidatePtrs = 'particleFlowPtrs'
input_PrimaryVertices = 'goodOfflinePrimaryVertices'

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
						  )

	## ------------------------------------------------------------------------
	## TopProjections from CommonTools/ParticleFlow:
process.load("CommonTools.ParticleFlow.pfNoPileUpIso_cff")
process.load("CommonTools.ParticleFlow.pfParticleSelection_cff")


## pf candidate configuration for everything but CHS jets
# Modifications for new particleFlow Pointers
## pf candidate configuration for CHS jets
process.pfPileUp.PFCandidates = cms.InputTag(input_PFCandidatePtrs)
process.pfPileUp.Vertices  = cms.InputTag(input_PrimaryVertices)
process.pfPileUp.checkClosestZVertex	= False
process.pfNoPileUp.bottomCollection = cms.InputTag(input_PFCandidatePtrs)


## change the input collection. Not realy needed here
process.pfPileUpIso.PFCandidates = cms.InputTag(input_PFCandidatePtrs)
process.pfNoPileUpIso.bottomCollection = cms.InputTag(input_PFCandidatePtrs)


process.path *= (
	process.goodOfflinePrimaryVertices
	* process.pfParticleSelectionSequence
	)
	# Also skipp the PUPPI part here will follow later SF@20160303
#	if add_puppi:
## Now add also puppi jets 
#		## PUPPI - https://twiki.cern.ch/twiki/bin/viewauth/CMS/PUPPI
#		# creates filtered PFCandidates collection 'puppi'

## Usual Pupi stuff
process.load('CommonTools.PileupAlgos.Puppi_cff')
process.puppi.candName = cms.InputTag(input_PFCandidates)
process.puppi.vertexName = cms.InputTag(input_PrimaryVertices)

## Pupi no lep collection
process.PFCandidatesNoLep = cms.EDFilter("CandPtrSelector",
		src = cms.InputTag(input_PFCandidates), 
		cut = cms.string("abs(pdgId) != 13 && abs(pdgId) != 11")
	       )
process.puppinolep = process.puppi.clone(
	candName = cms.InputTag('PFCandidatesNoLep'),
	useWeightsNoLep = True
	)
process.PFNoPileUpCandidatesLep = cms.EDFilter("CandPtrSelector",
		src = cms.InputTag(input_PFCandidates),  
		cut = cms.string("abs(pdgId) == 13 && abs(pdgId) == 11")
	       )

process.pupinolepforjets = cms.EDProducer("CandViewMerger",
	src = cms.VInputTag( "puppinolep", "PFNoPileUpCandidatesLep")
	 )

process.path *= (process.puppi * (process.PFCandidatesNoLep *  process.puppinolep * process.PFNoPileUpCandidatesLep * process.pupinolepforjets))

#		# PFCandidates w/o muons for PUPPI - avoid misidentification from high-PT muons
#		process.PFCandidatesNoMu  = cms.EDFilter("CandPtrSelector",
#			src = cms.InputTag(input_PFCandidates),
#			cut = cms.string("abs(pdgId)!=13" )
#		)
#		process.PFCandidatesOnlyMu  = cms.EDFilter("CandPtrSelector",
#			src = cms.InputTag(input_PFCandidates),
#			cut = cms.string("abs(pdgId)==13" )
#		)
#		# veto without any muons
#		process.puppinomutmp = process.puppi.clone(
#			candName = cms.InputTag('PFCandidatesNoMu')
#		)
#		# nomu veto, muons merged back again for proper MET etc.
#		process.puppinomu = cms.EDProducer("CandViewMerger",
#			src = cms.VInputTag( "puppinomutmp", "PFCandidatesOnlyMu")
#		)
#		process.path *= (process.puppi * (process.PFCandidatesNoMu * process.PFCandidatesOnlyMu * process.puppinomutmp * process.puppinomu))

#  Muons  ##########################################################
process.load('Kappa.Skimming.KMuons_run2_cff')
process.kappaTuple.Muons.minPt = 8.0
process.kappaTuple.Muons.doPfIsolation = cms.bool(False)
process.kappaTuple.active += cms.vstring('Muons')
process.path *= (process.makeKappaMuons)

# Electrons ########################################################
process.load('Kappa.Skimming.KElectrons_run2_cff')
process.kappaTuple.Electrons.minPt = 8.0
process.kappaTuple.Electrons.ids = cms.VInputTag("cutBasedElectronID_Spring15_25ns_V1_standalone_loose",
					       "cutBasedElectronID_Spring15_25ns_V1_standalone_medium",
					       "cutBasedElectronID_Spring15_25ns_V1_standalone_tight",
					       "cutBasedElectronID_Spring15_25ns_V1_standalone_veto",
					       "ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values")
from Kappa.Skimming.KElectrons_run2_cff import setupElectrons
setupElectrons(process)

process.kappaTuple.active += cms.vstring('Electrons')
process.path *= process.makeKappaElectrons

#  Jets  ###########################################################
# Kappa jet processing
process.kappaTuple.Jets.minPt = 5.0
process.kappaTuple.Jets.taggers = cms.vstring()

	# containers for objects to process
#jet_resources = []
#cmssw_jets = {}  # algoname: cmssw module
kappa_jets = {}  # algoname: kappa jet config

# GenJets
if not data:
	process.load('RecoJets.Configuration.GenJetParticles_cff')
	process.load('RecoJets.JetProducers.ak5GenJets_cfi')
	process.path *=process.genParticlesForJetsNoNu
	process.kappaTuple.active += cms.vstring('LV')
	process.kappaTuple.LV.whitelist = cms.vstring('ak5GenJetsNoNu') #default?
	genbase_jet = process.ak5GenJets.clone(src=cms.InputTag("genParticlesForJetsNoNu"), doAreaFastjet=True)

	## PFBRECO?
process.load("RecoJets.JetProducers.ak5PFJets_cfi")
pfbase_jet = process.ak5PFJets.clone(srcPVs = 'goodOfflinePrimaryVertices', doAreaFastjet=True)

#process.load("RecoJets.JetProducers.ak5CaloJets_cfi")
#calobase_jet = process.ak5CaloJets.clone(srcPVs = 'goodOfflinePrimaryVertices')
#process.load("RecoJets.Configuration.CaloTowersRec_cff")
#process.path*=(process.caloTowersRec)

# for PUJetID
process.load("RecoJets.JetProducers.PileupJetID_cfi")
#pujetid_base = process.pileupJetId.clone(inputIsCorrected=False, applyJec=False, vertexes=cms.InputTag("goodOfflinePrimaryVertices"))



	# create Jet variants
for param in (4, 5, 8):
	# PFJets
	algos_and_tags = [("", input_PFCandidates), ("CHS", 'pfNoPileUp')]
	#		if add_puppi:
	algos_and_tags += [("Puppi", 'puppi'),("PuppiNoMu", 'pupinolepforjets')]
	for algo, input_tag in algos_and_tags:
		variant_name = "ak%dPFJets%s" % (param, algo)
		variant_module = pfbase_jet.clone(src=cms.InputTag(input_tag), rParam=param/10.0)
		setattr(process, variant_name, variant_module)
		process.path *=getattr(process, variant_name)
		
		# for PUJetID:
		variant_pujetid_name = "ak%dPF%sPuJetMva" % (param, algo)
		#variant_pujetid_module = pujetid_base.clone(jets = cms.InputTag(variant_name))
		#setattr(process, variant_pujetid_name, variant_pujetid_module)
		#process.path *=getattr(process, variant_pujetid_name)
		
		#cmssw_jets[variant_name] = variant_module
		# Full Kappa jet definition
		kappa_jets["ak%dPFJets%s"%(param, algo)] = cms.PSet(
			src = cms.InputTag(variant_name),
			PUJetID = cms.InputTag(variant_pujetid_name),
			PUJetID_full = cms.InputTag("full"),
			QGtagger = cms.InputTag("AK%dPFJets%sQGTagger" % (param, algo)),
			Btagger = cms.InputTag("ak%dPF%s" % (param, algo)),
			)

	# CaloJets
	if param == 4:
	#variant_name = "ak%dCaloJets" % (param)
	#variant_module = calobase_jet.clone(rParam=param/10.0)
	#setattr(process, variant_name, variant_module)
	#process.path *=getattr(process, variant_name)
		
		# for PUJetID:
        	#variant_pujetid_name = "ak%dCaloJetsPuJetMva" % (param)
        	#variant_pujetid_module = pujetid_base.clone(jets = cms.InputTag(variant_name))
        	#setattr(process, variant_pujetid_name, variant_pujetid_module)
        	#process.path *=getattr(process, variant_pujetid_name)


		kappa_jets["ak%dCaloJets"%(param)] = cms.PSet(
			src = cms.InputTag(variant_name),
			PUJetID = cms.InputTag(variant_pujetid_name),
			PUJetID_full = cms.InputTag("full"),
			QGtagger = cms.InputTag("AK%dCaloJetsQGTagger" % (param)),
			Btagger = cms.InputTag("ak%dCaloJets" % (param)),
			)

		# GenJets
	if not data:
		for collection in ("NoNu",): # TODO: add "NoMuNoNu", "" ?
			variant_name = "ak%sGenJets%s" % (param, collection)
			variant_module = genbase_jet.clone(rParam=param/10.0)
			setattr(process, variant_name, variant_module)
			process.path *=getattr(process, variant_name)
				# GenJets are just KLVs
			process.kappaTuple.LV.whitelist += cms.vstring(variant_name)
	# mount generated jets for processing
	
#for name, jet_module in cmssw_jets.iteritems():
#	setattr(process, name, jet_module)
for name, pset in kappa_jets.iteritems():
	setattr(process.kappaTuple.Jets, name, pset)
	
process.kappaTuple.Jets.taggers = cms.vstring(
#  "puJetIDFullDiscriminant", "puJetIDFullLoose", "puJetIDFullMedium", "puJetIDFullTight"
  ) 
#print reduce(lambda a, b: a * b, jet_resources + sorted(cmssw_jets.values()))
#process.path *= reduce(lambda a, b: a * b, jet_resources + sorted(cmssw_jets.values()))


	# Gluon tagging? - https://twiki.cern.ch/twiki/bin/viewauth/CMS/GluonTag
	# B-tagging (for ak5 jets)? - https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets
	# B-tagging for (ak5 CHS jets)? - https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookBTagging#DifferentJets
	# PileupDensity ########################
from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
process.pileupDensitykt6PFJets = kt4PFJets.clone(rParam=0.6, doRhoFastjet=True, Rho_EtaMax=2.5)

process.kappaTuple.active += cms.vstring('Jets', 'PileupDensity')
process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")

process.path *= (process.pileupDensitykt6PFJets)
	# MET correction ----------------------------------------------------------
	#TODO check type 0 corrections
from RecoMET.METProducers.PFMET_cfi import pfMet
process.pfMETCHS = pfMet.clone(src=cms.InputTag(input_PFCandidates))
process.kappaTuple.active += cms.vstring('MET')

# MET without forward region
process.PFCandidatesNoHF  = cms.EDFilter("CandPtrSelector",
					 src = cms.InputTag(input_PFCandidates),
					 cut = cms.string("abs(eta) < 3" )
					 )
process.pfMETCHSNoHF = pfMet.clone(src=cms.InputTag('PFCandidatesNoHF'))
process.path *= (process.pfMETCHS * process.PFCandidatesNoHF * process.pfMETCHSNoHF)

# CaloMet
#process.load("RecoMET.METProducers.CaloMET_cfi")
#process.caloMetForKappa = process.caloMet.clone()
#process.kappaTuple.MET.whitelist += cms.vstring('CaloMetForKappa')
#process.path *= (process.caloMetForKappa)
	
#	if add_puppi:
process.pfMetPuppi = pfMet.clone(src=cms.InputTag('puppi'))
process.pfMetPuppiNoMu = pfMet.clone(src=cms.InputTag('pupinolepforjets'))
process.path *= (
			process.pfMetPuppi
			* process.pfMetPuppiNoMu
		)

#		process.PuppiNoHF  = cms.EDFilter("CandPtrSelector",
#			src = cms.InputTag('puppi'),
#			cut = cms.string("abs(eta) < 3" )
#		)
#		process.PuppiNoMuNoHF  = cms.EDFilter("CandPtrSelector",
#			src = cms.InputTag('puppinomu'),
#			cut = cms.string("abs(eta) < 3" )
#		)
#		process.pfMetPuppiNoHF = pfMet.clone(src=cms.InputTag('PuppiNoHF'))
#		process.pfMetPuppiNoMuNoHF = pfMet.clone(src=cms.InputTag('PuppiNoMuNoHF'))
#		process.path *= (
#			process.PuppiNoHF * process.pfMetPuppiNoHF
#			* process.PuppiNoMuNoHF * process.pfMetPuppiNoMuNoHF
#		)
#
process.kappaTuple.MET.whitelist += cms.vstring('pfMetPuppi', 'pfMetPuppiNoMu')

	#  Kappa  Output ###########################################################
process.path *= (process.kappaOut)
	# explicit declaration until white/blacklist works again - MF@160119
	# note: extracted from running on CMSSW < 7_6
process.kappaTuple.BeamSpot.offlineBeamSpot = cms.PSet(src=cms.InputTag("offlineBeamSpot"))
process.kappaTuple.VertexSummary.offlinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("offlinePrimaryVertices"))
process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("goodOfflinePrimaryVertices"))

if not data:
	process.kappaTuple.LV.ak4GenJetsNoNu = cms.PSet(src=cms.InputTag("ak4GenJetsNoNu"))
	process.kappaTuple.LV.ak5GenJetsNoNu = cms.PSet(src=cms.InputTag("ak5GenJetsNoNu"))
	process.kappaTuple.LV.ak8GenJetsNoNu = cms.PSet(src=cms.InputTag("ak8GenJetsNoNu"))

process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAll"))
process.kappaTuple.PileupDensity.pileupDensityCalo = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAllCalo"))

process.kappaTuple.MET.pfChMet = cms.PSet(src=cms.InputTag("pfChMet"))
process.kappaTuple.MET.metCHS = cms.PSet(src=cms.InputTag("pfMETCHS"))
process.kappaTuple.MET.metCHSNoHF = cms.PSet(src=cms.InputTag("pfMETCHSNoHF"))
process.kappaTuple.MET.met = cms.PSet(src=cms.InputTag("pfMet"))
process.kappaTuple.MET.metEI = cms.PSet(src=cms.InputTag("pfMetEI"))
#process.kappaTuple.MET.caloMet = cms.PSet(src=cms.InputTag("caloMet"))
#	if channel == 'mm':
process.kappaTuple.MET.metPuppi = cms.PSet(src=cms.InputTag("pfMetPuppi"))
#			process.kappaTuple.MET.metPuppiNoHF = cms.PSet(src=cms.InputTag("pfMetPuppiNoHF"))
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
