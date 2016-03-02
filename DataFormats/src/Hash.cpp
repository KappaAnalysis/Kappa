
#include <boost/functional/hash.hpp>

#include "Kappa/DataFormats/interface/Hash.h"

int roundToSignificantDigits(double value, int nDigits)
{
	int p = nDigits - (unsigned int)std::log10(value);
	return int(std::floor(value * std::pow(10.0, p) + 0.5));
}
int getLVChargeHash(double pt, double eta, double phi, double mass, int charge)
{
	// needs to be boost::hash instead of std::hash which is only available since C++11 that is not used in CMSSW 53X
	return (boost::hash<int>()(roundToSignificantDigits(pt, 8)) ^
	        boost::hash<int>()(roundToSignificantDigits(eta, 8)) ^
	        boost::hash<int>()(roundToSignificantDigits(phi, 8)) ^
	        boost::hash<int>()(roundToSignificantDigits(mass, 8)) ^
	        boost::hash<int>()(charge));
}

