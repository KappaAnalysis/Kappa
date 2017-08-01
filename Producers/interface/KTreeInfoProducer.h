//- Copyright (c) 2014 - All Rights Reserved
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_TREE_METADATAPRODUCER_H
#define KAPPA_TREE_METADATAPRODUCER_H

#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"


class KTreeInfoProducer: public KBaseProducer
{
public:
	KTreeInfoProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector)
	{
	
		TList* keys = new TList();
		keys->SetName("keys");
		
		TList* values = new TList();
		values->SetName("values");
		
		edm::ParameterSet parameterSet(cfg.getParameterSet("parameters"));
		const std::vector<std::string> parameterNames(parameterSet.getParameterNames());
		for (std::vector<std::string>::const_iterator iParam = parameterNames.begin(), iEnd = parameterNames.end(); iParam != iEnd; ++iParam)
		{
			keys->Add(new TObjString(iParam->c_str()));
			
			std::string parameterValue;
			if(parameterSet.existsAs<std::string>(*iParam))
			{
				parameterValue = getString(parameterSet.getParameter<std::string>(*iParam));
			}
			if(parameterSet.existsAs<int>(*iParam))
			{
				parameterValue = getString(parameterSet.getParameter<int>(*iParam));
			}
			if(parameterSet.existsAs<bool>(*iParam))
			{
				parameterValue = getString(parameterSet.getParameter<bool>(*iParam));
			}
			values->Add(new TObjString(parameterValue.c_str()));
		}
		
		_lumi_tree->GetUserInfo()->Add(keys);
		_lumi_tree->GetUserInfo()->Add(values);
	}

	static const std::string getLabel() { return "TreeInfo"; }

	inline std::string getString(bool input) { if (input) return "True"; else return "False"; }
	inline std::string getString(int input) { return static_cast<std::ostringstream*>( &(std::ostringstream() << input) )->str(); }
	inline std::string getString(std::string input) { return input; }

};

#endif
