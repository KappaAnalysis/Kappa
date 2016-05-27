
#ifndef KDATAFORMAT_HXX
#define KDATAFORMAT_HXX

unsigned int roundToSignificantDigitsAndHash(const double &value, int nDigits, const unsigned int &base);
unsigned int getLVChargeHash(const double &pt, const double &eta, const double &phi, const double &mass, const int &charge);
unsigned int bitShift(const unsigned int &base, const int &digits);

#endif
