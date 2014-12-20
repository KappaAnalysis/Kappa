
import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.datasetsHelper as datasetsHelper
import Kappa.Skimming.tools as tools


def getBaseConfig(globaltag= 'START53_V15A::All', testfile=cms.untracked.vstring(""), maxevents=100, nickname = 'SM_VBFHToTauTau_M_90_powheg_pythia_8TeV', kappaTag = 'Kappa_1_0_0'):

	from Kappa.Producers.KSkimming_template_cfg import process
	process.source.fileNames      = testfile
	process.maxEvents.input	      = maxevents				## number of events to be processed (-1 = all in file)
	process.kappaTuple.outputFile = 'kappaTuple.root'			## name of output file
	process.kappaTuple.verbose    = cms.int32(0)				## verbosity level
	process.kappaTuple.profile    = cms.bool(True)
	if not globaltag.lower() == 'auto' :
		process.GlobalTag.globaltag   = globaltag
		print "GT (overwritten):", process.GlobalTag.globaltag
	data = datasetsHelper.isData(nickname)
	centerOfMassEnergy = datasetsHelper.getCenterOfMassEnergy(nickname)
	isEmbedded = datasetsHelper.getIsEmbedded(nickname)
	
	process.p = cms.Path ( )
	## ------------------------------------------------------------------------
	# Configure Metadata describing the file
	process.kappaTuple.active										= cms.vstring('TreeInfo')
	process.kappaTuple.TreeInfo.parameters = cms.PSet(
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

	if not isEmbedded:
		if data:
			process.kappaTuple.active+= cms.vstring('DataInfo')		## produce Metadata for data,
		else:
			process.kappaTuple.active+= cms.vstring('GenInfo')		## produce Metadata for MC,
			process.kappaTuple.active+= cms.vstring('GenParticles')		## save GenParticles,
			process.kappaTuple.active+= cms.vstring('GenTaus')				## save GenParticles,
	
	# prune GenParticles
	if not data and not isEmbedded:
		process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
		process.prunedGenParticles = cms.EDProducer("GenParticlePruner",
			src = cms.InputTag("genParticles", "", "SIM"),
			select = cms.vstring(
				"drop  *",
				"keep status == 3",  # all status 3
				"keep++ abs(pdgId) == 23", # Z
				"keep++ abs(pdgId) == 24", # W
				"keep++ abs(pdgId) == 25", # H
				"keep abs(pdgId) == 11 || abs(pdgId) == 13",  # charged leptons
				"keep++ abs(pdgId) == 15"  # keep full tau decay chain
			)
		)
	
	process.kappaTuple.Info.hltWhitelist = cms.vstring(			## HLT selection
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
	
	process.kappaTuple.Info.hltBlacklist = cms.vstring(
		"HLT_Mu13_Mu8", # v21 gives errors for the trigger objects
		)

	## ------------------------------------------------------------------------
	# Configure PFCandidates and offline PV
	process.load("Kappa.Producers.KPFCandidates_cff")
	#process.kappaTuple.active += cms.vstring('PFCandidates')		## save PFCandidates for deltaBeta corrected
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
	process.kappaTuple.Muons.minPt = cms.double(8.0)
	process.p *= process.makeKappaMuons

	## ------------------------------------------------------------------------
	# Configure Electrons
	process.load("Kappa.Producers.KElectrons_cff")
	process.kappaTuple.active += cms.vstring('Electrons')	                ## produce/save KappaElectrons,
	process.kappaTuple.Electrons.ids = cms.vstring("mvaTrigV0",
	                                               "mvaTrigNoIPV0",
	                                               "mvaNonTrigV0")
	process.kappaTuple.Electrons.minPt = cms.double(8.0)
	process.p *= process.makeKappaElectrons
	
	## for electron iso
	from CommonTools.ParticleFlow.Tools.pfIsolation import setupPFElectronIso #, setupPFMuonIso
	process.eleIsoSequence = setupPFElectronIso(process, 'patElectrons')
	
	# https://github.com/ajgilbert/ICHiggsTauTau/blob/master/test/higgstautau_cfg.py#L418-L448
	process.eleIsoSequence.remove(process.elPFIsoValueCharged03NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValueChargedAll03NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValueGamma03NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValueNeutral03NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValuePU03NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValueCharged04NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValueChargedAll04NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValueGamma04NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValueNeutral04NoPFIdPFIso)
	process.eleIsoSequence.remove(process.elPFIsoValuePU04NoPFIdPFIso)
	process.elPFIsoValueGamma04PFIdPFIso.deposits[0].vetos      = cms.vstring('EcalEndcaps:ConeVeto(0.08)','EcalBarrel:ConeVeto(0.08)')
	process.elPFIsoValueNeutral04PFIdPFIso.deposits[0].vetos    = cms.vstring()
	process.elPFIsoValuePU04PFIdPFIso.deposits[0].vetos         = cms.vstring()
	process.elPFIsoValueCharged04PFIdPFIso.deposits[0].vetos    = cms.vstring('EcalEndcaps:ConeVeto(0.015)')
	process.elPFIsoValueChargedAll04PFIdPFIso.deposits[0].vetos = cms.vstring('EcalEndcaps:ConeVeto(0.015)','EcalBarrel:ConeVeto(0.01)')
	process.pfiso = cms.Sequence(process.pfParticleSelectionSequence + process.eleIsoSequence)

	# rho for electron iso
	from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
	process.kt6PFJetsForIsolation = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
	process.kt6PFJetsForIsolation.Rho_EtaMax = cms.double(2.5)
	process.p *= (process.pfiso * process.kt6PFJetsForIsolation)

	## ------------------------------------------------------------------------
	# Configure Taus
	process.load("Kappa.Producers.KTaus_cff")
	process.kappaTuple.active += cms.vstring('Taus')	                ## produce/save KappaTaus
	process.kappaTuple.Taus.minPt = cms.double(8.0)
	process.p *= process.makeKappaTaus

	## ------------------------------------------------------------------------
	## KappaPFTaggedJets
	process.load("Kappa.Producers.KPFTaggedJets_cff")
	process.kappaTuple.active += cms.vstring('Jets')           ## produce KappaPFTaggedJets
	process.kappaTuple.Jets = cms.PSet(
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
			"puJetIDFullDiscriminant",
			"puJetIDFullLoose",
			"puJetIDFullMedium",
			"puJetIDFullTight",
			"puJetIDCutbasedDiscriminant",
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
	process.kappaTuple.Jets.minPt = cms.double(10.0)
	process.kappaTuple.active += cms.vstring('PileupDensity')

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
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)
		process.kappaTuple.active+= cms.vstring('DataInfo')
		process.kappaTuple.active+= cms.vstring('GenParticles')		## save GenParticles,
		process.kappaTuple.active+= cms.vstring('GenTaus')				## save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("genParticles","","EmbeddedRECO")
		process.kappaTuple.Info.isEmbedded = cms.bool(True)

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
	process.load("Kappa.Producers.KMET_cff")
	process.kappaTuple.active += cms.vstring('BasicMET')                         ## produce/save KappaMET
	process.kappaTuple.active += cms.vstring('MET')                       ## produce/save KappaPFMET
	process.p *= process.makeKappaMET
	#"""
	
	# add python config to TreeInfo
	process.kappaTuple.TreeInfo.parameters.config = cms.string(process.dumpPython())
	
	# add repository revisions to TreeInfo
	for repo, rev in tools.get_repository_revisions().iteritems():
		setattr(process.kappaTuple.TreeInfo.parameters, repo, cms.string(rev))
	

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
		testfile	= cms.untracked.vstring('file:/storage/a/friese/aod/VBF-Htautau.root')
		#testfile	= cms.untracked.vstring('file:/storage/6/berger/testfiles/data_2012C_AOD.root')
		## test file for lxplus
		#testfile	= cms.untracked.vstring('root://eoscms//eos/cms/store/relval/CMSSW_5_3_6-START53_V14/RelValProdTTbar/AODSIM/v2/00000/76ED0FA6-1E2A-E211-B8F1-001A92971B72.root')
		## test file for NAF
		#testfile	= cms.untracked.vstring('file:///nfs/dust/cms/user/fcolombo/VBF_HToTauTau_M-125_8TeV_powheg_pythia6_Summer12_DR53X-PU_S10_START53_V7A-v1_004B56D8-AAED-E111-AB70-1CC1DE1CEDB2.root')
		## test file for RWTH
		#testfile	= cms.untracked.vstring('file:/user/kargoll/testfiles/DYTauTau/DYTauTau_Summer12.root')
		process = getBaseConfig(testfile = testfile)

	## for grid-control:
	else:
		process = getBaseConfig('@GLOBALTAG@', nickname = '@NICK@', kappaTag = '@KAPPA_TAG@')

