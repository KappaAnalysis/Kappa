#ifndef KAPPA_JET_H
#define KAPPA_JET_H

#include "KBasic.h"

struct KDataJet : public KDataLV
{
	double emf;
	double area;
	int n90, n90Hits;
	double noiseHCAL;
	double detectorEta;
	double fHPD, fRBX;
	int nTracksAtCalo;
	int nTracksAtVertex;
	int nConst;
};
typedef std::vector<KDataJet> KDataJets;

struct KDataPFJet : public KDataJet
{
	float neutralEmFraction, chargedEmFraction;
	float neutralHadFraction, chargedHadFraction;
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

#endif
