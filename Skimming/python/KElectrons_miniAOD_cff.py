
import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools

from PhysicsTools.SelectorUtils.tools.vid_id_tools import *



from RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cfi import *
egmGsfElectronIDs.physicsObjectSrc = cms.InputTag('slimmedElectrons')

from PhysicsTools.SelectorUtils.centralIDRegistry import central_id_registry
egmGsfElectronIDSequence = cms.Sequence(egmGsfElectronIDs)

cmssw_version_number = tools.get_cmssw_version_number()

def setupElectrons(process):
	if (cmssw_version_number.startswith("7_4")):
		my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_PHYS14_PU20bx25_V2_cff']
	else:
		my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_PHYS14_PU20bx25_V1_miniAOD_cff']
	for idmod in my_id_modules:
		setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)

makeKappaElectrons = cms.Sequence(
	egmGsfElectronIDSequence
	)
