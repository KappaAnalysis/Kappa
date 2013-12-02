/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_ELECTRON_H
#define KAPPA_ELECTRON_H

#include "KTrack.h"
#include "KMetadata.h"
#include "KJetMET.h"

#include <algorithm>

struct KDataElectron : KDataLV
{
	char charge;

};
typedef std::vector<KDataElectron> KDataElectrons;

#endif
