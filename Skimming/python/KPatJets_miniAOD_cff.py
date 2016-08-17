import FWCore.ParameterSet.Config as cms

def setup_PatJets(process):
	##Sequence to write out tagged PatJets from JetToolbox modules for each Algorithm 
	makePatJets = {}
	for param in (4, 8):
		for algo in ["", "CHS", "Puppi"]:
			variant_name = "AK%dPF%s" % (param, algo)
			makePatJets[variant_name] = cms.Sequence( 
						getattr(process, "pfImpactParameterTagInfos"+variant_name)*
						getattr(process, "pfTrackCountingHighEffBJetTags"+variant_name)*
						getattr(process, "pfSecondaryVertexTagInfos"+variant_name)*
						getattr(process, "pfCombinedSecondaryVertexV2BJetTags"+variant_name)*
						getattr(process, "softPFElectronsTagInfos"+variant_name)*
						getattr(process, "softPFMuonsTagInfos"+variant_name)*
						getattr(process, "pfInclusiveSecondaryVertexFinderTagInfos"+variant_name)*
						getattr(process, "pfCombinedMVAV2BJetTags"+variant_name)*
						getattr(process, "pfCombinedInclusiveSecondaryVertexV2BJetTags"+variant_name)*
   						getattr(process, "pfSimpleSecondaryVertexHighPurBJetTags"+variant_name)*
						getattr(process, "pfSimpleSecondaryVertexHighEffBJetTags"+variant_name)*
						getattr(process, "pfJetBProbabilityBJetTags"+variant_name)*
						getattr(process, "pfJetProbabilityBJetTags"+variant_name)*
						getattr(process, "pfTrackCountingHighPurBJetTags"+variant_name)*
						getattr(process, "patJets"+variant_name)*
						getattr(process, "selectedPatJets"+variant_name))
	return(makePatJets)




