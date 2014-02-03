import FWCore.ParameterSet.Config as cms

# https://github.com/violatingcp/Jets_Short/blob/master/RecoJets/JetAnalyzers/test/JetMetPlotsExample.py#L220

#Pileup Reduced MET
#Load the conditions (needed for the JEC applied inside the MVA Met)
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
from JetMETCorrections.Configuration.JetCorrectionProducers_cff import *

#Load the MVA Met
from RecoMET.METPUSubtraction.mvaPFMET_leptons_cff import *
from RecoMET.METPUSubtraction.noPileUpPFMET_cff import *

#Specify the leptons
#pfMEtMVA.srcLeptons = cms.VInputTag("isomuons")#,"isoelectrons","isotaus")

#Type1 Corrections
from JetMETCorrections.Type1MET.correctionTermsPfMetType1Type2_cff import *
from JetMETCorrections.Type1MET.correctedMet_cff import *
JetCorrection = "ak5PFL1FastL2L3" # NOTE: use "ak5PFL1FastL2L3" for MC / "ak5PFL1FastL2L3Residual" for Data. See comment in mvaPFMET_cff.py
corrPfMetType1.jetCorrLabel = cms.string(JetCorrection)
