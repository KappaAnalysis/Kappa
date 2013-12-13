/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_PRODUCER_H
#define KAPPA_PRODUCER_H

#include <TTree.h>
#include <FWCore/Framework/interface/Event.h>
#include <FWCore/Framework/interface/LuminosityBlock.h>
#include <FWCore/Framework/interface/Run.h>
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include "../../DataFormats/interface/KMetadata.h"

// KBaseProducer is the base class for all producers
//  - provides common matching tools
class KBaseProducer
{
public:
	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup);
	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup);
	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup);
	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup);
	virtual ~KBaseProducer() {};

protected:
	bool tagMatch(const edm::Provenance *prov, const std::vector<edm::InputTag> &tags);
	bool regexMatch(const std::string &in, const std::string &filter);
	bool regexMatch(const std::string &in,
		const std::vector<std::string> &whitelist, const std::vector<std::string> &blacklist);
	std::string regexRename(std::string in, const std::vector<std::string> &patterns);
	bool fail(const std::ostream &s);

public:
	static int verbosity;
};

// Producer with provenance
//  - producer can rename collections => save mapping between new and old name
class KBaseProducerWP : public KBaseProducer
{
public:
	virtual ~KBaseProducerWP() {};
	KBaseProducerWP(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, const std::string &producerName);
	void addProvenance(std::string oldName, std::string newName);

protected:
	const edm::ParameterSet psBase;
	KProvenance *provenance;
};

template<typename T1, typename T2>
inline void copyP4(const T1 &in, T2 &out)
{
	out.SetCoordinates(in.pt(), in.eta(), in.phi(), in.mass());
}

#endif
