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


// This producer is responsible for the common task of writing a vector of objects
// into the destination vector Tout::type, which has a p4 property
// The filling is implemented via:
//  * virtual void fillSingle(const SingleInputType &in, SingleOutputType &out);
template<typename Tin, typename Tout>
class KCommonLVProducer
{
public:
	KCommonLVProducer(const edm::ParameterSet &cfg, const int verbose) : verbosity(verbose),
		maxN(cfg.getParameter<int>("maxN")),
		minPt(cfg.getParameter<double>("minPt")),
		maxEta(cfg.getParameter<double>("maxEta")) {}

	virtual void clearProduct(typename KRegexMultiProducer<Tin, Tout>::OutputType &out) { out.clear(); }

	virtual void fillProduct(const Tin &in, typename Tout::type &out,
		const std::string &name)
	{
		if (verbosity > 0)
			std::cout << in.size() << " objects in collection " << name << std::endl;
		out.reserve(in.size());

		// Cursor is necessary to get "Refs" later
		nCursor = 0;
		for (typename Tin::const_iterator lvit = in.begin(); lvit < in.end(); ++lvit)
			if (lvit->pt() >= minPt && abs(lvit->eta()) <= maxEta)
			{
				out.push_back(SingleOutputType());
				fillSingle(*lvit, out.back());
				nCursor++;
			}
		std::sort(out.begin(), out.end(), lorentzsorter_pt);
		if (maxN > 0)
			out.erase(out.begin() + std::min(out.size(), (size_t)maxN), out.end());

		if (verbosity > 1)
		{
			std::cout << "\t" << "Number of accepted objects: " << out.size() << "\t";
			if (out.size() > 0)
				std::cout << "First: " << out[0].p4 << "\tLast: " << out[out.size() - 1].p4 << std::endl;
		}
	}

protected:
	const int verbosity;
	int maxN, nCursor;
	double minPt;
	double maxEta;

	typedef typename Tin::value_type SingleInputType;
	typedef typename Tout::type::value_type SingleOutputType;
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out) = 0;

private:
	KLVSorter<SingleOutputType> lorentzsorter_pt;
};


// This is the pset variant of the LV producer
template<typename Tin, typename Tout>
class KManualMultiLVProducer : public KManualMultiProducer<Tin, Tout>, public KCommonLVProducer<Tin, Tout>
{
public:
	KManualMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KManualMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		KCommonLVProducer<Tin, Tout>(cfg, KBaseProducer::verbosity) {}
	virtual ~KManualMultiLVProducer() {};

	virtual void clearProduct(typename KRegexMultiProducer<Tin, Tout>::OutputType &out) { out.clear(); }
	virtual void fillProduct(
		const typename KRegexMultiProducer<Tin, Tout>::InputType &in,
		typename KRegexMultiProducer<Tin, Tout>::OutputType &out,
		const std::string &name, const edm::ParameterSet &pset)
	{
		KCommonLVProducer<Tin, Tout>::fillProduct(in, out, name);
	}
};


// This is the regex variant of the LV producer
template<typename Tin, typename Tout>
class KRegexMultiLVProducer : public KRegexMultiProducer<Tin, Tout>, public KCommonLVProducer<Tin, Tout>
{
public:
	KRegexMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KRegexMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		KCommonLVProducer<Tin, Tout>(cfg, KBaseProducer::verbosity) {}
	virtual ~KRegexMultiLVProducer() {};

	virtual void clearProduct(typename KRegexMultiProducer<Tin, Tout>::OutputType &out) { out.clear(); }
	virtual void fillProduct(
		const typename KRegexMultiProducer<Tin, Tout>::InputType &in,
		typename KRegexMultiProducer<Tin, Tout>::OutputType &out, edm::InputTag *tag)
	{
		const std::string name = this->nameMap[tag].first + " (" + this->nameMap[tag].second + ")";
		KCommonLVProducer<Tin, Tout>::fillProduct(in, out, name);
	}
};

#endif
