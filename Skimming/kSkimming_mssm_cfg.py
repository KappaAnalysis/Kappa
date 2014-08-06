import os
import sys
import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.datasetsHelper as datasetsHelper

def getBaseConfig(globaltag= 'START53_V15A::All', testfile=cms.untracked.vstring(""), maxevents=100, nickname = 'SM_VBFHToTauTau_M_90_powheg_pythia_8TeV', kappaTag = 'Kappa_1_0_0'):

	from Kappa.Producers.KSkimming_template_cfg import process
	process.source.fileNames      = testfile
	process.maxEvents.input	      = maxevents				## number of events to be processed (-1 = all in file)
	process.kappaTuple.outputFile = 'kappaTuple.root'			## name of output file
	process.kappaTuple.verbose    = cms.int32(0)				## verbosity level
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag   = globaltag
		print "GT (overwritten):", process.GlobalTag.globaltag
	data = datasetsHelper.isData(nickname)
	centerOfMassEnergy = datasetsHelper.getCenterOfMassEnergy(nickname)
	isEmbedded = datasetsHelper.getIsEmbedded(nickname)
	process.p = cms.Path ( )
	## ------------------------------------------------------------------------
	# Configure Metadata describing the file
	process.kappaTuple.active										= cms.vstring('TreeMetadata')
	process.kappaTuple.TreeMetadata.parameters = cms.PSet(
		dataset						= cms.string(datasetsHelper.getDatasetName(nickname)),
		generator					= cms.string(datasetsHelper.getGenerator(nickname)),
		productionProcess			= cms.string(datasetsHelper.getProcess(nickname)),
		globalTag					= cms.string(globaltag),
		prodCampaignGlobalTag	= cms.string(datasetsHelper.getProductionCampaignGlobalTag(nickname, centerOfMassEnergy)),
		runPeriod					= cms.string(datasetsHelper.getRunPeriod(nickname)),
		kappaTag						= cms.string(kappaTag),
		isEmbedded					= cms.bool(isEmbedded),
		jetMultiplicity			= cms.int32(datasetsHelper.getJetMultiplicity(nickname)),
		centerOfMassEnergy		= cms.int32(centerOfMassEnergy),
		puScenario					= cms.string(datasetsHelper.getPuScenario(nickname, centerOfMassEnergy)),
		isData						= cms.bool(data)
		)


	## ------------------------------------------------------------------------
	# General configuration

	process.kappaTuple.active += cms.vstring('VertexSummary')	## save VertexSummary,
	process.kappaTuple.active += cms.vstring('BeamSpot')		## save Beamspot,
	process.kappaTuple.active += cms.vstring('TriggerObjects')

	if data:
		process.kappaTuple.active+= cms.vstring('DataMetadata')		## produce Metadata for data,
	else:
		process.kappaTuple.active+= cms.vstring('GenMetadata')		## produce Metadata for MC,
		process.kappaTuple.active+= cms.vstring('GenParticles')		## save GenParticles,
		process.kappaTuple.active+= cms.vstring('GenTaus')				## save GenParticles,

	process.kappaTuple.Metadata.hltWhitelist = cms.vstring(			## HLT selection
		# https://github.com/cms-analysis/HiggsAnalysis-KITHiggsToTauTau/blob/master/data/triggerTables-2011-2012.txt
		# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauWorkingSummer2013
		# can be tested at http://regexpal.com
		# e
		"^HLT_Ele[0-9]+_CaloIdVT(_CaloIsoT)?_TrkIdT(_TrkIsoT)?_v[0-9]+$",
		"^HLT_Ele[0-9]+_WP[0-9]+_v[0-9]+$",
		# m
		"^HLT_(Iso)?Mu[0-9]+(_eta2p1)?_v[0-9]+$",
		# ee
		"^HLT_Ele[0-9]+_CaloId(L|T)(_TrkIdVL)?_CaloIsoVL(_TrkIdVL)?(_TrkIsoVL)?" +
			"_Ele[0-9]+_CaloId(L|T)(_TrkIdVL)?_CaloIsoVL(_TrkIdVL)?(_TrkIsoVL)?_v[0-9]+$",
		"^HLT_Ele[0-9]+_Ele[0-9]+_CaloId(L|T)_CaloIsoVL(_TrkIdVL_TrkIsoVL)?_v[0-9]+$",
		# mm
		"^HLT_(Double)?Mu[0-9]+(_(Mu|Jet)[0-9]+)?_v[0-9]+$",
		# em
		"^HLT_Mu[0-9]+_(Ele|Photon)[0-9]+_CaloId(L|T|VT)(_CaloIsoVL|_IsoT)?(_TrkIdVL_TrkIsoVL)?_v[0-9]+$",
		# et
		"^HLT_Ele[0-9]+_CaloIdVT(_Calo(IsoRho|Iso)T)?_TrkIdT(_TrkIsoT)?_(Loose|Medium|Tight)IsoPFTau[0-9]+_v[0-9]+$",
		"^HLT_Ele[0-9]+_eta2p1_WP[0-9]+(Rho|NoIso)_LooseIsoPFTau[0-9]+_v[0-9]+$",
		# mt
		"^HLT_(Iso)?Mu[0-9]+(_eta2p1)?_(Loose|Medium|Tight)IsoPFTau[0-9]+(_Trk[0-9]_eta2p1)?_v[0-9]+$",
		# tt
		"^HLT_Double(Medium)?IsoPFTau[0-9]+_Trk(1|5)_eta2p1_(Jet[0-9]+|Prong[0-9])?_v[0-9]+$",
		"^HLT_Double(Medium)?IsoPFTau[0-9]+_Trk(1|5)(_eta2p1)?_v[0-9]+$",
		# specials (possible generalization: Mu15, L1ETM20, Photon20, Ele8)
		"^HLT_Ele[0-9]+_CaloId(L|T|VT)_CaloIso(VL|T|VT)(_TrkIdT)?(_TrkIsoVT)?_(SC|Ele)[0-9](_Mass[0-9]+)?_v[0-9]+$",
		"^HLT_Ele8_v[0-9]+$",
		"^HLT_IsoMu15(_eta2p1)?_L1ETM20_v[0-9]+$",
		"^HLT_Photon20_CaloIdVT_IsoT_Ele8_CaloIdL_CaloIsoVL_v[0-9]+$",
		# specials for tag and probe and em fakerate studies could be added if enough bits are ensured
		#"^HLT_Ele[0-9]+_CaloId(L|T|VT)_CaloIso(VL|T|VT)(_TrkIdT_TrkIso(T|VT))?_(SC|Ele)[0-9]+(_Mass[0-9]+)?_v[0-9]+$",
		#"^HLT_Mu[0-9]+_Photon[0-9]+_CaloIdVT_IsoT_v[0-9]+$",
		#"^HLT_Ele[0-9]+_CaloId(L|T)(_TrkIdVL)?_CaloIsoVL(_TrkIdVL_TrkIsoVL)?(_TrkIsoVL)?(_Jet[0-9]+|)?_v[0-9]+$",
		)

	process.kappaTuple.Metadata.hltFailToleranceList = cms.vstring(
		"hltDoubleL2Tau25eta2p1",
		"hltDoubleL2Tau30eta2p1",
		"hltDoubleL2Tau35eta2p1",
		"hltL2Tau25eta2p1",
		"hltL2Tau35eta2p1",
		"hltL2fL1sMu16Eta2p1L1f0L2Filtered16Q",
		)

	## ------------------------------------------------------------------------
	# Configure PFCandidates and offline PV
	process.load("Kappa.Producers.KPFCandidates_cff")
	process.kappaTuple.active += cms.vstring('PFCandidates')		## save PFCandidates for deltaBeta corrected 
	process.kappaTuple.PFCandidates.whitelist = cms.vstring(                ## isolation used for electrons and muons.
##		"pfNoPileUpChargedHadrons",    ## switch to pfAllChargedParticles
		"pfAllChargedParticles",       ## same as pfNoPileUpChargedHadrons +pf_electrons + pf_muons
		"pfNoPileUpNeutralHadrons",
		"pfNoPileUpPhotons",
		"pfPileUpChargedHadrons",
		)

	process.p *= ( process.makePFBRECO * process.makePFCandidatesForDeltaBeta )

	## ------------------------------------------------------------------------
	# Configure Muons
	process.load("Kappa.Producers.KMuons_cff")
	process.kappaTuple.active += cms.vstring('Muons')	                ## produce/save KappaMuons
	process.p *= process.makeKappaMuons

	## ------------------------------------------------------------------------
	# Configure Electrons
	process.load("Kappa.Producers.KElectrons_cff")
	process.kappaTuple.active += cms.vstring('Electrons')	                ## produce/save KappaElectrons,
	process.p *= process.makeKappaElectrons

	## ------------------------------------------------------------------------
	# Configure Taus
	process.load("Kappa.Producers.KTaus_cff")
	process.kappaTuple.active += cms.vstring('PFTaus')	                ## produce/save KappaTaus
	process.kappaTuple.PFTaus.hpsPFTaus.binaryDiscrWhitelist = cms.vstring(
		"hpsPFTauDiscriminationByDecayModeFinding",
		"hpsPFTauDiscriminationByDecayModeFindingOldDMs",
		"hpsPFTauDiscriminationByDecayModeFindingNewDMs",
		#against electrons
		"hpsPFTauDiscriminationByLooseElectronRejection",
		"hpsPFTauDiscriminationByMediumElectronRejection",
		"hpsPFTauDiscriminationByTightElectronRejection",
		"hpsPFTauDiscriminationByMVA5VLooseElectronRejection",
		"hpsPFTauDiscriminationByMVA5LooseElectronRejection",
		"hpsPFTauDiscriminationByMVA5MediumElectronRejection",
		"hpsPFTauDiscriminationByMVA5TightElectronRejection",
		"hpsPFTauDiscriminationByMVA5VTightElectronRejection",
		#against muons
		"hpsPFTauDiscriminationByMVALooseMuonRejection",
		"hpsPFTauDiscriminationByMVAMediumMuonRejection",
		"hpsPFTauDiscriminationByMVATightMuonRejection",
		"hpsPFTauDiscriminationByLooseMuonRejection3",
		"hpsPFTauDiscriminationByTightMuonRejection3",
		#isolation
		"hpsPFTauDiscriminationByVLooseIsolation",
		
		"hpsPFTauDiscriminationByVLooseCombinedIsolationDBSumPtCorr",
		"hpsPFTauDiscriminationByLooseCombinedIsolationDBSumPtCorr",
		"hpsPFTauDiscriminationByMediumCombinedIsolationDBSumPtCorr",
		"hpsPFTauDiscriminationByTightCombinedIsolationDBSumPtCorr",
		
		"hpsPFTauDiscriminationByLooseCombinedIsolationDBSumPtCorr3Hits",
		"hpsPFTauDiscriminationByMediumCombinedIsolationDBSumPtCorr3Hits"
		"hpsPFTauDiscriminationByTightCombinedIsolationDBSumPtCorr3Hits",
		
		"hpsPFTauDiscriminationByVLooseIsolationMVA3oldDMwoLT",
		"hpsPFTauDiscriminationByLooseIsolationMVA3oldDMwoLT",
		"hpsPFTauDiscriminationByMediumIsolationMVA3oldDMwoLT",
		"hpsPFTauDiscriminationByTightIsolationMVA3oldDMwoLT",
		"hpsPFTauDiscriminationByVTightIsolationMVA3oldDMwoLT",
		"hpsPFTauDiscriminationByVVTightIsolationMVA3oldDMwoLT",
		
		"hpsPFTauDiscriminationByVLooseIsolationMVA3oldDMwLT",
		"hpsPFTauDiscriminationByLooseIsolationMVA3oldDMwLT",
		"hpsPFTauDiscriminationByMediumIsolationMVA3oldDMwLT",
		"hpsPFTauDiscriminationByTightIsolationMVA3oldDMwLT",
		"hpsPFTauDiscriminationByVTightIsolationMVA3oldDMwLT",
		"hpsPFTauDiscriminationByVVTightIsolationMVA3oldDMwLT",
		
		"hpsPFTauDiscriminationByVLooseIsolationMVA3newDMwoLT",
		"hpsPFTauDiscriminationByLooseIsolationMVA3newDMwoLT",
		"hpsPFTauDiscriminationByMediumIsolationMVA3newDMwoLT",
		"hpsPFTauDiscriminationByTightIsolationMVA3newDMwoLT",
		"hpsPFTauDiscriminationByVTightIsolationMVA3newDMwoLT",
		"hpsPFTauDiscriminationByVVTightIsolationMVA3newDMwoLT",
		
		"hpsPFTauDiscriminationByVLooseIsolationMVA3newDMwLT",
		"hpsPFTauDiscriminationByLooseIsolationMVA3newDMwLT",
		"hpsPFTauDiscriminationByMediumIsolationMVA3newDMwLT",
		"hpsPFTauDiscriminationByTightIsolationMVA3newDMwLT",
		"hpsPFTauDiscriminationByVTightIsolationMVA3newDMwLT",
		"hpsPFTauDiscriminationByVVTightIsolationMVA3newDMwLT",

		#old (and not in new)
		#"hpsPFTauDiscriminationByMVA3LooseElectronRejection", #not working
		#"hpsPFTauDiscriminationByMVA3MediumElectronRejection", #not working
		
		"hpsPFTauDiscriminationByLooseMuonRejection",
		"hpsPFTauDiscriminationByTightMuonRejection",
		)
	process.p *= process.makeKappaTaus

	## ------------------------------------------------------------------------
	## KappaPFTaggedJets
	process.load("Kappa.Producers.KPFTaggedJets_cff")
	process.kappaTuple.active += cms.vstring('PFTaggedJets')           ## produce KappaPFTaggedJets
	process.kappaTuple.PFTaggedJets = cms.PSet(
		process.kappaNoCut,
		process.kappaNoRegEx,
		taggers = cms.vstring(
			"QGlikelihood",
			"QGmlp",
			"TrackCountingHighEffBJetTags",
			"TrackCountingHighPurBJetTags", 
			"JetProbabilityBJetTags",
			"JetBProbabilityBJetTags", 
			"SoftElectronBJetTags",
			"SoftMuonBJetTags",
			"SoftMuonByIP3dBJetTags",
			"SoftMuonByPtBJetTags",
			"SimpleSecondaryVertexBJetTags", 
			"CombinedSecondaryVertexBJetTags",
			"CombinedSecondaryVertexMVABJetTags",
			"puJetIDFullLoose",
			"puJetIDFullMedium",
			"puJetIDFullTight",
			"puJetIDCutbasedLoose",
			"puJetIDCutbasedMedium",
			"puJetIDCutbasedTight" 
			),
		AK5PFTaggedJets = cms.PSet(
			src = cms.InputTag("ak5PFJets"),
			QGtagger = cms.InputTag("AK5PFJetsQGTagger"),
			Btagger  = cms.InputTag("ak5PF"),
			PUJetID  = cms.InputTag("ak5PFPuJetMva"),
			PUJetID_full = cms.InputTag("full"),
			),
		AK5PFTaggedJetsCHS = cms.PSet(
			src = cms.InputTag("ak5PFJetsCHS"),
			QGtagger = cms.InputTag("AK5PFJetsCHSQGTagger"),
			Btagger  = cms.InputTag("ak5PFCHS"),
			PUJetID  = cms.InputTag("ak5PFCHSPuJetMva"),
			PUJetID_full = cms.InputTag("full"),
			),
		)
	process.kappaTuple.active += cms.vstring('JetArea')

	## ------------------------------------------------------------------------
	# Special settings for embedded samples
	# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonTauReplacementWithPFlow
	if isEmbedded:
		process.load('RecoBTag/Configuration/RecoBTag_cff')
		process.load('RecoJets/JetAssociationProducers/ak5JTA_cff')
		process.ak5PFJetNewTracksAssociatorAtVertex.tracks = "tmfTracks"
		process.ak5PFCHSNewJetTracksAssociatorAtVertex.tracks = "tmfTracks"
		process.p *= process.btagging
		# disable overrideHLTCheck for embedded samples, since it triggers an Kappa error
		process.kappaTuple.Metadata.overrideHLTCheck = cms.untracked.bool(True)
		process.kappaTuple.active+= cms.vstring('GenParticles')		## save GenParticles,
		process.kappaTuple.active+= cms.vstring('GenTaus')				## save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("genParticles","","EmbeddedRECO")
		process.kappaTuple.isEmbedded = cms.bool(True)

	# Let Jets run
	process.p *= (
		process.makeKappaTaus *
		process.makePFJets *
		process.makePFJetsCHS *
		process.makeQGTagging *
		process.makeBTagging *
		process.makePUJetID
	)

	## ------------------------------------------------------------------------
	## MET
	process.load("Kappa.Producers.KMET_mssm_cff")
	process.kappaTuple.active += cms.vstring('MET')                         ## produce/save KappaMET
	process.kappaTuple.active += cms.vstring('PFMET')                       ## produce/save KappaPFMET
	process.p *= process.makeKappaMET

	## ------------------------------------------------------------------------
	## And let it run
	process.p *= (
		process.kappaOut
	)
	## ------------------------------------------------------------------------
	## declare edm OutputModule (expects a path 'p'), uncommented if wanted

	#process.edmOut = cms.OutputModule(
	#	"PoolOutputModule",
	#	fileName = cms.untracked.string('dump.root'),				## name of output file
	#	SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),	## save only events passing the full path
	#	outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')	## save each edm object that has been produced by process KAPPA
	#	)
	#process.ep = cms.EndPath(process.edmOut)

	return process

if __name__ == "__main__":
	if('@' in '@NICK@'): # run local skim by hand without replacements by grid-control
		## test file for EKP
		#testfile	= cms.untracked.vstring('file:/storage/a/friese/aod/pfEmbedded.root')
		#testfile	= cms.untracked.vstring('file:/storage/a/friese/aod/tauPlusX.root')
		#testfile	= cms.untracked.vstring('file:/storage/a/friese/aod/VBF-Htautau.root')
		#testfile	= cms.untracked.vstring('file:/storage/6/berger/testfiles/data_2012C_AOD.root')
		## test file for lxplus
		#testfile	= cms.untracked.vstring('root://eoscms//eos/cms/store/relval/CMSSW_5_3_6-START53_V14/RelValProdTTbar/AODSIM/v2/00000/76ED0FA6-1E2A-E211-B8F1-001A92971B72.root')
		## test file for RWTH
		#testfile	= cms.untracked.vstring('file:/user/kargoll/testfiles/DYTauTau/DYTauTau_Summer12.root')		
		testfile	= cms.untracked.vstring('file:/nfs/dust/cms/user/ffrensch/storage/SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/test.root')
		process = getBaseConfig(testfile = testfile)

	## for grid-control:
	else:
		process = getBaseConfig('@GLOBALTAG@', nickname = '@NICK@', kappaTag = '@KAPPA_TAG@')



