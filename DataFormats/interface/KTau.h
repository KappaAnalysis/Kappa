#ifndef KAPPA_TAU_H
#define KAPPA_TAU_H

#include "KBasic.h"

struct KDataTau : KDataLV
{
	char charge;
};

struct KDataCaloTau : KDataTau
{
};

struct KDataPFTau : KDataTau
{  
  unsigned long discr;
  
  float emFraction;
  
  int cntSignalChargedHadrCands, cntSignalGammaCands, cntSignalNeutrHadrCands, cntSignalCands;
  
  RMDataLV leadTrack;
  RMDataLV leadChargedHadrTrack;
  RMDataLV leadNeutralTrack;
  
  //bool longLived
  int cntSignalTracks;
};

struct KDataGenTau : KDataLV
{
	RMDataLV p4_vis;		// momenta of visible particles
	int status;
	char decayMode;
	//  0 - undefined
	//	1 - electron
	//	2 - muon
	// >2 - hadronic
	// most significant bit (1<<15):
	//		0 = tau
	//		1 = descendant of a tau
	KDataVertex vertex;
};

typedef std::vector<KDataTau> KDataTaus;
typedef std::vector<KDataCaloTau> KDataCaloTaus;
typedef std::vector<KDataPFTau> KDataPFTaus;
typedef std::vector<KDataGenTau> KDataGenTaus;

#endif

