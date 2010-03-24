#include "../src/classes.h"

#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;

/************************************************************/

#pragma link C++ class ROOT::Math::PtEtaPhiM4D<float>+;
#pragma link C++ class ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >+;
#pragma link C++ typedef RMDataLV_Store;
#pragma link C++ typedef RMDataLV;

// Already defined by ROOT:
//#pragma link C++ class ROOT::Math::PtEtaPhiM4D<double>+;
//#pragma link C++ class ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double> >+;
#pragma link C++ typedef RMLV_Store;
#pragma link C++ typedef RMLV;

#pragma link C++ class ROOT::Math::Cartesian3D<float>+;
#pragma link C++ class ROOT::Math::PositionVector3D<ROOT::Math::Cartesian3D<float> >+;
#pragma link C++ class ROOT::Math::DisplacementVector3D<ROOT::Math::Cartesian3D<float>, ROOT::Math::DefaultCoordinateSystemTag>+;
#pragma link C++ typedef RMPoint;

/************************************************************/

#pragma link C++ struct KDataLV+;
#pragma link C++ class std::vector<KDataLV>+;
#pragma link C++ typedef KDataLVs;

#pragma link C++ struct KDataMET+;

#pragma link C++ struct KDataTrack+;
#pragma link C++ class std::vector<KDataTrack>+;
#pragma link C++ typedef KDataTracks;

#pragma link C++ struct KDataJet+;
#pragma link C++ class std::vector<KDataJet>+;
#pragma link C++ typedef KDataJets;

#pragma link C++ struct KLV+;
#pragma link C++ class std::vector<KLV>+;
#pragma link C++ typedef KLVs;

#pragma link C++ struct KParton+;
#pragma link C++ class std::vector<KParton>+;
#pragma link C++ typedef KPartons;

/************************************************************/

#pragma link C++ struct KProvenance+;

// Already defined by ROOT:
//#pragma link C++ class std::map<std::string, int>+;
#pragma link C++ struct KLumiMetadata+;
#pragma link C++ struct KGenLumiMetadata+;

#pragma link C++ struct KEventMetadata+;
#pragma link C++ struct KGenEventMetadata+;

/************************************************************/

#endif
