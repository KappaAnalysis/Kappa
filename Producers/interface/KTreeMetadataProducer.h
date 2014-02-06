/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 *   Raphael Friese <raphael.friese@cern.ch>
 */

#ifndef KAPPA_TREE_METADATAPRODUCER_H
#define KAPPA_TREE_METADATAPRODUCER_H

#include <bitset>
#include <TMath.h>

#include "../../DataFormats/interface/KTreeMetadata.h"

class KTreeMetadataProducer: public KBaseProducer
{
public:
	KTreeMetadataProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree)
	{
	//read parameters from config

	KTreeMetadataObject.dataset				= cfg.getParameter<std::string>("dataset");
	KTreeMetadataObject.generator				= cfg.getParameter<std::string>("generator");
	KTreeMetadataObject.tune					= cfg.getParameter<std::string>("tune");
	KTreeMetadataObject.productionProcess	= cfg.getParameter<std::string>("productionProcess");
	KTreeMetadataObject.globalTag				= cfg.getParameter<std::string>("globalTag");
	KTreeMetadataObject.runPeriod				= cfg.getParameter<std::string>("runPeriod");
	KTreeMetadataObject.kappaTag				= cfg.getParameter<std::string>("kappaTag");
	KTreeMetadataObject.isEmbedded			= cfg.getParameter<bool>("isEmbedded");
	KTreeMetadataObject.jetMultiplicity		= cfg.getParameter<int>("jetMultiplicity");

	// write parameters in GetUserInfo of lumi tree
	std::vector<TList*> label;

	label.push_back( new TList() );
		label.back()->SetName("dataset");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.dataset).c_str()) );

	label.push_back( new TList() );
		label.back()->SetName("generator");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.generator).c_str()) );

	label.push_back( new TList() );
		label.back()->SetName("tune");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.tune).c_str()) );

	label.push_back( new TList() );
		label.back()->SetName("productionProcess");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.productionProcess).c_str()) );

	label.push_back( new TList() );
		label.back()->SetName("globalTag");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.globalTag).c_str()) );

	label.push_back( new TList() );
		label.back()->SetName("runPeriod");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.runPeriod).c_str()) );

	label.push_back( new TList() );
		label.back()->SetName("kappaTag");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.kappaTag).c_str()) );

	label.push_back( new TList() );
		label.back()->SetName("isEmbedded");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.isEmbedded).c_str()) );

	label.push_back( new TList() );
		label.back()->SetName("jetMultiplicity");
		tstring.push_back( new TObjString(getString(KTreeMetadataObject.jetMultiplicity).c_str()) );

	for(unsigned int i = 0; i < label.size(); i++)
		{
		label[i]->Add(tstring[i]);
		_lumi_tree->GetUserInfo()->Add(label[i]);
		}

	}

	static const std::string getLabel() { return "TreeMetadata"; }

	KTreeMetadata KTreeMetadataObject;
	std::vector<TObjString*> tstring;
	std::vector<TList*> label;

	// conversion functions to write block above in a uniform way
	inline std::string getString(bool input) { if(input == true) return "True"; else return "False"; }
	inline std::string getString(int input) { return static_cast<std::ostringstream*>( &(std::ostringstream() << input) )->str(); }
	inline std::string getString(std::string input) { return input; }

};

#endif
