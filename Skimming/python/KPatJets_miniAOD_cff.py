import FWCore.ParameterSet.Config as cms

def setup_PatJets(process, data):
	##Sequence to write out tagged PatJets from JetToolbox modules for each Algorithm 
	makePatJets = {}
	makePatJetsData = {}
	makePatJetsMC = {}
	for param in (4, 8):
		for algo in ["", "CHS", "Puppi"]:
			variant_name = "AK%dPF%s" % (param, algo)
			makePatJetsData[variant_name] = cms.Sequence( 
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
						getattr(process, "pfTrackCountingHighPurBJetTags"+variant_name)
						)						
			if not data:
				makePatJetsMC[variant_name] = cms.Sequence(
						getattr(process, "patJetPartons")*
						getattr(process, "patJetFlavourAssociation"+variant_name)*
						getattr(process, "patJetPartonMatch"+variant_name)*
						getattr(process, "patJetGenJetMatch"+variant_name)								
						)
				makePatJets[variant_name] = cms.Sequence(
						makePatJetsData[variant_name]*
						makePatJetsMC[variant_name]*
						getattr(process, "patJets"+variant_name)*
						getattr(process, "selectedPatJets"+variant_name)
						)
			else:
				makePatJets[variant_name] = cms.Sequence(
						makePatJetsData[variant_name]*
						getattr(process, "patJets"+variant_name)*
						getattr(process, "selectedPatJets"+variant_name)
						)

	return(makePatJets)




