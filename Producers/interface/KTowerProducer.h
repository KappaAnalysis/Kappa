#ifndef KAPPA_TOWERPRODUCER_H
#define KAPPA_TOWERPRODUCER_H

#include "KBaseMultiProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/VertexReco/interface/Vertex.h>
#include <DataFormats/VertexReco/interface/VertexFwd.h>

struct KTowerProducer_Product
{
	typedef std::vector<KDataLV> type;
	static const std::string id() { return "std::vector<KDataLV>"; };
	static const std::string producer() { return "KTowerProducer"; };
};

class KTowerProducer : public KRegexMultiProducer<CaloTowerCollection, KTowerProducer_Product>
{
public:
	KTowerProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KRegexMultiProducer<CaloTowerCollection, KTowerProducer_Product>(cfg, _event_tree, _run_tree),
		srcPVs(cfg.getParameter<edm::InputTag>("srcPVs")),
		nMaxJets(cfg.getParameter<int>("maxN")),
		minPt(cfg.getParameter<double>("minPt")) {}
	virtual ~KTowerProducer() {};

protected:
	edm::InputTag srcPVs;
	int nMaxJets;
	double minPt;

	virtual void clearProduct(OutputType &output) { output.clear(); }
	virtual void fillProduct(const InputType &input, OutputType &output, edm::InputTag *tag)
	{
		if (verbosity > 0)
			std::cout << input.size() << " objects in collection "
				<< nameMap[tag].first << " (" << nameMap[tag].second << ")" << std::endl;
		output.reserve(input.size());

		// Get information for vertex correction
		reco::Jet::Point vertex;
		edm::Handle<reco::VertexCollection> pvCollection;
		cEvent->getByLabel(srcPVs, pvCollection);
		if (pvCollection->size() > 0)
			vertex = pvCollection->begin()->position();
		else
			vertex = reco::Jet::Point(0, 0, 0);

		for (InputType::const_iterator lvit = input.begin(); lvit < input.end(); ++lvit)
			if (lvit->pt() >= minPt)
			{
				output.push_back(OutputType::value_type());
				math::PtEtaPhiMLorentzVector ct(lvit->p4(vertex));
				copyP4(ct, output.back().p4);
			}
		std::sort(output.begin(), output.end(), towersorter_pt);
		if (nMaxJets > 0)
			output.erase(output.begin() + std::min(output.size(), (size_t)nMaxJets), output.end());

		if (verbosity > 1)
		{
			std::cout << "\t" << "Number of accepted objects: " << output.size() << "\t";
			if (output.size() > 0)
				std::cout
					<< "First: " << output[0].p4 << "\t"
					<< "Last: " << output[output.size() - 1].p4;
				std::cout << std::endl;
		}
	}

private:
	struct KTowerSorter_PT
	{
		bool operator() (const KDataLV &a, const KDataLV &b) { return (a.p4.pt() > b.p4.pt()); };
	} towersorter_pt;
};

#endif
