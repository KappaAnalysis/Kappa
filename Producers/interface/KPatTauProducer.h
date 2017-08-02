//Todo: fill pf candidates

#ifndef KAPPA_PATTAUPRODUCER_H
#define KAPPA_PATTAUPRODUCER_H
#include "KBaseMultiLVProducer.h"
#include "KTauProducer.h"
#include "KVertexProducer.h"
#include "KVertexSummaryProducer.h"
#include "KPackedPFCandidateProducer.h"
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "TrackingTools/PatternTools/interface/ClosestApproachInRPhi.h"
#include "TrackingTools/TrajectoryState/interface/TrajectoryStateTransform.h"

#include <DataFormats/PatCandidates/interface/Tau.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "boost/functional/hash.hpp"

#if (CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0)
#include "RecoTauTag/RecoTau/interface/PFRecoTauClusterVariables.h"
#endif


class KPatTauProducer : public KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>
{
	protected:

		virtual void fillChargeAndFlavour(const SingleInputType &in, SingleOutputType &out)
		{
			out.leptonInfo = KLeptonFlavour::TAU;
			//assert(in.charge() == 1 || in.charge() == -1);
			if (in.charge() > 0)
				out.leptonInfo |= KLeptonChargeMask;
			if(in.isPFTau())
				out.leptonInfo |= KLeptonPFMask;

				pat::PackedCandidate const* packedLeadTauCand = dynamic_cast<pat::PackedCandidate const*>(in.leadChargedHadrCand().get());
				out.dz = packedLeadTauCand->dz();
				out.dxy = packedLeadTauCand->dxy();
				if (packedLeadTauCand->bestTrack() != nullptr)
				{
					KTrackProducer::fillTrack(*packedLeadTauCand->bestTrack(), out.track, std::vector<reco::Vertex>(), this->trackBuilder.product());
					KTrackProducer::fillIPInfo(*packedLeadTauCand->bestTrack(), out.track, *RefitVertices, trackBuilder.product());
				}
				else // at least fill reference point
				{
					out.track.ref.SetXYZ(in.vertex().x(), in.vertex().y(), in.vertex().z());
				}

			if (in.isPFTau()) out.emFraction = in.emFraction();

			out.decayMode = in.decayMode();
		}

		virtual void fillDiscriminators(const SingleInputType &in, SingleOutputType &out)
		{
			const std::vector<std::pair<std::string, float>> tauIDs = in.tauIDs();
			int digit = 0;
			out.binaryDiscriminators = 0;
			for(auto discriminator: discriminatorMap[names[0]]->binaryDiscriminatorNames)
			{
				if(in.tauID(discriminator) > 0.5 )
					out.binaryDiscriminators |= (1ull << digit);
				++digit;
			}

			out.floatDiscriminators.resize(n_float_dict);
			for(auto discriminator=realTauIdfloatmap[names[0]].begin(); discriminator != realTauIdfloatmap[names[0]].end(); discriminator++)
			{
				out.floatDiscriminators[discriminator->second] = in.tauID(discriminator->first);
			}

			#if (CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0)
				for(auto variable = extraTaufloatmap[names[0]].begin();  variable!= extraTaufloatmap[names[0]].end(); variable++)
				{
					if (variable->first == EXTRATAUFLOATS::decayDistX ) out.floatDiscriminators[variable->second] = in.flightLength().x();
					else if (variable->first == EXTRATAUFLOATS::decayDistY) out.floatDiscriminators[variable->second] = in.flightLength().y();
					else if (variable->first == EXTRATAUFLOATS::decayDistZ) out.floatDiscriminators[variable->second] = in.flightLength().z();
					else if (variable->first == EXTRATAUFLOATS::decayDistM) out.floatDiscriminators[variable->second] =  std::sqrt(in.flightLength().x()*in.flightLength().x()
																		+ in.flightLength().y()*in.flightLength().y()
																		+ in.flightLength().z()*in.flightLength().z());
					else if (variable->first == EXTRATAUFLOATS::nPhoton ) out.floatDiscriminators[variable->second] = (float)clusterVariables_.tau_n_photons_total(in);
					else if (variable->first == EXTRATAUFLOATS::ptWeightedDetaStrip ) out.floatDiscriminators[variable->second] = clusterVariables_.tau_pt_weighted_deta_strip(in, in.decayMode());
					else if (variable->first == EXTRATAUFLOATS::ptWeightedDphiStrip ) out.floatDiscriminators[variable->second] = clusterVariables_.tau_pt_weighted_dphi_strip(in, in.decayMode());
					else if (variable->first == EXTRATAUFLOATS::ptWeightedDrSignal ) out.floatDiscriminators[variable->second]  = clusterVariables_.tau_pt_weighted_dr_signal(in, in.decayMode());
					else if (variable->first == EXTRATAUFLOATS::ptWeightedDrIsolation) out.floatDiscriminators[variable->second]= clusterVariables_.tau_pt_weighted_dr_iso(in, in.decayMode());
					else if (variable->first == EXTRATAUFLOATS::leadingTrackChi2 )  out.floatDiscriminators[variable->second] = in.leadingTrackNormChi2();
					else if (variable->first == EXTRATAUFLOATS::eRatio )  out.floatDiscriminators[variable->second] = clusterVariables_.tau_Eratio(in);
				}
			#endif
		}

		virtual void fillPFCandidates(const SingleInputType &in, SingleOutputType &out)
		{
			cEvent->getByToken(this->tokenVertexCollection, this->VertexCollection);
			cEvent->getByToken(this->tokenBeamSpot, this->BeamSpot);

				std::vector<pat::PackedCandidate const*> tau_picharge;

				for(size_t i = 0; i < in.signalChargedHadrCands().size(); ++i)
				{
					KPFCandidate outCandidate;
					outCandidate.indexInOriginalCollection = i;

					if (kshortinformation[names[0]])
					{
						pat::PackedCandidate const* single_pion = dynamic_cast<pat::PackedCandidate const*>(in.signalChargedHadrCands()[i].get());
						tau_picharge.push_back(single_pion);

						outCandidate.bestTrack = KTrack();
						if (single_pion->bestTrack() != nullptr){
							KTrackProducer::fillTrack(*single_pion->bestTrack(), outCandidate.bestTrack, *VertexCollection, trackBuilder.product());
							KTrackProducer::fillIPInfo(*single_pion->bestTrack(), outCandidate.bestTrack, *RefitVertices, trackBuilder.product());
						}
						else
							outCandidate.bestTrack.ref.SetXYZ(single_pion->vertex().x(), single_pion->vertex().y(), single_pion->vertex().z());
					}

					KPackedPFCandidateProducer::fillPackedPFCandidate(*(in.signalChargedHadrCands()[i].get()), outCandidate);
					out.chargedHadronCandidates.push_back(outCandidate);
				}

				if (kshortinformation[names[0]])
				{
					for(size_t i = 0; i < in.isolationChargedHadrCands().size(); ++i)
					{
						KPFCandidate outCandidate;
						outCandidate.indexInOriginalCollection = i + in.signalChargedHadrCands().size();

						pat::PackedCandidate const* single_pion = dynamic_cast<pat::PackedCandidate const*>(in.isolationChargedHadrCands()[i].get());
						tau_picharge.push_back(single_pion);

						outCandidate.bestTrack = KTrack();
						if (single_pion->bestTrack() != nullptr){
							KTrackProducer::fillTrack(*single_pion->bestTrack(), outCandidate.bestTrack, *VertexCollection, trackBuilder.product());
							KTrackProducer::fillIPInfo(*single_pion->bestTrack(), outCandidate.bestTrack, *RefitVertices, trackBuilder.product());
						}
						else
							outCandidate.bestTrack.ref.SetXYZ(single_pion->vertex().x(), single_pion->vertex().y(), single_pion->vertex().z());

						KPackedPFCandidateProducer::fillPackedPFCandidate(*(in.isolationChargedHadrCands()[i].get()), outCandidate);
						out.isolationChargedHadronCandidates.push_back(outCandidate);
					}

					std::sort(out.isolationChargedHadronCandidates.begin(), out.isolationChargedHadronCandidates.end(), KLVSorter<KPFCandidate>());
				}

				for(size_t i = 0; i < in.signalNeutrHadrCands().size(); ++i)
				{
					KLV tmp;
					copyP4(in.signalNeutrHadrCands()[i].get()->p4(), tmp.p4);
					out.piZeroCandidates.push_back(tmp);
				}

				for(size_t i = 0; i < in.signalGammaCands().size(); ++i)
				{
					KPFCandidate outCandidate;
					KPackedPFCandidateProducer::fillPackedPFCandidate(*(in.signalGammaCands()[i].get()), outCandidate);
					out.gammaCandidates.push_back(outCandidate);
				}

			std::sort(out.chargedHadronCandidates.begin(), out.chargedHadronCandidates.end(), KLVSorter<KPFCandidate>());
			std::sort(out.piZeroCandidates.begin(), out.piZeroCandidates.end(), KLVSorter<KLV>());
			std::sort(out.gammaCandidates.begin(), out.gammaCandidates.end(), KLVSorter<KPFCandidate>());

			if (kshortinformation[names[0]]) fillMapOfTracksSV(in, out);
		}

		virtual void fillMapOfTracksSV(const SingleInputType &in, SingleOutputType &out)
		{
			unsigned short nTracks = in.signalChargedHadrCands().size() + in.isolationChargedHadrCands().size();
			//kshortTracksMap
			if (nTracks > 1)
			{
				std::vector<reco::TransientTrack> transientTracks;
				std::vector<reco::Track> bestTracks;
				KPFCandidates hadronCandidates;
				//TODO: store the map index:track
				for(size_t chargedPFCandidateIndex = 0; chargedPFCandidateIndex < in.signalChargedHadrCands().size(); ++chargedPFCandidateIndex)
				{
					const reco::Track* track = in.signalChargedHadrCands()[chargedPFCandidateIndex]->bestTrack();
					if (track)
					{
						KPFCandidate outCandidate;
						transientTracks.push_back(trackBuilder->build(track));
						bestTracks.push_back(*track);

						KPackedPFCandidateProducer::fillPackedPFCandidate(*(in.signalChargedHadrCands()[chargedPFCandidateIndex].get()), outCandidate);
						KTrackProducer::fillTrack(*(in.signalChargedHadrCands()[chargedPFCandidateIndex]->bestTrack()), outCandidate.bestTrack, *VertexCollection, trackBuilder.product());
						KTrackProducer::fillIPInfo(*(in.signalChargedHadrCands()[chargedPFCandidateIndex]->bestTrack()), outCandidate.bestTrack, *RefitVertices, trackBuilder.product());
						hadronCandidates.push_back(outCandidate);
					}
				}

				for(size_t chargedPFCandidateIndex = 0; chargedPFCandidateIndex < in.isolationChargedHadrCands().size(); ++chargedPFCandidateIndex)
				{
					const reco::Track* track = in.isolationChargedHadrCands()[chargedPFCandidateIndex]->bestTrack();
					if (track)
					{
						KPFCandidate outCandidate;
						transientTracks.push_back(trackBuilder->build(track));
						bestTracks.push_back(*track);

						KPackedPFCandidateProducer::fillPackedPFCandidate(*(in.isolationChargedHadrCands()[chargedPFCandidateIndex].get()), outCandidate);
						KTrackProducer::fillTrack(*(in.isolationChargedHadrCands()[chargedPFCandidateIndex]->bestTrack()), outCandidate.bestTrack, *VertexCollection, trackBuilder.product());
						KTrackProducer::fillIPInfo(*(in.isolationChargedHadrCands()[chargedPFCandidateIndex]->bestTrack()), outCandidate.bestTrack, *RefitVertices, trackBuilder.product());
						hadronCandidates.push_back(outCandidate);
					}
				}

				if (transientTracks.size() > 2)
				{
					TransientVertex theRecoVertex;
					bool useRefTracks = true; //temp
					const float piMass = 0.13957018;
					const float piMassSquared = pow(piMass, 2);
					KalmanVertexFitter theKalmanFitter(useRefTracks == 0 ? false : true);

					for(size_t trackIndex_1 = 0; trackIndex_1 < transientTracks.size() - 1; ++trackIndex_1)
						for(size_t trackIndex_2 = trackIndex_1 + 1; trackIndex_2 < transientTracks.size(); ++trackIndex_2)
						{
							if (transientTracks[trackIndex_1].charge() * transientTracks[trackIndex_2].charge() > 0.) continue;
							KKaonCandidate kaonCandidate;
							std::vector<reco::TransientTrack> transientTracksPair;
							transientTracksPair.push_back(transientTracks[trackIndex_1]);
							transientTracksPair.push_back(transientTracks[trackIndex_2]);

							kaonCandidate.isValid = true;
							kaonCandidate.firstTransTrack.indexOfTrackInColl = trackIndex_1; // Do not correspond to the indexes in taujet-charged collection
							kaonCandidate.secondTransTrack.indexOfTrackInColl = trackIndex_2; // Do not correspond to the indexes in taujet-charged collection
							KTrackProducer::fillTrack(bestTracks[trackIndex_1], kaonCandidate.firstTransTrack, *VertexCollection, trackBuilder.product());
							KTrackProducer::fillTrack(bestTracks[trackIndex_2], kaonCandidate.secondTransTrack, *VertexCollection, trackBuilder.product());
							kaonCandidate.firstTransPFCand = hadronCandidates[trackIndex_1];
							kaonCandidate.secondTransPFCand = hadronCandidates[trackIndex_2];
							kaonCandidate.firstTransTrack.impactPointTSCPIsValid = transientTracksPair[0].impactPointTSCP().isValid();
							kaonCandidate.secondTransTrack.impactPointTSCPIsValid = transientTracksPair[1].impactPointTSCP().isValid();
							if (!kaonCandidate.firstTransTrack.impactPointTSCPIsValid || !kaonCandidate.secondTransTrack.impactPointTSCPIsValid) continue;

							FreeTrajectoryState const & firstState = transientTracksPair[0].impactPointTSCP().theState();
							FreeTrajectoryState const & secondState = transientTracksPair[1].impactPointTSCP().theState();

							ClosestApproachInRPhi cApp;
							cApp.calculate(firstState, secondState);
							kaonCandidate.statusOfClosestApproachInRPhi = cApp.status(); //remove
							if (!cApp.status()) continue;

							float dca = std::abs(cApp.distance());
							kaonCandidate.distanceOfClosestApproach = dca;

							GlobalPoint cxPt = cApp.crossingPoint();
							kaonCandidate.POCA.SetXYZ(cxPt.x(), cxPt.y(), cxPt.z());

							// the tracks should at least point in the same quadrant
							TrajectoryStateClosestToPoint const & firstTSCP = transientTracks[trackIndex_1].trajectoryStateClosestToPoint(cxPt); // TODO::KAPPA
							TrajectoryStateClosestToPoint const & secondTSCP = transientTracks[trackIndex_2].trajectoryStateClosestToPoint(cxPt); // TODO::KAPPA
							if (!firstTSCP.isValid() || !secondTSCP.isValid()) continue;
							if (firstTSCP.momentum().dot(secondTSCP.momentum())  < 0) continue;

							//CartesianRMFLV initialFirstTSCP, initialSecondTSCP;
							kaonCandidate.initialFirstTSCP.SetCoordinates(firstTSCP.momentum().x(), firstTSCP.momentum().y(), firstTSCP.momentum().z(), piMassSquared);
							kaonCandidate.initialSecondTSCP.SetCoordinates(secondTSCP.momentum().x(), secondTSCP.momentum().y(), secondTSCP.momentum().z(), piMassSquared);
							{
								float totalE = sqrt(firstTSCP.momentum().mag2() + piMassSquared) + sqrt(secondTSCP.momentum().mag2() + piMassSquared);
								float totalPSq = (firstTSCP.momentum() + secondTSCP.momentum()).mag2();
								kaonCandidate.pionMass = sqrt(pow(totalE, 2) - totalPSq);
							}

							TransientVertex sv = theKalmanFitter.vertex(transientTracksPair);
							if (sv.isValid())
								KVertexProducer::fillVertex(sv, kaonCandidate.secondaryVertex);
							else continue;

							// Variables needef for significance
								reco::Vertex theVtx = sv; // Artus
								GlobalPoint vtxPos(theVtx.x(), theVtx.y(), theVtx.z()); // Artus
								reco::Vertex referencePV = VertexCollection->at(KVertexSummaryProducer::getValidVertexIndex(*VertexCollection)); // Artus. TODO: check that KVertex stores the same variable
								math::XYZPoint referencePosBS(BeamSpot->position());
								math::XYZPoint referencePosPV(referencePV.position());
									//kaonCandidate.refPosBS(BeamSpot->position()); //temp for checks
									//kaonCandidate.refPosPV(referencePV.position()); //temp for checks
									kaonCandidate.referencePosBS = referencePosBS; //temp
									kaonCandidate.referencePosPV = referencePosPV; //temp
								//TODO: typedef  ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3> >
								SMatrixSym3D totalCovBS = BeamSpot->rotatedCovariance3D() + theVtx.covariance();
								SMatrixSym3D totalCovPV = referencePV.covariance() + theVtx.covariance(); // TODO::KAPPA
									kaonCandidate.totalCovBS = totalCovBS; //temp for checks
									kaonCandidate.totalCovPV = totalCovPV; //temp for checks

							// Significance
								// Move to Artus
									// 2D decay significance
										ROOT::Math::SVector<double, 3> distVecXYBS(vtxPos.x() - referencePosBS.x(), vtxPos.y() - referencePosBS.y(), 0.);
										ROOT::Math::SVector<double, 3> distVecXYPV(vtxPos.x() - referencePosPV.x(), vtxPos.y() - referencePosPV.y(), 0.);
										kaonCandidate.distMagXYBS = ROOT::Math::Mag(distVecXYBS);
										kaonCandidate.distMagXYPV = ROOT::Math::Mag(distVecXYPV);
										kaonCandidate.sigmaDistMagXYBS  = sqrt(ROOT::Math::Similarity(totalCovBS, distVecXYBS)) / ROOT::Math::Mag(distVecXYBS);
										kaonCandidate.sigmaDistMagXYPV  = sqrt(ROOT::Math::Similarity(totalCovPV, distVecXYPV)) / ROOT::Math::Mag(distVecXYPV);
									// 3D decay significance
										ROOT::Math::SVector<double, 3> distVecXYZBS(vtxPos.x() - referencePosBS.x(), vtxPos.y() - referencePosBS.y(), vtxPos.z() - referencePosBS.z());
										ROOT::Math::SVector<double, 3> distVecXYZPV(vtxPos.x() - referencePosPV.x(), vtxPos.y() - referencePosPV.y(), vtxPos.z() - referencePosPV.z());
										kaonCandidate.distMagXYZBS = ROOT::Math::Mag(distVecXYZBS);
										kaonCandidate.distMagXYZPV = ROOT::Math::Mag(distVecXYZPV);
										kaonCandidate.sigmaDistMagXYZBS = sqrt(ROOT::Math::Similarity(totalCovBS, distVecXYZBS)) / ROOT::Math::Mag(distVecXYZBS);;
										kaonCandidate.sigmaDistMagXYZPV = sqrt(ROOT::Math::Similarity(totalCovPV, distVecXYZPV)) / ROOT::Math::Mag(distVecXYZPV);;

							// Correct the momentum of pions with respect to the refitted SV
								std::auto_ptr<TrajectoryStateClosestToPoint> trajFirst, trajSecond;
								std::vector<reco::TransientTrack> theRefTracks;
								if (sv.hasRefittedTracks())
									theRefTracks = sv.refittedTracks(); // TODO: check that sequence of returned objects is preserved

								if (theRefTracks.size() > 1)
								{
									trajFirst.reset(new TrajectoryStateClosestToPoint(theRefTracks[0].trajectoryStateClosestToPoint(vtxPos)));
									trajSecond.reset(new TrajectoryStateClosestToPoint(theRefTracks[1].trajectoryStateClosestToPoint(vtxPos)));
								}
								else
								{
									trajFirst.reset(new TrajectoryStateClosestToPoint(transientTracksPair[0].trajectoryStateClosestToPoint(vtxPos)));
									trajSecond.reset(new TrajectoryStateClosestToPoint(transientTracksPair[0].trajectoryStateClosestToPoint(vtxPos)));
								}
								if (trajFirst.get() == 0 || trajSecond.get() == 0 || !trajFirst->isValid() || !trajSecond->isValid())
								{
									std::cout << "TrajectoryStateClosestToPoint was invalid";
									continue;
								}

							// Calculate the 4-momentums
								float piFirstE = sqrt(trajFirst->momentum().mag2() + piMassSquared);
								float piSecondE = sqrt(trajSecond->momentum().mag2() + piMassSquared);

								CartesianRMFLV firstPiMomentumClosestToSV, secondPiMomentumClosestToSV;
								firstPiMomentumClosestToSV.SetCoordinates(trajFirst->momentum().x(), trajFirst->momentum().y(), trajFirst->momentum().z(), piFirstE);
								secondPiMomentumClosestToSV.SetCoordinates(trajSecond->momentum().x(), trajSecond->momentum().y(), trajSecond->momentum().z(), piSecondE);
								CartesianRMFLV totalPiMomentumClosestToSV(firstPiMomentumClosestToSV + secondPiMomentumClosestToSV);

								kaonCandidate.firstPiMomentumClosestToSV = firstPiMomentumClosestToSV;
								kaonCandidate.secondPiMomentumClosestToSV = secondPiMomentumClosestToSV;
								kaonCandidate.totalPiMomentumClosestToSV = totalPiMomentumClosestToSV;
								kaonCandidate.kMass = totalPiMomentumClosestToSV.mass();

							//Move to Artus
								// 2D pointing angle
									float dxBS = theVtx.x() - referencePosBS.x(), dyBS = theVtx.y() - referencePosBS.y(), pxBS = totalPiMomentumClosestToSV.x(), pyBS = totalPiMomentumClosestToSV.y();
									float dxPV = theVtx.x() - referencePosPV.x(), dyPV = theVtx.y() - referencePosPV.y(), pxPV = totalPiMomentumClosestToSV.x(), pyPV = totalPiMomentumClosestToSV.y();
									kaonCandidate.angleXYBS = (dxBS * pxBS + dyBS * pyBS) / (sqrt(dxBS * dxBS + dyBS * dyBS) * sqrt(pxBS * pxBS + pyBS * pyBS));
									kaonCandidate.angleXYPV = (dxPV * pxPV + dyPV * pyPV) / (sqrt(dxPV * dxPV + dyPV * dyPV) * sqrt(pxPV * pxPV + pyPV * pyPV));
								// 3D pointing angle
									float dzBS = theVtx.z() - referencePosBS.z(), pz = totalPiMomentumClosestToSV.z();
									float dzPV = theVtx.z() - referencePosPV.z();
									kaonCandidate.angleXYZPS = (dxBS * pxBS + dyBS * pyBS + dzBS * pz) / (sqrt(dxBS * dxBS + dyBS * dyBS + dzBS * dzBS) * sqrt(pxBS * pxBS + pyBS * pyBS + pz * pz));
									kaonCandidate.angleXYZPV = (dxPV * pxPV + dyPV * pyPV + dzPV * pz) / (sqrt(dxPV * dxPV + dyPV * dyPV + dzPV * dzPV) * sqrt(pxPV * pxPV + pyPV * pyPV + pz * pz));

							// Write down the object
							out.kshortCandidates.push_back(kaonCandidate);
						}

					// https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/RecoVertex/VertexPrimitives/interface/TransientVertex.h

				}
				else
					edm::LogInfo("fillMapOfTracksSV") <<  "transientTracks.size() !> 2\n";
			}
			else
				edm::LogInfo("fillMapOfTracksSV") <<  "nTracks !> 1\n";
		}

		virtual void fillTemporaryPVandBSVariables(const SingleInputType &in, SingleOutputType &out)
		{
			out.referencePosBS = BeamSpot->position();
			KVertexProducer::fillVertex(VertexCollection->at(KVertexSummaryProducer::getValidVertexIndex(*VertexCollection)), out.referencePV);
		}

		virtual void fillSecondaryVertex(const SingleInputType &in, SingleOutputType &out)
		{
			// https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/DataFormats/TauReco/interface/PFTau.h#L34-L54
			if ((in.decayMode() >= reco::PFTau::hadronicDecayMode::kThreeProng0PiZero) &&
			    (in.signalChargedHadrCands().size() > 2))
			{
				// refit SV since in.secondaryVertexPos() is empty
				// https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/DataFormats/PatCandidates/interface/Tau.h#L325

				std::vector<reco::TransientTrack> transientTracks;
				for(size_t chargedPFCandidateIndex = 0; chargedPFCandidateIndex < in.signalChargedHadrCands().size(); ++chargedPFCandidateIndex)
				{
					const reco::Track* track = in.signalChargedHadrCands()[chargedPFCandidateIndex]->bestTrack();
					if (track)
					{
						transientTracks.push_back(trackBuilder->build(track));
					}
				}
				if (transientTracks.size() > 2)
				{
					AdaptiveVertexFitter adaptiveVertexFitter;
					adaptiveVertexFitter.setWeightThreshold(0.001);

					// https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/RecoVertex/VertexPrimitives/interface/TransientVertex.h
					TransientVertex sv = adaptiveVertexFitter.vertex(transientTracks, *BeamSpot); // TODO: add beam spot
					if (sv.isValid())
					{
						KVertexProducer::fillVertex(sv, out.sv);
					}
				}
			}
		}

	public:

		KPatTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
			KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
			BeamSpotSource(cfg.getParameter<edm::InputTag>("offlineBeamSpot")),
			VertexCollectionSource(cfg.getParameter<edm::InputTag>("vertexcollection")),
			RefitVerticesSource(cfg.getParameter<edm::InputTag>("refitvertexcollection")),
			_lumi_tree_pointer(_lumi_tree)
		{
			this->tokenBeamSpot = consumescollector.consumes<reco::BeamSpot>(BeamSpotSource);
			this->tokenVertexCollection = consumescollector.consumes<reco::VertexCollection>(VertexCollectionSource);
			this->tokenRefitVertices = consumescollector.consumes<RefitVertexCollection>(RefitVerticesSource);

			const edm::ParameterSet &psBase = this->psBase;
			names = psBase.getParameterNamesForType<edm::ParameterSet>();
			if(names.size() != 1)
			{
				std::cout << "Currently the PatTau Producer only supports one PSet" << std::endl;
				assert(false);
			}

			for(size_t i = 0; i < names.size(); ++i)
			{
				discriminatorMap[names[i]] = new KTauMetadata();
				_lumi_tree_pointer->Bronch(names[i].c_str(), "KTauMetadata", &discriminatorMap[names[i]]);

				const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);

				kshortinformation[names[i]] =  pset.getUntrackedParameter<bool>("kshortinformation", false);
				preselectionDiscr[names[i]] = pset.getParameter< std::vector<std::string> >("preselectOnDiscriminators");
				binaryDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrWhitelist");
				binaryDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrBlacklist");
				floatDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrWhitelist");
				extrafloatDiscrlist[names[i]] = pset.getUntrackedParameter< std::vector<std::string> >("extrafloatDiscrlist", std::vector<std::string>(0) );
				#if (CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION < 21) || (CMSSW_MAJOR_VERSION < 8 )
					if (extrafloatDiscrlist[names[i]].size() > 0)
						std::cout << "Warining: extrafloatDiscrlist only available in CMSSW_8_0_21 or new" << std::endl;
				#endif
				floatDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrBlacklist");
			}
		}

		static const std::string getLabel() { return "PatTaus"; }

		virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
		{
			setup.get<TransientTrackRecord>().get("TransientTrackBuilder", trackBuilder);
			return true;
		}


		virtual void fillProduct(const InputType &in, OutputType &out,
								const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
		{
			edm::InputTag beamSpotSource = pset.getParameter<edm::InputTag>("beamSpotSource");
			cEvent->getByLabel(beamSpotSource, BeamSpot);

			cEvent->getByToken(this->tokenRefitVertices, this->RefitVertices);
			// Continue normally
			KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>::fillProduct(in, out, name, tag, pset);
		}

		virtual bool acceptSingle(const SingleInputType &in) override
		{
			// propagate the selection on minPt/maxEta
			bool acceptTau = KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>::acceptSingle(in);

			// reject taus with a charge different from +/- 1
			acceptTau = acceptTau && (in.charge() == 1 || in.charge() == -1);

			for(auto discriminator: preselectionDiscr[names[0]])
			{
				if ( !in.isTauIDAvailable(discriminator) )
				{
					std::cout << "Configured Tau preselection discriminator " << discriminator << " is not available. Available discriminators are: " << std::endl;
					for(auto availableDiscriminator : in.tauIDs())
						std::cout << availableDiscriminator.first << std::endl;
				}
				acceptTau = acceptTau && (in.tauID(discriminator) > 0.5);
			}
			return acceptTau;
		}

		virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
		{
			copyP4(in, out.p4);
			// hash of pointer as Id
			out.internalId = hasher(&in);
			fillChargeAndFlavour(in, out);
			out.tauKey = createTauHash<pat::Tau>(in);
			fillDiscriminators(in, out);
			if (in.isPFTau())
				KTauProducer::fillPFCandidates(in, out);
			else
				KPatTauProducer::fillPFCandidates(in, out);
			fillSecondaryVertex(in, out);
			fillTemporaryPVandBSVariables(in, out);
		}

		virtual void onFirstObject(const SingleInputType &in, SingleOutputType &out) override
		{
			if (this->verbosity > 0 && !in.isPFTau())
				std::cout << "Warning: pat::Tau has not been made from PFTau. emFraction and some PFCandidates will not be filled properly" << std::endl;

			// Write out discriminators
			// Discriminators are saved as floats in the pat::Tau.
			// The black/whitelisting mechanism is used to decide if a discriminato is used as binary or float.
			// The threshold between these two is 0.5
			out.binaryDiscriminators = 0;
			n_float_dict = 0;
			out.floatDiscriminators = std::vector<float>(0); // Will be resized in each event

			const std::vector<std::pair<std::string, float>> tauIDs = in.tauIDs();
			for(size_t i = 0; i < names.size(); ++i)
			{
				for(auto tauID : tauIDs)
				{
					if( KBaseProducer::regexMatch(tauID.first, binaryDiscrWhitelist[names[i]], binaryDiscrBlacklist[names[i]])) //regexmatch for binary discriminators
					{
						discriminatorMap[names[i]]->binaryDiscriminatorNames.push_back(tauID.first);
						if (this->verbosity > 0)
							std::cout << "Binary tau discriminator " << ": " << tauID.first << std::endl;
					}

					if( KBaseProducer::regexMatch(tauID.first, floatDiscrWhitelist[names[i]], floatDiscrBlacklist[names[i]])) //regexmatch for float discriminators
					{
					        realTauIdfloatmap[names[i]][tauID.first] = discriminatorMap[names[i]]->floatDiscriminatorNames.size();
						discriminatorMap[names[i]]->floatDiscriminatorNames.push_back(tauID.first);
						if (this->verbosity > 0)
							std::cout << "Float tau discriminator " << ": " << tauID.first << std::endl;
					}
				}

				#if (CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0)
					for (auto extrafloatDiscr : extrafloatDiscrlist[names[i]])
					{
						EXTRATAUFLOATS add_value = string_to_extraTaufloats(extrafloatDiscr);
						if (add_value != EXTRATAUFLOATS::UNKNOWN)
						{
							extraTaufloatmap[names[i]][add_value] = discriminatorMap[names[i]]->floatDiscriminatorNames.size();
							discriminatorMap[names[i]]->floatDiscriminatorNames.push_back(extrafloatDiscr);
						}
					}
				#endif

				checkMapsize(discriminatorMap[names[i]]->floatDiscriminatorNames, "float Discriminators");
				checkMapsize(discriminatorMap[names[i]]->binaryDiscriminatorNames, "binary Discriminators");
				n_float_dict += discriminatorMap[names[i]]->floatDiscriminatorNames.size();
			}
		}

	private:

		void checkMapsize(const std::vector<std::string> &map, const std::string &title)
		{
			if(map.size() > 64)
			{
				std::cout << title << " contains too many Elements(" << map.size() << ", max is 64" << std::endl;
				exit(1);
			}
		}

		#if (CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0)
			TauIdMVAAuxiliaries clusterVariables_;

			enum class EXTRATAUFLOATS : int
			{
				UNKNOWN = -1, decayDistX = 0, decayDistY = 1, decayDistZ = 2, decayDistM = 3,
				nPhoton = 4, ptWeightedDetaStrip = 5, ptWeightedDphiStrip = 6, ptWeightedDrSignal = 7,
				ptWeightedDrIsolation = 8, leadingTrackChi2 = 9, eRatio = 10
			};

			EXTRATAUFLOATS string_to_extraTaufloats(std::string in_string)
			{
				if      (in_string == "decayDistX") return EXTRATAUFLOATS::decayDistX;
				else if (in_string == "decayDistY") return EXTRATAUFLOATS::decayDistY;
				else if (in_string == "decayDistZ") return EXTRATAUFLOATS::decayDistZ;
				else if (in_string == "decayDistM") return EXTRATAUFLOATS::decayDistM;
				else if (in_string == "nPhoton") return EXTRATAUFLOATS::nPhoton;
				else if (in_string == "ptWeightedDetaStrip") return EXTRATAUFLOATS::ptWeightedDetaStrip;
				else if (in_string == "ptWeightedDphiStrip") return EXTRATAUFLOATS::ptWeightedDphiStrip;
				else if (in_string == "ptWeightedDrSignal") return EXTRATAUFLOATS::ptWeightedDrSignal;
				else if (in_string == "ptWeightedDrIsolation") return EXTRATAUFLOATS::ptWeightedDrIsolation;
				else if (in_string == "leadingTrackChi2") return EXTRATAUFLOATS::leadingTrackChi2;
				else if (in_string == "eRatio") return EXTRATAUFLOATS::eRatio;
				std::cout<<"Warning: "<<in_string <<" is not implemented so far !!!!!"<<std::endl;
				return EXTRATAUFLOATS::UNKNOWN;
			}

			std::map<std::string, std::map< EXTRATAUFLOATS, int > > extraTaufloatmap;
		#endif
		std::map<std::string, std::vector<std::string> > preselectionDiscr;
		std::map<std::string, std::vector<std::string> > binaryDiscrWhitelist, binaryDiscrBlacklist, floatDiscrWhitelist, floatDiscrBlacklist, extrafloatDiscrlist;
		std::map<std::string, std::map< std::string, int > > realTauIdfloatmap;
		std::map<std::string, KTauMetadata *> discriminatorMap;
		std::map<std::string, bool> kshortinformation;
		//std::map<unsigned short, unsigned short> kshortTracksMap;


		std::vector<std::string> names;
		boost::hash<const pat::Tau*> hasher;
		int n_float_dict;

		edm::Handle<reco::BeamSpot> BeamSpot;
		edm::Handle<reco::VertexCollection> VertexCollection;
		edm::Handle<RefitVertexCollection> RefitVertices;

		edm::InputTag BeamSpotSource;
		edm::InputTag VertexCollectionSource;
		edm::InputTag RefitVerticesSource;

		edm::EDGetTokenT<reco::VertexCollection> tokenVertexCollection;
		edm::EDGetTokenT<reco::BeamSpot> tokenBeamSpot;
		edm::EDGetTokenT<RefitVertexCollection> tokenRefitVertices;

		edm::ESHandle<TransientTrackBuilder> trackBuilder;

		TTree* _lumi_tree_pointer;
};

#endif
