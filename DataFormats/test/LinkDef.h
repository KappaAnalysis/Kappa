/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#include "../src/classes.h"

#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;

/************************************************************/
/* BASIC BUILDING BLOCKS                                    */
/************************************************************/

#pragma link C++ class ROOT::Math::PtEtaPhiM4D<float>+;
#pragma link C++ class ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >+;
#pragma link C++ typedef RMFLV_Store;
#pragma link C++ typedef RMFLV;

// Already defined by ROOT:
//#pragma link C++ class ROOT::Math::PtEtaPhiM4D<double>+;
//#pragma link C++ class ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double> >+;
#pragma link C++ typedef RMDLV_Store;
#pragma link C++ typedef RMDLV;

#pragma link C++ class ROOT::Math::Cartesian3D<float>+;
#pragma link C++ class ROOT::Math::PositionVector3D<ROOT::Math::Cartesian3D<float> >+;
#pragma link C++ class ROOT::Math::DisplacementVector3D<ROOT::Math::Cartesian3D<float>, ROOT::Math::DefaultCoordinateSystemTag>+;
#pragma link C++ typedef RMPoint;

#pragma link C++ class ROOT::Math::RowOffsets<2>+;
#pragma link C++ class ROOT::Math::MatRepSym<double,2>+;
#pragma link C++ class ROOT::Math::SymMatrixOffsets<2>+;
#pragma link C++ class ROOT::Math::SMatrix<double,2,2,ROOT::Math::MatRepSym<double,2> >+;

#pragma link C++ class ROOT::Math::RowOffsets<3>+;
#pragma link C++ class ROOT::Math::MatRepSym<double,3>+;
#pragma link C++ class ROOT::Math::SymMatrixOffsets<3>+;
#pragma link C++ class ROOT::Math::SMatrix<double,3,3,ROOT::Math::MatRepSym<double,3> >+;

#pragma link C++ class ROOT::Math::RowOffsets<7>+;
#pragma link C++ class ROOT::Math::MatRepSym<double,7>+;
#pragma link C++ class ROOT::Math::SymMatrixOffsets<7>+;
#pragma link C++ class ROOT::Math::SMatrix<double,7,7,ROOT::Math::MatRepSym<double,7> >+;

/************************************************************/
/* DATATYPES                                                */
/************************************************************/

#pragma link C++ struct KLV+;
#pragma link C++ class std::vector<KLV>+;
#pragma link C++ typedef KLVs;

#pragma link C++ struct KLepton+;
#pragma link C++ class std::vector<KLeptons>+;
#pragma link C++ typedef KLeptons;

#pragma link C++ struct KDataMET+;
#pragma link C++ struct KDataPFMET+;

#pragma link C++ struct KDataTrack+;
#pragma link C++ class std::vector<KDataTrack>+;
#pragma link C++ typedef KDataTracks;

#pragma link C++ struct KTrackSummary+;

#pragma link C++ struct KDataJet+;
#pragma link C++ class std::vector<KDataJet>+;
#pragma link C++ typedef KDataJets;

#pragma link C++ struct KDataPFJet+;
#pragma link C++ class std::vector<KDataPFJet>+;
#pragma link C++ typedef KDataPFJets;

#pragma link C++ struct KDataPFTaggedJet+;
#pragma link C++ class std::vector<KDataPFTaggedJet>+;
#pragma link C++ typedef KDataPFTaggedJets;

#pragma link C++ struct KDataMuon+;
#pragma link C++ class std::vector<KDataMuon>+;
#pragma link C++ typedef KDataMuons;

#pragma link C++ struct KDataElectron+;
#pragma link C++ class std::vector<KDataElectron>+;
#pragma link C++ typedef KDataElectrons;

#pragma link C++ struct KTauDiscriminatorMetadata+;
#pragma link C++ struct KMuonMetadata+;

#pragma link C++ struct KDataTau+;
#pragma link C++ class std::vector<KDataTau>+;
#pragma link C++ typedef KDataTaus;

#pragma link C++ struct KDataCaloTau+;
#pragma link C++ class std::vector<KDataCaloTau>+;
#pragma link C++ typedef KDataCaloTaus;

#pragma link C++ struct KDataPFTau+;
#pragma link C++ class std::vector<KDataPFTau>+;
#pragma link C++ typedef KDataPFTaus;

#pragma link C++ struct KDataGenTau+;
#pragma link C++ class std::vector<KDataGenTau>+;
#pragma link C++ typedef KDataGenTaus;
#pragma link C++ struct KUnbiasedDiTauPV;

#pragma link C++ struct KDataVertex+;
#pragma link C++ class std::vector<KDataVertex>+;
#pragma link C++ typedef KDataVertices;

#pragma link C++ struct KVertexSummary+;

#pragma link C++ struct KDataBeamSpot+;
#pragma link C++ class std::vector<KDataBeamSpot>+;
#pragma link C++ typedef KDataBeamSpots;

#pragma link C++ struct KGenParticle+;
#pragma link C++ class std::vector<KGenParticle>+;
#pragma link C++ typedef KGenParticles;

#pragma link C++ struct KDataHit+;
#pragma link C++ class std::vector<KDataHit>+;
#pragma link C++ typedef KDataHits;

#pragma link C++ struct KL1Muon+;
#pragma link C++ class std::vector<KL1Muon>+;
#pragma link C++ typedef KL1Muons;

#pragma link C++ struct KPFCandidate+;
#pragma link C++ class std::vector<KPFCandidate>+;
#pragma link C++ typedef KPFCandidates;

#pragma link C++ struct KGenPhoton+;
#pragma link C++ class std::vector<KGenPhoton>+;
#pragma link C++ typedef KGenPhotons;

#pragma link C++ struct KJetArea+;
#pragma link C++ struct KHCALNoiseSummary+;
#pragma link C++ struct KFilterSummary+;
#pragma link C++ struct KFilterMetadata+;
#pragma link C++ struct KTaggerMetadata+;
#pragma link C++ struct KElectronIdMetadata+;
#pragma link C++ struct KTriggerInfos+;

#pragma link C++ class std::vector<std::vector<size_t> >+;
#pragma link C++ struct KTriggerObjects+;

#pragma link C++ struct KMuonTriggerCandidate+;
#pragma link C++ class std::vector<KMuonTriggerCandidate>+;
#pragma link C++ typedef KMuonTriggerCandidates;

/************************************************************/
/* METADATA                                                 */
/************************************************************/

#pragma link C++ struct KProvenance+;

// Already defined by ROOT:
//#pragma link C++ class std::map<std::string, int>+;
#pragma link C++ struct KLumiMetadata+;
#pragma link C++ struct KGenLumiMetadata+;
#pragma link C++ struct KDataLumiMetadata+;

#pragma link C++ struct KEventMetadata+;
#pragma link C++ struct KGenEventMetadata+;

/************************************************************/

#endif
