#ifndef KAPPA_JET_H
#define KAPPA_JET_H

#include <Math/SMatrix.h>
#include "KBasic.h"

struct KDataJet : public KDataLV
{
	double area;
	double fHPD, fRBX;
	double fEM, fHO;
	int nConst, n90Hits;
};
typedef std::vector<KDataJet> KDataJets;

struct KDataPFJet : public KDataLV
{
	double area;
	float neutralEMFraction, chargedEMFraction;
	float neutralHadFraction, chargedHadFraction;
	float muonFraction, photonFraction, electronFraction;
	float HFHadFraction, HFEMFraction;

	int nConst, nCharged;
};
typedef std::vector<KDataPFJet> KDataPFJets;


struct KDataPFJetTagged : public KDataPFJet
{
	float QGLikelihood, QGMLP,

        TrackCountingHighEffBJetTag,TrackCountingHighPurBJetTag,
        JetProbabilityBJetTag, JetBProbabilityBJetTag,
        SoftElectronBJetTag, SoftMuonBJetTag, SoftMuonByIP3dBJetTag, SoftMuonByPtBJetTag,
        SimpleSecondaryVertexBJetTag, CombinedSecondaryVertexBJetTag, CombinedSecondaryVertexMVABJetTag,

        PUJetMVAfull, PUJetMVAcutbased;
    int PUJetIDfull, PUJetIDcutbased;
    bool PUJetIDfull_passloose, PUJetIDfull_passmedium, PUJetIDfull_passtight, 
        PUJetIDcutbased_passloose, PUJetIDcutbased_passmedium, PUJetIDcutbased_passtight;
};
typedef std::vector<KDataPFJetTagged> KDataPFJetsTagged;


struct KDataMET : public KDataLV
{
	double sumEt;

	ROOT::Math::SMatrix<double, 2, 2, ROOT::Math::MatRepSym<double, 2> > significance;
};

struct KDataPFMET : public KDataMET
{
	double chargedEMEtFraction, chargedHadEtFraction;
	double neutralEMEtFraction, neutralHadEtFraction;
	double muonEtFraction;
	double type6EtFraction, type7EtFraction;
};

struct KHCALNoiseSummary
{
	bool hasBadRBXTS4TS5;
	float isolatedNoiseSumE;
	float isolatedNoiseSumEt;
	float max25GeVHitTime;
	float maxE2Over10TS;
	int maxHPDHits;
	int maxHPDNoOtherHits;
	int maxRBXHits;
	int maxZeros;
	float min25GeVHitTime;
	float minE2Over10TS;
	float minRBXEMF;
	int numIsolatedNoiseChannels;
};

#define KAPPA_FEATURE_JETAREA
struct KJetArea
{
	float median, sigma;
};

#endif
