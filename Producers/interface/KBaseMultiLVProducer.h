#ifndef KAPPA_MULTILVPRODUCER_H
#define KAPPA_MULTILVPRODUCER_H

#include "KBaseMultiProducer.h"

template<typename T>
struct KLVSorter
{
	bool operator()(const T &a, const T &b) { return (a.p4.pt() > b.p4.pt()); };
};


// This producer is responsible for writing a vector of objects into the destination vector Tout::type
// The filling is implemented via:
//  * virtual bool acceptSingle(const SingleInputType &in);
//  * virtual void fillSingle(const SingleInputType &in, SingleOutputType &out);
//  * virtual void sort(typename Tout::type &out);
template<typename Tin, typename Tout>
class KBaseMultiVectorProducer : public KBaseMultiProducer<Tin, Tout>
{
public:
	KBaseMultiVectorProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		maxN(cfg.getParameter<int>("maxN")) {}

	virtual void fillProduct(const typename KBaseMultiProducer<Tin, Tout>::InputType &input,
		typename KBaseMultiProducer<Tin, Tout>::OutputType &output,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (KBaseProducer::verbosity > 0)
			std::cout << input.size() << " objects in collection " << name << std::endl;
		output.reserve(input.size());

		// Cursor is necessary to get "Refs" later
		typename Tin::const_iterator lvit;
		for (lvit = input.begin(), nCursor = 0; lvit < input.end(); ++lvit, ++nCursor)
			if (acceptSingle(*lvit))
			{
				output.push_back(SingleOutputType());
				fillSingle(*lvit, output.back());
			}
		if (maxN > 0)
			output.erase(output.begin() + std::min(output.size(), (size_t)maxN), output.end());

		if (KBaseProducer::verbosity > 1)
			std::cout << "\t" << "Number of accepted objects: " << output.size() << "\t";
	}

	virtual void clearProduct(typename KBaseMultiProducer<Tin, Tout>::OutputType &output) { output.clear(); }
	virtual void sort(typename KBaseMultiProducer<Tin, Tout>::OutputType &out) {}

protected:
	int maxN, nCursor;

	typedef typename KBaseMultiProducer<Tin, Tout>::InputType::value_type SingleInputType;
	typedef typename KBaseMultiProducer<Tin, Tout>::OutputType::value_type SingleOutputType;

	virtual bool acceptSingle(const SingleInputType &in) { return true; }
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out) = 0;
};


// This producer is responsible for the common task of writing a vector of objects
// into the destination vector Tout::type, which has a p4 property
// The filling is implemented via:
//  * virtual void fillSingle(const SingleInputType &in, SingleOutputType &out);
template<typename Tin, typename Tout>
class KBaseMultiLVProducer : public KBaseMultiVectorProducer<Tin, Tout>
{
public:
	KBaseMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiVectorProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		minPt(cfg.getParameter<double>("minPt")),
		maxEta(cfg.getParameter<double>("maxEta")) {}

	virtual bool acceptSingle(const typename KBaseMultiVectorProducer<Tin, Tout>::SingleInputType &in)
	{
		return ((in.pt() >= minPt) && ((maxEta < 0) || (std::abs(in.eta()) <= maxEta)));
	}

	virtual void sort(typename KBaseMultiVectorProducer<Tin, Tout>::OutputType &out)
	{
		std::sort(out.begin(), out.end(), sorter);
	}

	virtual void fillProduct(const typename KBaseMultiVectorProducer<Tin, Tout>::InputType &input,
		typename KBaseMultiVectorProducer<Tin, Tout>::OutputType &output,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		KBaseMultiVectorProducer<Tin, Tout>::fillProduct(input, output, name, tag, pset);
		if ((KBaseProducer::verbosity > 1) && (output.size() > 0))
			std::cout << "First: " << output[0].p4 << "\tLast: " << output[output.size() - 1].p4 << std::endl;
	}

protected:
	double minPt;
	double maxEta;

private:
	KLVSorter<typename KBaseMultiVectorProducer<Tin, Tout>::SingleOutputType> sorter;
};


// This is the pset variant of the LV producer
template<typename Tin, typename Tout>
class KManualMultiLVProducer : public KBaseMultiLVProducer<Tin, Tout>
{
public:
	KManualMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<Tin, Tout>(cfg, _event_tree, _run_tree) {}
	virtual ~KManualMultiLVProducer() {};
};


// This is the regex variant of the LV producer
template<typename Tin, typename Tout>
class KRegexMultiLVProducer : public KBaseMultiLVProducer<Tin, Tout>
{
public:
	KRegexMultiLVProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<Tin, Tout>(cfg, _event_tree, _run_tree) {}
	virtual ~KRegexMultiLVProducer() {};
};

#endif
