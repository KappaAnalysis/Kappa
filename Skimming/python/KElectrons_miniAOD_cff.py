
import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools

cmssw_version_number = tools.get_cmssw_version_number()

from PhysicsTools.SelectorUtils.tools.vid_id_tools import *

# https://github.com/ikrav/EgammaWork/blob/v1/ElectronNtupler/test/runElectrons_VID_MVA_PHYS14_demo.py
from PhysicsTools.SelectorUtils.tools.vid_id_tools import switchOnVIDElectronIdProducer, DataFormat
from RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cff import *

"""
	The electron ID(MVA) configuration on MiniAOD event content in CMSSW_9_4_X can be found in the following wiki page:
	https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentificationRun2#Recommended_MVA_Recipe_for_regul
"""

def setupElectrons(process, electrons):
	egmGsfElectronIDs.physicsObjectSrc = cms.InputTag(electrons)
	switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)

	my_id_modules = []
	if tools.is_above_cmssw_version([9]):
		my_id_modules.extend(['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V1_cff',
			'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V1_cff',
			'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V1_cff'])
	elif tools.is_above_cmssw_version([8]):
		my_id_modules.extend(['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff',
			'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring16_GeneralPurpose_V1_cff'])
	else:
		my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Spring15_25ns_V1_cff',
			'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring15_25ns_nonTrig_V1_cff']

	for idmod in my_id_modules:
		setupAllVIDIdsInModule(process, idmod, setupVIDElectronSelection)
	process.elPFIsoDepositCharged.src = cms.InputTag(electrons)
	process.elPFIsoDepositChargedAll.src = cms.InputTag(electrons)
	process.elPFIsoDepositNeutral.src = cms.InputTag(electrons)
	process.elPFIsoDepositGamma.src = cms.InputTag(electrons)
	process.elPFIsoDepositPU.src = cms.InputTag(electrons)

## for electron iso
from CommonTools.ParticleFlow.Isolation.pfElectronIsolation_cff import *
elPFIsoValueCharged03PFIdPFIso = elPFIsoValueCharged03PFId.clone()
elPFIsoValueChargedAll03PFIdPFIso = elPFIsoValueChargedAll03PFId.clone()
elPFIsoValueGamma03PFIdPFIso = elPFIsoValueGamma03PFId.clone()
elPFIsoValueNeutral03PFIdPFIso = elPFIsoValueNeutral03PFId.clone()
elPFIsoValuePU03PFIdPFIso = elPFIsoValuePU03PFId.clone()

elPFIsoValueGamma03PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.08)','EcalBarrel:ConeVeto(0.08)'))
elPFIsoValueNeutral03PFIdPFIso.deposits[0].vetos = (cms.vstring())
elPFIsoValuePU03PFIdPFIso.deposits[0].vetos = (cms.vstring())
elPFIsoValueCharged03PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.015)'))
elPFIsoValueChargedAll03PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.015)','EcalBarrel:ConeVeto(0.01)'))

electronPFIsolationValuesSequence = cms.Sequence(
	elPFIsoValueCharged03PFIdPFIso+
	elPFIsoValueChargedAll03PFIdPFIso+
	elPFIsoValueGamma03PFIdPFIso+
	elPFIsoValueNeutral03PFIdPFIso+
	elPFIsoValuePU03PFIdPFIso
)
elPFIsoDepositGamma.ExtractorPSet.ComponentName = cms.string("CandViewExtractor")

# electron/muon PF iso sequence
pfElectronIso = cms.Sequence(
	electronPFIsolationDepositsSequence +
	electronPFIsolationValuesSequence
)

makeKappaElectrons = cms.Sequence(
	egmGsfElectronIDSequence
	#pfElectronIso
	)
