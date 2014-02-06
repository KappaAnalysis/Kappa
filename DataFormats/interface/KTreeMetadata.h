/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 *   Raphael Friese <raphael.friese@cern.ch>
 */

#ifndef KAPPA_TREE_METADATA_H
#define KAPPA_TREE_METADATA_H

#include <algorithm>
#include <sstream>

struct KTreeMetadata
{
	std::string dataset;
	std::string generator;
	std::string tune;
	std::string productionProcess;
	std::string globalTag;
	std::string runPeriod;
	std::string kappaTag;
	bool isEmbedded;
	int jetMultiplicity;

	int year() { return 0; }
	int centerOfMassEnergy() { return 0; }
	bool isStandardModel() { return true; }
	bool isHiggs() { return false; }
	bool isData() { return false;}

};

#endif
