#ifndef KAPPA_LORENTZVECTOR_H
#define KAPPA_LORENTZVECTOR_H

#include <Math/PtEtaPhiE4D.h>
#include <Math/PtEtaPhiM4D.h>
#include <Math/LorentzVector.h>

#include <Math/Point3D.h>
#include <Math/MatrixRepresentationsStatic.h>

typedef ROOT::Math::PtEtaPhiM4D<float> RMDataLV_Store;
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> > RMDataLV;

typedef ROOT::Math::PtEtaPhiM4D<double> RMLV_Store;
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double> > RMLV;

typedef ROOT::Math::PositionVector3D<ROOT::Math::Cartesian3D<float> > RMPoint;

#ifdef KAPPA_STANDALONE_DICT
namespace ROOT
{
	namespace Math
	{
		template<unsigned int D>
		struct SymMatrixOffsets
		{
		protected:
			static RowOffsets<D> offsets;
		};
	};
};
#endif

#endif
