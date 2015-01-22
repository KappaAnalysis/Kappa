//- Copyright (c) 2014 - All Rights Reserved
//-  * Roger Wolf <roger.wolf@cern.ch>

#include <FWCore/Framework/interface/MakerMacros.h>

#include <CommonTools/UtilAlgos/interface/AnySelector.h>
#include <CommonTools/UtilAlgos/interface/AndSelector.h>
#include <CommonTools/UtilAlgos/interface/ObjectCountFilter.h>
#include <CommonTools/UtilAlgos/interface/MinNumberSelector.h>
#include <CommonTools/UtilAlgos/interface/MaxNumberSelector.h>

#include <DataFormats/Common/interface/View.h>
#include <DataFormats/VertexReco/interface/Vertex.h>


typedef ObjectCountFilter<edm::View<reco::Vertex>, AnySelector, AndSelector<MinNumberSelector, MaxNumberSelector> >::type KVertexFilter;


DEFINE_FWK_MODULE(KVertexFilter);
