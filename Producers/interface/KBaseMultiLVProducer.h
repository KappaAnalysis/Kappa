#ifndef KAPPA_MULTILVPRODUCER_H
#define KAPPA_MULTILVPRODUCER_H

#include "KBaseMultiProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KMetadata.h"

template<typename T>
struct KLVSorter
{
	bool operator() (const T &a, const T &b) { return (a.p4.pt() > b.p4.pt()); };
};

// Only use this producer with Tout = std::vector<T>
template<typename Tin, typename Tout>
class KManualMultiLVProducer : public KManualMultiProducer<Tin, Tout>
{
public:
	KManualMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KManualMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		nMaxJets(cfg.getParameter<int>("maxN")),
		minPt(cfg.getParameter<double>("minPt")),
		maxEta(cfg.getParameter<double>("maxEta")) {}
	virtual ~KManualMultiLVProducer() {};

	virtual void clearProduct(typename KBaseMultiProducer<Tin, Tout>::OutputType &output) { output.clear(); }
	virtual void onProdCommon(const edm::ParameterSet &pset) {}

	virtual void fillProduct(
		const typename KBaseMultiProducer<Tin, Tout>::InputType &input,
		typename KBaseMultiProducer<Tin, Tout>::OutputType &output,
		const std::string &name, const edm::ParameterSet &pset)
	{
		if (this->verbosity > 0)
			std::cout << input.size() << " objects in collection " << name << std::endl;
		output.reserve(input.size());

		onProdCommon(pset);
		for (typename KBaseMultiProducer<Tin, Tout>::InputType::const_iterator lvit = input.begin(); lvit < input.end(); ++lvit)
			if (lvit->pt() >= minPt && abs(lvit->eta()) <= maxEta)
			{
				output.push_back(typename KBaseMultiProducer<Tin, Tout>::OutputType::value_type());
				fillSingle(*lvit, output.back());
			}
		std::sort(output.begin(), output.end(), lorentzsorter_pt);
		if (nMaxJets > 0)
			output.erase(output.begin() + std::min(output.size(), (size_t)nMaxJets), output.end());

		if (this->verbosity > 1)
		{
			std::cout << "\t" << "Number of accepted objects: " << output.size() << "\t";
			if (output.size() > 0)
				std::cout
					<< "First: " << output[0].p4 << "\t"
					<< "Last: " << output[output.size() - 1].p4;
				std::cout << std::endl;
		}
	}

protected:
	int nMaxJets;
	double minPt;
	double maxEta;

	typedef typename KBaseMultiProducer<Tin, Tout>::InputType::value_type SingleInputType;
	typedef typename KBaseMultiProducer<Tin, Tout>::OutputType::value_type SingleOutputType;

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out) = 0;

private:
	KLVSorter<SingleOutputType> lorentzsorter_pt;
};

// Only use this producer with Tout = std::vector<T>
template<typename Tin, typename Tout>
class KBaseMultiLVProducer : public KBaseMultiProducer<Tin, Tout>
{
public:
	KBaseMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		nMaxJets(cfg.getParameter<int>("maxN")),
		minPt(cfg.getParameter<double>("minPt")),
		maxEta(cfg.getParameter<double>("maxEta")) {}
	virtual ~KBaseMultiLVProducer() {};

	virtual void clearProduct(typename KBaseMultiProducer<Tin, Tout>::OutputType &output) { output.clear(); }

	virtual void fillProduct(
		const typename KBaseMultiProducer<Tin, Tout>::InputType &input,
		typename KBaseMultiProducer<Tin, Tout>::OutputType &output, edm::InputTag *tag)
	{
		if (this->verbosity > 0)
			std::cout << input.size() << " objects in collection "
				<< this->nameMap[tag].first << " (" << this->nameMap[tag].second << ")" << std::endl;
		output.reserve(input.size());

		for (typename KBaseMultiProducer<Tin, Tout>::InputType::const_iterator lvit = input.begin(); lvit < input.end(); ++lvit)
			if (lvit->pt() >= minPt && abs(lvit->eta()) <= maxEta)
			{
				output.push_back(typename KBaseMultiProducer<Tin, Tout>::OutputType::value_type());
				fillSingle(*lvit, output.back());
			}
		std::sort(output.begin(), output.end(), lorentzsorter_pt);
		if (nMaxJets > 0)
			output.erase(output.begin() + std::min(output.size(), (size_t)nMaxJets), output.end());

		if (this->verbosity > 1)
		{
			std::cout << "\t" << "Number of accepted objects: " << output.size() << "\t";
			if (output.size() > 0)
				std::cout
					<< "First: " << output[0].p4 << "\t"
					<< "Last: " << output[output.size() - 1].p4;
				std::cout << std::endl;
		}
	}

protected:
	int nMaxJets;
	double minPt;
	double maxEta;

	typedef typename KBaseMultiProducer<Tin, Tout>::InputType::value_type SingleInputType;
	typedef typename KBaseMultiProducer<Tin, Tout>::OutputType::value_type SingleOutputType;

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out) = 0;

private:
	KLVSorter<SingleOutputType> lorentzsorter_pt;
};

#endif
