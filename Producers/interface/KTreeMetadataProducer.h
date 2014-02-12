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

class KTreeMetadataProducer: public KBaseProducer
{
public:
	KTreeMetadataProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree)
	{
	
		std::vector<TList*> label;
		edm::ParameterSet parameterSet(cfg.getParameterSet("parameters"));
		const std::vector<std::string> parameterNames(parameterSet.getParameterNames());
		for (std::vector<std::string>::const_iterator iParam = parameterNames.begin(), iEnd = parameterNames.end(); iParam != iEnd; ++iParam)
		{
			label.push_back( new TList() );
			label.back()->SetName(iParam->c_str());
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

			tstring.push_back( new TObjString(parameterValue.c_str() ) );
			label.back()->Add(tstring.back());

		}

		for(unsigned int i = 0; i < label.size(); i++)
			{
			_lumi_tree->GetUserInfo()->Add(label[i]);
			}

	}
	std::vector<TObjString*> tstring;

	static const std::string getLabel() { return "TreeMetadata"; }

	inline std::string getString(bool input) { if(input == true) return "True"; else return "False"; }
	inline std::string getString(int input) { return static_cast<std::ostringstream*>( &(std::ostringstream() << input) )->str(); }
	inline std::string getString(std::string input) { return input; }

};

#endif
