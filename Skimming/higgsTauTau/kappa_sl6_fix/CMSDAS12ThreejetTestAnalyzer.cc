// Created: Mon Nov 7 21:58:01 CET 2011 $Id: CMSDAS12ThreejetTestAnalyzer.cc,v 1.1.2.3 2012/01/25 11:23:38 duggan Exp $

#include "RecoJets/JetAnalyzers/interface/CMSDAS12ThreejetTestAnalyzer.h"

CMSDAS12ThreejetTestAnalyzer::CMSDAS12ThreejetTestAnalyzer(const edm::ParameterSet& iConfig) {
}

void CMSDAS12ThreejetTestAnalyzer::beginJob() {
/*
  const int   NBINS = 52;
  double BINNING[NBINS+1] = {0.,5.,10.,15.,20.,25.,30.,35.,40.,45.,50.,56.,62.,68.,75.,
			     83.,91.,100.,110.,121.,133.,147.,162.,179.,197.,217.,239.,
			     263.,290.,319.,351.,386.,425.,468.,515.,567.,624.,687.,756.,
			     832.,915.,1007.,1108.,1219.,1341.,1475.,1623.,1785.,1964.,
			     2160.,2376.,2614.,3000.};
*/

  outputFile = new TFile("myhistos.root","recreate");
  
  //setup histograms
  hNJets             = new TH1F("hNJets",             "Number of PAT Jets",                          100, 0.0, 100.0);
  hNGoodJets         = new TH1F("hNGoodJets",         "Number of Selected Jets",                     100, 0.0, 100.0);

  //Jet Phi
  hJetPhi            = new TH1F("hJetPhi",            "Jet #phi; Entries; Jet #phi",                 50, -TMath::Pi(), TMath::Pi());
  hSelJetPhi         = new TH1F("hSelJetPhi",         "Jet #phi; Entries; Jet #phi",                 50, -TMath::Pi(), TMath::Pi());

  //Jet Pt
  hJetPt             = new TH1F("hJetPt",             "Jet p_{T}; Entries; Jet p_{T} (GeV)",         200, 0.0, 2000.);
  hSelJetPt          = new TH1F("hSelJetPt",          "Jet p_{T}; Entries; Jet p_{T} (GeV)",         200, 0.0, 2000.);

  //Jet Eta
  hJetEta            = new TH1F("hJetEta",            "Jet #eta; Entries; Jet #eta",                 50, -5.0, 5.);
  hSelJetEta         = new TH1F("hSelJetEta",         "Jet #eta; Entries; Jet #eta",                 50, -5.0, 5.);

  //HT for the event
  hSumHT             = new TH1F("hSumHT",             "#Sigma H_{T}; Events; #Sigma H_{T} (GeV)",    150, 0.0, 3000.);
  hSelHT             = new TH1F("hSelHT",             "#Sigma H_{T}; Events; #Sigma H_{T} (GeV)",    150, 0.0, 3000.);

  //Jet triplet invariant mass
  hPartonMass        = new TH1F("hPartonMass",        "Particle Jet Triplet Mass",                   300, 0.0, 3000.);
  hGenjetMass        = new TH1F("hGenjetMass",        "GenJet Triplet Mass",                         300, 0.0, 3000.);
  hMatchedMass       = new TH1F("hMatchedMass",       "PatJet Matched Triplet Mass",                 300, 0.0, 3000.);
  hAllTripletMass    = new TH1F("hAllTripletMass",    "PatJet Triplet Mass (20 Combinations)",       300, 0.0, 3000.);
  hTripletMass       = new TH1F("hTripletMass",       "PatJet Triplet Mass",                         300, 0.0, 3000.);
  //hMatchedMass       = new TH1F("hMatchedMass",       "PatJet Matched Triplet Mass",                 NBINS, BINNING);
  //hAllTripletMass    = new TH1F("hAllTripletMass",    "PatJet Triplet Mass (20 Combinations)",       NBINS, BINNING);
  //hTripletMass       = new TH1F("hTripletMass",       "PatJet Triplet Mass",                         NBINS, BINNING);


  //2D Jet triplet mass vs. triplet scalar sum pt
  hGenjetMassVsSumPt     = new TH2F("hGenjetMassVsSumPt",    "GenJet Triplet Mass vs. Triplet Sum P_{T}",            150, 0.0, 3000., 150, 0.0, 3000.);
  hPartonMassVsSumPt     = new TH2F("hPartonMassVsSumPt",    "Particle Jet Triplet Mass vs. Triplet Sum P_{T}",      150, 0.0, 3000., 150, 0.0, 3000.);
  hMatchedMassVsSumPt    = new TH2F("hMatchedMassVsSumPt",   "PatJet Matched Triplet Mass vs. Triplet Sum P_{T}",    150, 0.0, 3000., 150, 0.0, 3000.);
  hAllTripletMassVsSumPt = new TH2F("hAllTripletMassVsSumPt","PatJet Triplet Mass vs. Triplet Sum P_{T} (20 Combos)",150, 0.0, 3000., 150, 0.0, 3000.);
  hTripletMassVsSumPt    = new TH2F("hTripletMassVsSumPt",   "PatJet Triplet Mass vs.  Triplet Sum P_{T}",           150, 0.0, 3000., 150, 0.0, 3000.);
}

void CMSDAS12ThreejetTestAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {

  //Load in Pat Jet collection (PFJets)
  iEvent.getByLabel("selectedPatJetsAK5PF", PatJets);
  std::vector<pat::Jet> const & Jets = *PatJets;

  //Define jet containers and iterators
  std::vector<pat::Jet> selectedJets;
  std::vector<pat::Jet>::const_iterator iJet;
  //float sumHT    = 0.0;

  //Fill a histogram
  hNJets->Fill(Jets.size());

  //Looping over all jets
  for ( iJet =  Jets.begin(); iJet !=  Jets.end() ; ++iJet) {
    pat::Jet jet = *iJet;

    //Accessing jet quantities
    //jet.pt();
    //jet.eta();
    //jet.phi();
    //Fill Histograms
    //hJetPt ->Fill(jet.pt());
    //hJetEta->Fill(jet.eta());
    //hJetPhi->Fill(jet.phi());   
    
    selectedJets.push_back(jet);
  }
  //hSumHT    -> Fill(sumHT);

  //size of container for selected jets:
  //selectedJets.size()
  //access i^th jet of selected jets collection
  //selectedJets[i]
  //Accessing i^th jet's 4-vector:
  //selectedJets[i].p4()
  //Accessing i^th jet's invariant mass:
  //selectedJets[i].mass()

}


void CMSDAS12ThreejetTestAnalyzer::endJob() { 
  outputFile->cd();
  hNJets->Write();
  hJetPt->Write();
  hJetEta->Write();
  hJetPhi->Write();
  hSumHT->Write();
  hNGoodJets->Write();
  hSelJetPt->Write();
  hSelJetEta->Write();
  hSelJetPhi->Write();
  hSelHT->Write();
  hGenjetMass->Write();
  hGenjetMassVsSumPt->Write();
  hPartonMass->Write();
  hPartonMassVsSumPt->Write();
  hMatchedMass->Write();
  hMatchedMassVsSumPt->Write();
  hAllTripletMass->Write();
  hAllTripletMassVsSumPt->Write();
  hTripletMass->Write();
  hTripletMassVsSumPt->Write();
  outputFile->Write(); outputFile->Close();
}

bool CMSDAS12ThreejetTestAnalyzer::findMCDaughters(std::vector<pat::Jet> myJets){
  genjets.clear();
  partons.clear();
  matchedjets.clear();
  std::auto_ptr<reco::GenParticleCollection> children(new reco::GenParticleCollection());
  std::auto_ptr<reco::GenJetCollection> gjets(new reco::GenJetCollection());
  std::vector<pat::Jet> foundJets;
  std::vector<pat::Jet>::const_iterator iJet;

  for ( iJet = myJets.begin(); iJet != myJets.end(); ++iJet) {
    pat::Jet jet                   = *iJet;
    const reco::GenJet*     gjet   = jet.genJet();
    const reco::GenParticle* child = jet.genParton();
    if (!child || !gjet) continue;
    reco::GenParticle daughter(*child);
    reco::GenJet genjet(*gjet);
    children->push_back(daughter);
    gjets->push_back(genjet);
    foundJets.push_back(jet);
  }

  if (children->size() < 3) return false;
  for (int i = 0; i < int(children->size() - 2); ++i){
    for (int j = i+1; j < int(children->size() - 1); ++j){
      for (int k = j+1; k < int(children->size() - 0); ++k){
	if ((*children)[i].motherRef() == (*children)[j].motherRef() && (*children)[i].motherRef() == (*children)[k].motherRef())
	  {
            float dEta = (foundJets[i].p4() + foundJets[j].p4() + foundJets[k].p4()).eta() - (*children)[i].motherRef()->eta();
            float dPhi = (foundJets[i].p4() + foundJets[j].p4() + foundJets[k].p4()).phi() - (*children)[i].motherRef()->phi();
            float dR = sqrt( dEta*dEta + dPhi*dPhi);
            if (dR > 0.25) continue;
	    reco::GenParticle* d1 = (*children)[i].clone();
	    reco::GenParticle* d2 = (*children)[j].clone();
	    reco::GenParticle* d3 = (*children)[k].clone();
	    reco::GenJet*      g1 = (*gjets)[i].clone();
	    reco::GenJet*      g2 = (*gjets)[j].clone();
	    reco::GenJet*      g3 = (*gjets)[k].clone();
	    genjets.push_back(g1); genjets.push_back(g2); genjets.push_back(g3);
	    partons.push_back(d1); partons.push_back(d2); partons.push_back(d3);
	    matchedjets.push_back(foundJets[i]);
	    matchedjets.push_back(foundJets[j]);
	    matchedjets.push_back(foundJets[k]);
	  }
      }
    }
  }
  if (genjets.size() > 0  && partons.size() > 0) return true;
  else return false;
}

DEFINE_FWK_MODULE(CMSDAS12ThreejetTestAnalyzer); // define this as a plug-in
