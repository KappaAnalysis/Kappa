#ifndef KAPPA_CALOJETPRODUCER_H
#define KAPPA_CALOJETPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/METReco/interface/HcalNoiseRBX.h>
#include <DataFormats/JetReco/interface/JetExtendedAssociation.h>
#include <DataFormats/JetReco/interface/JetID.h>

struct KCaloJetProducer_Product
{
	typedef std::vector<KDataJet> type;
	static const std::string id() { return "std::vector<KDataJet>"; };
	static const std::string producer() { return "KCaloJetProducer"; };
};

class KCaloJetProducer : public KManualMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>
{
public:
	KCaloJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KManualMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>(cfg, _event_tree, _run_tree),
		tagNoiseHCAL(cfg.getParameter<edm::InputTag>("srcNoiseHCAL")) {}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		// Read HCAL noise tower map - done once per event
		if (tagNoiseHCAL.label() != "")
		{
			hcalNoise.clear();
			event.getByLabel(tagNoiseHCAL, noiseHCALcoll);
			// Iterate over readout boxes
			for (reco::HcalNoiseRBXCollection::const_iterator rit = noiseHCALcoll->begin(); rit != noiseHCALcoll->end(); ++rit)
			{
				// Iterate over the hybrid photo diodes
				const std::vector<reco::HcalNoiseHPD> vHPD = rit->HPDs();
				for (std::vector<reco::HcalNoiseHPD>::const_iterator itHPD = vHPD.begin(); itHPD != vHPD.end(); ++itHPD)
				{
					// Iterator over the calo towers
					const edm::RefVector<CaloTowerCollection> noiseTowers = itHPD->caloTowers();
					for (edm::RefVector<CaloTowerCollection>::const_iterator itTower = noiseTowers.begin(); itTower != noiseTowers.end(); ++itTower)
					{
						const edm::Ref<CaloTowerCollection> tower = *itTower;
						hcalNoise.insert(std::pair<CaloTowerDetId, double>(tower->id(), tower->hadEnergy()));
					}
				}
			}
		}

		// Continue normally
		return KManualMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>::onEvent(event, setup);
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		tagExtender = pset.getParameter<edm::InputTag>("srcExtender");
		if (tagExtender.label() != "")
			cEvent->getByLabel(tagExtender, hJetExtender);

		tagJetID = pset.getParameter<edm::InputTag>("srcJetID");
		if (tagJetID.label() != "")
			cEvent->getByLabel(tagJetID, hJetID);

		// Continue normally
		KManualMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.area = in.jetArea();
		out.detectorEta = in.detectorP4().eta();
		out.emf = in.emEnergyFraction();
		out.nConst = in.getJetConstituents().size();
		out.n90 = in.n90();

		// Jet ID variables
		out.n90Hits = -1;
		out.fHPD = -1;
		out.fRBX = -1;
		if (tagJetID.label() != "")
		{
			edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::CaloJetCollection>(handle, this->nCursor));
			const reco::JetID &jetID = (*hJetID)[jetRef];
			out.n90Hits = (int)(jetID.n90Hits);
			// energy fraction from dominant hybrid photo diode
			out.fHPD = jetID.fHPD;
			// energy fraction from dominant readout box
			out.fRBX = jetID.fRBX;
		}

		// Jet extender variables
		out.nTracksAtCalo = -1;
		out.nTracksAtVertex = -1;
		if (tagExtender.label() != "")
		{
			out.nTracksAtCalo = reco::JetExtendedAssociation::tracksAtCaloNumber(*hJetExtender, in);
			out.nTracksAtVertex = reco::JetExtendedAssociation::tracksAtVertexNumber(*hJetExtender, in);
		}

		// Get noise of constituents
		out.noiseHCAL = 0;
		std::vector<CaloTowerPtr> towers = in.getCaloConstituents();
		for (unsigned int tID = 0; tID < towers.size(); tID++)
			if (hcalNoise.find(towers[tID]->id()) != hcalNoise.end())
				out.noiseHCAL += hcalNoise[towers[tID]->id()];
	}

private:
	edm::InputTag tagNoiseHCAL, tagJetID, tagExtender;

	edm::Handle<reco::HcalNoiseRBXCollection> noiseHCALcoll;
	edm::Handle<reco::JetExtendedAssociation::Container> hJetExtender;
	edm::Handle<edm::ValueMap<reco::JetID> > hJetID;

	std::map<CaloTowerDetId, double> hcalNoise;
};

#endif
