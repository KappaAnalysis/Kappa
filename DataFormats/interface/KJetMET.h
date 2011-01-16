#ifndef KAPPA_JET_H
#define KAPPA_JET_H

#include "KBasic.h"

struct KDataJet : public KDataLV
{
	double area;
	double noiseHCAL;
	double fHPD, fRBX;
	double fEM, fHO;
	int nConst, n90, n90Hits;
};
typedef std::vector<KDataJet> KDataJets;

struct KDataPFJet : public KDataLV
{
	double area;
	float neutralEMFraction, chargedEMFraction;
	float neutralHadFraction, chargedHadFraction;
	int nConst, n90;
};
typedef std::vector<KDataPFJet> KDataPFJets;

struct KDataMET : public KDataLV
{
	double sumEt;
};

struct KDataPFMET : public KDataMET
{
	double chargedEMEtFraction, chargedHadEtFraction;
	double neutralEMEtFraction, neutralHadEtFraction;
	double muonEtFraction;
	double type6EtFraction, type7EtFraction;
};

#define KAPPA_FEATURE_JETAREA
struct KJetArea
{
	float median, sigma;
};
#endif
