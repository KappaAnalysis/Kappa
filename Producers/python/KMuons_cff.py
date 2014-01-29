import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Reconstruction_cff import *
from CommonTools.ParticleFlow.Isolation.tools_cfi import isoDepositReplace
pfmuIsoDepositPFCandidates = isoDepositReplace('muons', 'particleFlow')


