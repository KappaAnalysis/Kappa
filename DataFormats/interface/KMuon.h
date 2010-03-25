#ifndef KAPPA_MUON_H
#define KAPPA_MUON_H

#include "KBasic.h"

struct KDataMuon : KDataLV
{
	char charge;

  KDataTrack track;
  KDataTrack globalTrack;
  KDataTrack innerTrack;

  KDataVertex vertex;

  bool isTrackerMuon;
  bool isCaloMuon;
  bool isStandAloneMuon;
  bool isGlobalMuon;

  float hcalIso03;
  float ecalIso03;
  float trackIso03;

  float hcalIso05;
  float ecalIso05;
  float trackIso05;

  float hcalIso06;
  float ecalIso06;
  float trackIso06;

  unsigned int isGoodMuon;

  float caloComp, segComp;

  int numberOfChambers;
  int trackHits;

  int timeNDof;
  float timeAtIpInOut;
  float timeAtIpInOutErr;
  float timeAtIpOutIn;
  float timeAtIpOutInErr;
  int direction;

  unsigned long hltMatch;
};

typedef std::vector<KDataMuon> KDataMuons;

#endif

