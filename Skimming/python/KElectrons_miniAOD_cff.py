
import FWCore.ParameterSet.Config as cms

from PhysicsTools.SelectorUtils.tools.vid_id_tools import *



from RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cfi import *
egmGsfElectronIDs.physicsObjectSrc = cms.InputTag('slimmedElectrons')

from PhysicsTools.SelectorUtils.centralIDRegistry import central_id_registry
egmGsfElectronIDSequence = cms.Sequence(egmGsfElectronIDs)

def setupElectrons(process):
	my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_PHYS14_PU20bx25_V1_miniAOD_cff']
	for idmod in my_id_modules:
		setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)

makeKappaElectrons = cms.Sequence(
	egmGsfElectronIDSequence
	)
