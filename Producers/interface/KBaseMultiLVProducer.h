#ifndef KAPPA_MULTILVPRODUCER_H
#define KAPPA_MULTILVPRODUCER_H

#include "KBaseMultiProducer.h"

template<typename T>
struct KLVSorter
{
	bool operator() (const T &a, const T &b) { return (a.p4.pt() > b.p4.pt()); };
};


// This producer is responsible for the common task of writing a vector of objects
// into the destination vector Tout::type
// The filling is implemented via:
//  * virtual bool acceptSingle(const SingleInputType &in);
//  * virtual void fillSingle(const SingleInputType &in, SingleOutputType &out);
//  * virtual void sort(typename Tout::type &out);
template<typename Tin, typename Tout>
class KCommonVectorProducer
{
public:
	KCommonVectorProducer(const edm::ParameterSet &cfg) :
		maxN(cfg.getParameter<int>("maxN")) {}

	virtual void fillProduct(const Tin &in, typename Tout::type &out,
		const std::string &name)
	{
		if (KBaseProducer::verbosity > 0)
			std::cout << in.size() << " objects in collection " << name << std::endl;
		out.reserve(in.size());

		// Cursor is necessary to get "Refs" later
		typename Tin::const_iterator lvit;
		for (lvit = in.begin(), nCursor = 0; lvit < in.end(); ++lvit, ++nCursor)
			if (acceptSingle(*lvit))
			{
				out.push_back(SingleOutputType());
				fillSingle(*lvit, out.back());
			}
		if (maxN > 0)
			out.erase(out.begin() + std::min(out.size(), (size_t)maxN), out.end());

		if (KBaseProducer::verbosity > 1)
			std::cout << "\t" << "Number of accepted objects: " << out.size() << "\t";
	}

	virtual void sort(typename Tout::type &out) {}

protected:
	int maxN, nCursor;

	typedef typename Tin::value_type SingleInputType;
	typedef typename Tout::type::value_type SingleOutputType;

	virtual bool acceptSingle(const SingleInputType &in) { return true; }
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out) = 0;
};


// This producer is responsible for the common task of writing a vector of objects
// into the destination vector Tout::type, which has a p4 property
// The filling is implemented via:
//  * virtual void fillSingle(const SingleInputType &in, SingleOutputType &out);
template<typename Tin, typename Tout>
class KCommonLVProducer : public KCommonVectorProducer<Tin, Tout>
{
public:
	KCommonLVProducer(const edm::ParameterSet &cfg) :
		KCommonVectorProducer<Tin, Tout>(cfg),
		minPt(cfg.getParameter<double>("minPt")),
		maxEta(cfg.getParameter<double>("maxEta")) {}

	virtual bool acceptSingle(const typename Tin::value_type &in)
	{
		return (in.pt() >= minPt && ((maxEta < 0) || (std::abs(in.eta()) <= maxEta)));
	}

	virtual void sort(typename Tout::type &out)
	{
		std::sort(out.begin(), out.end(), sorter);
	}

	virtual void fillProduct(const Tin &in, typename Tout::type &out,
		const std::string &name)
	{
		KCommonVectorProducer<Tin, Tout>::fillProduct(in, out, name);
		if ((KBaseProducer::verbosity > 1) && (out.size() > 0))
			std::cout << "First: " << out[0].p4 << "\tLast: " << out[out.size() - 1].p4 << std::endl;
	}

protected:
	double minPt;
	double maxEta;

private:
	KLVSorter<typename Tout::type::value_type> sorter;
};


// This is the pset variant of the LV producer
template<typename Tin, typename Tout>
class KManualMultiLVProducer :
	public KManualMultiProducer<Tin, Tout>,
	public KCommonLVProducer<Tin, Tout>
{
public:
	KManualMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KManualMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		KCommonLVProducer<Tin, Tout>(cfg) {}
	virtual ~KManualMultiLVProducer() {};

	virtual void clearProduct(typename KBaseMultiProducer<Tin, Tout>::OutputType &out) { out.clear(); }
	virtual void fillProduct(
		const typename KBaseMultiProducer<Tin, Tout>::InputType &in,
		typename KBaseMultiProducer<Tin, Tout>::OutputType &out,
		const std::string &name, const edm::ParameterSet &pset)
	{
		KCommonLVProducer<Tin, Tout>::fillProduct(in, out, name);
	}
};


// This is the regex variant of the LV producer
template<typename Tin, typename Tout>
class KRegexMultiLVProducer :
	public KRegexMultiProducer<Tin, Tout>,
	public KCommonLVProducer<Tin, Tout>
{
public:
	KRegexMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KRegexMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		KCommonLVProducer<Tin, Tout>(cfg) {}
	virtual ~KRegexMultiLVProducer() {};

	virtual void clearProduct(typename KBaseMultiProducer<Tin, Tout>::OutputType &out) { out.clear(); }
	virtual void fillProduct(
		const typename KBaseMultiProducer<Tin, Tout>::InputType &in,
		typename KBaseMultiProducer<Tin, Tout>::OutputType &out,
		const std::string &name, const edm::InputTag *tag)
	{
		KCommonLVProducer<Tin, Tout>::fillProduct(in, out, name);
	}
};

#endif
