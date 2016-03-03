
#include <boost/functional/hash.hpp>

#include "Kappa/DataFormats/interface/Hash.h"

unsigned int roundToSignificantDigitsAndHash(const double &value, int nDigits, const unsigned int &base)
{
	int p = nDigits - (unsigned int)std::log10(value);
	return base ^ bitShift(boost::hash<int>()(int(std::floor(value * std::pow(10.0, p) + 0.5))), 1);
}

unsigned int bitShift(const unsigned int &base, const int &digits)
{
	return (base >> digits) | (base << (sizeof(unsigned int)*8 - digits));
}

unsigned int getLVChargeHash(const double &pt, const double &eta, const double &phi, const double &mass, const int &charge)
{
	// needs to be boost::hash instead of std::hash which is only available since C++11 that is not used in CMSSW 53X
	unsigned int hash = 0;
	hash = roundToSignificantDigitsAndHash(pt, 6, hash);
	hash = bitShift(hash, 3);
	hash = roundToSignificantDigitsAndHash(eta, 6, hash);
	hash = bitShift(hash, 3);
	hash = roundToSignificantDigitsAndHash(phi, 6, hash);
	hash = bitShift(hash, 3);
	hash = roundToSignificantDigitsAndHash(mass, 6, hash);
	hash = bitShift(hash, 3);
	hash = hash ^ boost::hash<int>()(charge);
	hash = bitShift(hash, 3);
	return hash;
}

