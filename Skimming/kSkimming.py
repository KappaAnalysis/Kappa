import os
import sys
import FWCore.ParameterSet.Config as cms
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0])) + "/Kappa/")

def getBaseConfig(globaltag, testfile="", maxevents=100, datatype='data'):

	from Kappa.Producers.KSkimming_template_cfg import process
	process.source.fileNames = testfile

	process.maxEvents.input			= maxevents										## number of events to be processed (-1 = all in file)
	process.kappaTuple.outputFile	= 'kappaTuple.root'							## name of output file
	process.kappaTuple.verbose		= cms.int32(0)									## verbosity level

	data = (datatype == 'data')


	## ------------------------------------------------------------------------
	# General configuration

	process.kappaTuple.active		= cms.vstring('VertexSummary')			## save VertexSummary,
	process.kappaTuple.active		+= cms.vstring('BeamSpot')					## save Beamspot,

	if data:
		process.kappaTuple.active		+= cms.vstring('DataMetadata')		## produce Metadata for data,
	else:
		process.kappaTuple.active		+= cms.vstring('GenMetadata')		## produce Metadata for MC,
		process.kappaTuple.active		+= cms.vstring('GenParticles')		## save GenParticles,


	## ------------------------------------------------------------------------
	# Configure Electrons

	process.kappaTuple.active		+= cms.vstring('Electrons')			## produce KappaElectrons,
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
	process.kappaTuple.active			+= cms.vstring('PFTaus')					## produce KappaTaus
	process.load("Kappa.Producers.KTaus_cff")

	## ------------------------------------------------------------------------
	## KappaPFTaggedJets
	process.load("Kappa.Producers.KPFTaggedJets_cff")

	process.kappaTuple.PFTaggedJets = cms.PSet(
				process.kappaNoCut,
				process.kappaNoRegEx,
				taggers = cms.vstring(
					"QGlikelihood", "QGmlp",
					"TrackCountingHighEffBJetTags", "TrackCountingHighPurBJetTags", 
					"JetProbabilityBJetTags", "JetBProbabilityBJetTags", 
					"SoftElectronBJetTags", "SoftMuonBJetTags", "SoftMuonByIP3dBJetTags", "SoftMuonByPtBJetTags",
					"SimpleSecondaryVertexBJetTags", 
					"CombinedSecondaryVertexBJetTags", "CombinedSecondaryVertexMVABJetTags",
					"puJetIDFullLoose", "puJetIDFullMedium", "puJetIDFullTight",
					"puJetIDCutbasedLoose", "puJetIDCutbasedMedium", "puJetIDCutbasedTight" 
				),
				AK5PFTaggedJets = cms.PSet(
					src = cms.InputTag("ak5PFJets"),
					QGtagger = cms.InputTag("AK5PFJetsQGTagger"),
					Btagger = cms.InputTag("ak5PF"),
					PUJetID = cms.InputTag("ak5PFPuJetMva"),
					PUJetID_full = cms.InputTag("full"),
				),
				AK5PFTaggedJetsCHS = cms.PSet(
					src = cms.InputTag("ak5PFJetsCHS"),
					QGtagger = cms.InputTag("AK5PFJetsCHSQGTagger"),
					Btagger = cms.InputTag("ak5PFCHS"),
					PUJetID = cms.InputTag("ak5PFCHSPuJetMva"),
					PUJetID_full = cms.InputTag("full"),
				),
			)


	## ------------------------------------------------------------------------
	## MET
	process.kappaTuple.active += cms.vstring('MET')
	process.kappaTuple.active += cms.vstring('PFMET')
	process.load("Kappa.Producers.KMET_cff")

	## ------------------------------------------------------------------------
	## And let it run
	process.p = cms.Path(
		process.makeKappaElectrons *
		process.pfmuIsoDepositPFCandidates *
		process.makeKappaTaus *
		process.pfMEtMVAsequence *
		process.makePfCHS *
		process.makePFJets *
		process.makePFJetsCHS *
		process.makeQGTagging *
		process.makeBTagging *
		process.makePUJetID
	)

	## ------------------------------------------------------------------------
	## declare edm OutputModule (expects a path 'p'), uncommented if wanted

	process.edmOut = cms.OutputModule("PoolOutputModule",
											fileName = cms.untracked.string('dump.root'),					## name of output file
											SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),	## save only events passing the full path
											outputCommands = cms.untracked.vstring('drop *', 'keep *_*_*_KAPPA')		## save each edm object that has been produced by process KAPPA
											)
	process.kappaOut+=process.edmOut

	return process

if __name__ == "__main__":
	# for grid-control:
	# process = getBaseConfig('@GLOBALTAG@', datatype='@TYPE@')

	## test file for EKP
	#testfile	= cms.untracked.vstring('file:/storage/8/dhaitz/testfiles/mc11.root')
	testfile	= cms.untracked.vstring('file:/storage/6/berger/testfiles/data_2012C_AOD.root')
	## test file for lxplus
	testfile	= cms.untracked.vstring('root://eoscms//eos/cms/store/relval/CMSSW_5_3_6-START53_V14/RelValProdTTbar/AODSIM/v2/00000/76ED0FA6-1E2A-E211-B8F1-001A92971B72.root')
	## test file for RWTH
	#testfile	= cms.untracked.vstring('file:/user/kargoll/testfiles/DYTauTau/DYTauTau_Summer12.root')

	process = getBaseConfig(globaltag = 'FT53_V21A_AN6', testfile = testfile, maxevents = 100, datatype = 'mc')
