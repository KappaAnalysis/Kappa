#ifndef KAPPA_DEBUG_H
#define KAPPA_DEBUG_H

#include <iostream>
#include "Kappa.h"

std::ostream &operator<<(std::ostream &os, const KLV &lv);
std::ostream &operator<<(std::ostream &os, const KDataLV &lv);
std::ostream &operator<<(std::ostream &os, const KDataBeamSpot &bs);
std::ostream &operator<<(std::ostream &os, const KDataMET &met);
std::ostream &operator<<(std::ostream &os, const KDataPFMET &met);
std::ostream &operator<<(std::ostream &os, const KTrackSummary &s);
std::ostream &operator<<(std::ostream &os, const KParton &p);
std::ostream &operator<<(std::ostream &os, const KDataJet &jet);
std::ostream &operator<<(std::ostream &os, const KDataTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataCaloTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataGenTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataVertex &vertex);
std::ostream &operator<<(std::ostream &os, const KProvenance &p);
std::ostream &operator<<(std::ostream &os, const KLumiMetadata &m);
std::ostream &operator<<(std::ostream &os, const KGenLumiMetadata &m);
std::ostream &operator<<(std::ostream &os, const KEventMetadata &m);
std::ostream &operator<<(std::ostream &os, const KGenEventMetadata &m);

template<typename T>
void displayVector(std::ostream &os, const T &v, size_t n = 0)
{
	if (n == 0)
	{
		os << "Size: " << v.size() << std::endl;
		n = v.size();
	}
	n = std::min(n, v.size());
	for (typename T::const_iterator it = v.begin(); (it != v.end()) && (n != 0); ++it, --n)
		os << *it << " ";
	os << std::endl;
}

void displayHLT(std::ostream &os, KLumiMetadata *metaLumi, KEventMetadata *metaEvent);

#endif
