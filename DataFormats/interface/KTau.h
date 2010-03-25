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

typedef std::vector<KDataTau> KDataTaus;
typedef std::vector<KDataCaloTau> KDataCaloTaus;
typedef std::vector<KDataPFTau> KDataPFTaus;

#endif

