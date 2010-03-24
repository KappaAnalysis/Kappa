#ifndef KAPPA_DEBUG_H
#define KAPPA_DEBUG_H

#include <iostream>
#include "../src/classes.h"

using namespace std;

std::ostream &operator<<(std::ostream &os, const KLV &v)     { return os << v.p4; }

std::ostream &operator<<(std::ostream &os, const KDataLV &v) { return os << v.p4; }

std::ostream &operator<<(std::ostream &os, const KParton &v)
{
	bool neg = (v.pdgid & (1 << KPartonChargeMask)) != 0;
	unsigned status = (v.pdgid >> KPartonStatusMask) % 8;
	int id = (v.pdgid % (1 << KPartonStatusMask)) * (neg ? -1 : 1);
	return os << status << "|" << id << "|" << v.p4;
}

std::ostream &operator<<(std::ostream &os, const KGenLumiMetadata &v)
{
	os << v.nRun << " " << v.xSectionExt << " " << v.xSectionInt;
	for (size_t i = 0; i < v.hltNames.size(); ++i)
		cout << "(" << i << " = " << v.hltNames[i] << ") ";
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenEventMetadata &v)
{
	os << v.bitsHLT << " " << v.nEvent << " " << v.nRun << " "
		<< v.binValue << " " << v.alphaQCD << endl;
	return os;
}

template<typename T>
void printvec(const T *v)
{
	cout << "Size: " << v->size() << endl;
	for (typename T::const_iterator it = v->begin(); it != v->end(); ++it)
		cout << " " << *it;
	cout << endl;
}

#endif
