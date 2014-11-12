import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
##  rerun tau reconstruction sequence following POG recommendation:
##  https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#5_3_12_and_higher
##  rerun recoTauClassicHPSSequence to get newest taus
#from RecoTauTag.Configuration.RecoPFTauTag_cff import *

from RecoVertex.PrimaryVertexProducer.OfflinePrimaryVertices_cfi import *
#from RecoVertex.PrimaryVertexProducer.OfflinePrimaryVerticesWithBS_cfi import *
from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import *
from Configuration.Geometry.GeometryIdeal_cff import *
from Configuration.StandardSequences.MagneticField_cff import *
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
## ------------------------------------------------------------------------
## Definition of sequences
## run this to get latest greatest HPS taus
makeKappaUnbiasedDiTauPVs = cms.Sequence(
     offlinePrimaryVertices #*
#     offlinePrimaryVerticesWithBS
#    recoTauClassicHPSSequence
    )
