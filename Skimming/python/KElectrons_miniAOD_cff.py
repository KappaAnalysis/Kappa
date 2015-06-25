
import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools

cmssw_version_number = tools.get_cmssw_version_number()

from PhysicsTools.SelectorUtils.tools.vid_id_tools import *


if (cmssw_version_number.startswith("7_4")):
	# https://github.com/ikrav/EgammaWork/blob/v1/ElectronNtupler/test/runElectrons_VID_MVA_PHYS14_demo.py
	from PhysicsTools.SelectorUtils.tools.vid_id_tools import switchOnVIDElectronIdProducer, DataFormat
	from RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cff import *

else:
	# https://github.com/ikrav/ElectronWork/blob/master/ElectronNtupler/test/runIdDemoPrePHYS14AOD.py#L29-L56
	from PhysicsTools.SelectorUtils.centralIDRegistry import central_id_registry
	from RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cfi import *
	egmGsfElectronIDSequence = cms.Sequence(egmGsfElectronIDs)

egmGsfElectronIDs.physicsObjectSrc = cms.InputTag('slimmedElectrons')

def setupElectrons(process):
	if (cmssw_version_number.startswith("7_4")):
		switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)
		my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_PHYS14_PU20bx25_V2_cff',
				 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_PHYS14_PU20bx25_nonTrig_V1_cff']
	else:
		my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_PHYS14_PU20bx25_V1_miniAOD_cff']
	for idmod in my_id_modules:
		setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)

makeKappaElectrons = cms.Sequence(
	egmGsfElectronIDSequence
	)
