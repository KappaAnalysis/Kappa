#ifndef KDATAFORMAT_H
#define KDATAFORMAT_H

#define G__DICTIONARY
#include "../interface/KMetadata.h"
#include "../interface/KBasic.h"
#include "../interface/KLorentzVector.h"

namespace
{
	struct dictionary
	{

		RMDataLV_Store kappa_mdatalv_store;
		RMDataLV kappa_mdatalv;

		RMLV_Store kappa_mlv_store;
		RMLV kappa_mlv;



		KDataLV kappa_datalv;
		KDataLVs kappa_datalvs;

		KLV kappa_lv;
		KLVs kappa_lvs;

		KDataMET kappa_datamet;

		KDataJet kappa_datajet;
		KDataJets kappa_datajets;

		KDataTrack kappa_datatrack;
		KDataTracks kappa_datatracks;

		KParton kappa_parton;
		KPartons kappa_partons;


		KProvenance kappa_provenance;

		KLumiMetadata kappa_lumimetadata;
		KGenLumiMetadata kappa_genlumimetadata;

		KEventMetadata kappa_eventmetadata;
		KGenEventMetadata kappa_geneventmetadata;

	};
}

#endif
