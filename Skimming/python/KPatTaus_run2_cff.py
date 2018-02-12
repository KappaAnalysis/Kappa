#-# Copyright (c) 2014 - All Rights Reserved
#-#   Bastian Kargoll <bastian.kargoll@cern.ch>
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools

cmssw_version_number = tools.get_cmssw_version_number()

## ------------------------------------------------------------------------
##  rerun tau reconstruction sequence following POG recommendation:
##  https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Rerunning_of_the_tau_ID_on_MiniA
"""
	The tau ID configuration on MiniAOD event content in CMSSW_9_4_X can be found in the following wiki page:
	https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Rerunning_of_the_tau_ID_on_M_AN1
	It requires the package RecoTauTag:
	git cms-addpkg RecoTauTag/Configuration
	git cms-addpkg RecoTauTag/RecoTau
"""
## since we run in the unscheduled mode the normal import fails. Maybe a customizer would also be helpfull.

from RecoTauTag.RecoTau.TauDiscriminatorTools import noPrediscriminants
if not tools.is_above_cmssw_version([9]):
	from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import patDiscriminationByIsolationMVArun2v1raw as 	rerunDiscriminationByIsolationMVAOldDMrun2v1raw
	from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import patDiscriminationByIsolationMVArun2v1VLoose as rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose
if  tools.is_above_cmssw_version([9]):
	from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import patDiscriminationByIsolationMVArun2v1raw as 	rerunDiscriminationByIsolationMVArun2v1raw
	from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import patDiscriminationByIsolationMVArun2v1VLoose as rerunDiscriminationByIsolationMVArun2v1VLoose


from Kappa.Skimming.KSkimming_template_cfg import process
process.load('RecoTauTag.Configuration.loadRecoTauTagMVAsFromPrepDB_cfi')

##=== The following configurations can be removed when those will be added to the "RecoTauTag.Configuration.loadRecoTauTagMVAsFromPrepDB_cfi" config file ====
def loadMVA_WPs_run2_2017(process):
	for training, gbrForestName in tauIdDiscrMVA_trainings_run2_2017.items():

         process.loadRecoTauTagMVAsFromPrepDB.toGet.append(
            cms.PSet(
               record = cms.string('GBRWrapperRcd'),
               tag = cms.string("RecoTauTag_%s%s" % (gbrForestName, tauIdDiscrMVA_2017_version)),
               label = cms.untracked.string("RecoTauTag_%s%s" % (gbrForestName, tauIdDiscrMVA_2017_version))
            )
         )

         for WP in tauIdDiscrMVA_WPs_run2_2017[training].keys():
            process.loadRecoTauTagMVAsFromPrepDB.toGet.append(
               cms.PSet(
                  record = cms.string('PhysicsTGraphPayloadRcd'),
                  tag = cms.string("RecoTauTag_%s%s_WP%s" % (gbrForestName, tauIdDiscrMVA_2017_version, WP)),
                  label = cms.untracked.string("RecoTauTag_%s%s_WP%s" % (gbrForestName, tauIdDiscrMVA_2017_version, WP))
               )
            )

         process.loadRecoTauTagMVAsFromPrepDB.toGet.append(
            cms.PSet(
               record = cms.string('PhysicsTFormulaPayloadRcd'),
               tag = cms.string("RecoTauTag_%s%s_mvaOutput_normalization" % (gbrForestName, tauIdDiscrMVA_2017_version)),
               label = cms.untracked.string("RecoTauTag_%s%s_mvaOutput_normalization" % (gbrForestName, tauIdDiscrMVA_2017_version))
            )
)
tauIdDiscrMVA_trainings_run2_2017 = {
	'tauIdMVAIsoDBoldDMwLT2017' : "tauIdMVAIsoDBoldDMwLT2017",
	}

tauIdDiscrMVA_WPs_run2_2017 = {
	'tauIdMVAIsoDBoldDMwLT2017' : {
		'Eff95' : "DBoldDMwLTEff95",
		'Eff90' : "DBoldDMwLTEff90",
		'Eff80' : "DBoldDMwLTEff80",
		'Eff70' : "DBoldDMwLTEff70",
		'Eff60' : "DBoldDMwLTEff60",
		'Eff50' : "DBoldDMwLTEff50",
		'Eff40' : "DBoldDMwLTEff40"
		}
	}

tauIdDiscrMVA_2017_version = "v1"
if  tools.is_above_cmssw_version([9]):
	loadMVA_WPs_run2_2017(process)

if not tools.is_above_cmssw_version([9]):
	# new ids for oldDMs
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw.PATTauProducer = cms.InputTag('slimmedTaus')
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw.Prediscriminants = noPrediscriminants
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw.loadMVAfromDB = cms.bool(True)
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw.mvaName = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1")
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw.mvaOpt = cms.string("DBoldDMwLT")
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw.requireDecayMode = cms.bool(True)
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw.verbosity = cms.int32(0)

	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.PATTauProducer = cms.InputTag('slimmedTaus')
	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.Prediscriminants = noPrediscriminants
	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.toMultiplex = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1raw')
	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.key = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1raw:category')
	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.loadMVAfromDB = cms.bool(True)
	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.mvaOutput_normalization = cms.string	("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_mvaOutput_normalization")
	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.mapping = cms.VPSet(
		cms.PSet(
			category = cms.uint32(0),
			cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff90"),
			variable = cms.string("pt"),
			)
		)
if  tools.is_above_cmssw_version([9]):
	#	 n"w ids for oldDMs for 2017 training
	rerunDiscriminationByIsolationMVArun2v1raw.PATTauProducer = cms.InputTag('slimmedTaus')
	rerunDiscriminationByIsolationMVArun2v1raw.Prediscriminants = noPrediscriminants
	rerunDiscriminationByIsolationMVArun2v1raw.loadMVAfromDB = cms.bool(True)
	rerunDiscriminationByIsolationMVArun2v1raw.mvaName = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1")
	rerunDiscriminationByIsolationMVArun2v1raw.mvaOpt = cms.string("DBoldDMwLTwGJ")
	rerunDiscriminationByIsolationMVArun2v1raw.requireDecayMode = cms.bool(True)
	rerunDiscriminationByIsolationMVArun2v1raw.verbosity = cms.int32(0)

	rerunDiscriminationByIsolationMVArun2v1VLoose.PATTauProducer = cms.InputTag('slimmedTaus')
	rerunDiscriminationByIsolationMVArun2v1VLoose.Prediscriminants = noPrediscriminants
	rerunDiscriminationByIsolationMVArun2v1VLoose.toMultiplex = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1raw')
	rerunDiscriminationByIsolationMVArun2v1VLoose.key = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1raw:category')
	rerunDiscriminationByIsolationMVArun2v1VLoose.loadMVAfromDB = cms.bool(True)
	rerunDiscriminationByIsolationMVArun2v1VLoose.mvaOutput_normalization = cms.string	("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_mvaOutput_normalization")
	rerunDiscriminationByIsolationMVArun2v1VLoose.mapping = cms.VPSet(
		cms.PSet(
			category = cms.uint32(0),
			cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff90"),
			variable = cms.string("pt"),
		)
	)

if not tools.is_above_cmssw_version([9]):
	rerunDiscriminationByIsolationMVAOldDMrun2v1Loose = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVAOldDMrun2v1Loose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff80")
	rerunDiscriminationByIsolationMVAOldDMrun2v1Medium = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVAOldDMrun2v1Medium.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff70")
	rerunDiscriminationByIsolationMVAOldDMrun2v1Tight = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVAOldDMrun2v1Tight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff60")
	rerunDiscriminationByIsolationMVAOldDMrun2v1VTight = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVAOldDMrun2v1VTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff50")
	rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff40")

	# new ids for newDMs
	rerunDiscriminationByIsolationMVANewDMrun2v1raw = rerunDiscriminationByIsolationMVAOldDMrun2v1raw.clone()
	rerunDiscriminationByIsolationMVANewDMrun2v1raw.mvaName = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1")
	rerunDiscriminationByIsolationMVANewDMrun2v1raw.mvaOpt = cms.string("DBnewDMwLT")

	rerunDiscriminationByIsolationMVANewDMrun2v1VLoose = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.toMultiplex = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1raw')
	rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.key = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1raw:category')
	rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.mvaOutput_normalization = cms.string			("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_mvaOutput_normalization")
	rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff90")

	rerunDiscriminationByIsolationMVANewDMrun2v1Loose = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVANewDMrun2v1Loose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff80")
	rerunDiscriminationByIsolationMVANewDMrun2v1Medium = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVANewDMrun2v1Medium.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff70")
	rerunDiscriminationByIsolationMVANewDMrun2v1Tight = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVANewDMrun2v1Tight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff60")
	rerunDiscriminationByIsolationMVANewDMrun2v1VTight = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVANewDMrun2v1VTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff50")
	rerunDiscriminationByIsolationMVANewDMrun2v1VVTight = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVANewDMrun2v1VVTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff40")

if tools.is_above_cmssw_version([9]):

	rerunDiscriminationByIsolationMVArun2v1VVLoose = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVArun2v1VVLoose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff95")
	rerunDiscriminationByIsolationMVArun2v1VLoose = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVArun2v1VLoose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff90")
	rerunDiscriminationByIsolationMVArun2v1Loose = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVArun2v1Loose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff80")
	rerunDiscriminationByIsolationMVArun2v1Medium = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVArun2v1Medium.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff70")
	rerunDiscriminationByIsolationMVArun2v1Tight = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVArun2v1Tight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff60")
	rerunDiscriminationByIsolationMVArun2v1VTight = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVArun2v1VTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff50")
	rerunDiscriminationByIsolationMVArun2v1VVTight = rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
	rerunDiscriminationByIsolationMVArun2v1VVTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff40")

## ------------------------------------------------------------------------
## Definition of sequences

## run this to get latest greatest HPS taus
if not tools.is_above_cmssw_version([9]):
	makeKappaTaus = cms.Sequence(
		rerunDiscriminationByIsolationMVAOldDMrun2v1raw +
		rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose +
		rerunDiscriminationByIsolationMVAOldDMrun2v1Loose +
		rerunDiscriminationByIsolationMVAOldDMrun2v1Medium +
		rerunDiscriminationByIsolationMVAOldDMrun2v1Tight +
		rerunDiscriminationByIsolationMVAOldDMrun2v1VTight +
		rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight +
		rerunDiscriminationByIsolationMVANewDMrun2v1raw +
		rerunDiscriminationByIsolationMVANewDMrun2v1VLoose +
		rerunDiscriminationByIsolationMVANewDMrun2v1Loose +
		rerunDiscriminationByIsolationMVANewDMrun2v1Medium +
		rerunDiscriminationByIsolationMVANewDMrun2v1Tight +
		rerunDiscriminationByIsolationMVANewDMrun2v1VTight +
		rerunDiscriminationByIsolationMVANewDMrun2v1VVTight
	)
if tools.is_above_cmssw_version([9]):
	print "here"
	makeKappaTaus = cms.Sequence(
		rerunDiscriminationByIsolationMVArun2v1raw +
		rerunDiscriminationByIsolationMVArun2v1VVLoose +
		rerunDiscriminationByIsolationMVArun2v1VLoose +
		rerunDiscriminationByIsolationMVArun2v1Loose +
		rerunDiscriminationByIsolationMVArun2v1Medium +
		rerunDiscriminationByIsolationMVArun2v1Tight +
		rerunDiscriminationByIsolationMVArun2v1VTight +
		rerunDiscriminationByIsolationMVArun2v1VVTight
	)
