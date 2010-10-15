#ifndef KAPPA_CALOJETPRODUCER_H
#define KAPPA_CALOJETPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/METReco/interface/HcalNoiseRBX.h>
#include <DataFormats/JetReco/interface/JetID.h>

struct KCaloJetProducer_Product
{
	typedef std::vector<KDataJet> type;
	static const std::string id() { return "std::vector<KDataJet>"; };
	static const std::string producer() { return "KCaloJetProducer"; };
};

class KCaloJetProducer : public KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>
{
public:
	KCaloJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>(cfg, _event_tree, _run_tree),
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
		return KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>::onEvent(event, setup);
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		tagJetID = pset.getParameter<edm::InputTag>("srcJetID");
		if (tagJetID.label() != "")
			cEvent->getByLabel(tagJetID, hJetID);

		// Continue normally
		KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.area = in.jetArea();
		out.fEM = in.emEnergyFraction();
		out.nConst = in.getJetConstituents().size();
		out.n90 = in.n90();

		// Jet ID variables
		out.n90Hits = -2;
		out.fHPD = -2;
		out.fRBX = -2;
		out.fHO = -2;
		if (tagJetID.label() != "")
		{
			edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::CaloJetCollection>(handle, this->nCursor));
			const reco::JetID &jetID = (*hJetID)[jetRef];
			out.n90Hits = (int)(jetID.n90Hits);
			// energy fraction from dominant hybrid photo diode
			out.fHPD = jetID.fHPD;
			// energy fraction from dominant readout box
			out.fRBX = jetID.fRBX;
			// energy fraction in HO
			out.fHO = jetID.fHO;
		}

		// Get noise of constituents
		out.noiseHCAL = -2;
		double noiseSum = 0;
		std::vector<CaloTowerPtr> towers = in.getCaloConstituents();
		for (unsigned int tID = 0; tID < towers.size(); tID++)
			if (hcalNoise.find(towers[tID]->id()) != hcalNoise.end())
				noiseSum += hcalNoise[towers[tID]->id()];
		if (std::abs(noiseSum) > 1e-5)
			out.noiseHCAL = noiseSum;
	}

private:
	edm::InputTag tagNoiseHCAL, tagJetID;

	edm::Handle<reco::HcalNoiseRBXCollection> noiseHCALcoll;
	edm::Handle<edm::ValueMap<reco::JetID> > hJetID;

	std::map<CaloTowerDetId, double> hcalNoise;
};

#endif
