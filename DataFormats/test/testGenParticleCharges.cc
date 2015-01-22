//- Copyright (c) 2013 - All Rights Reserved
//-  * Joram Berger <joram.berger@cern.ch>

// test the charge function of GenParticles
// compile with
// g++ testGenParticleCharges.cc $(root-config --cflags) $(root-config --ldflags --libs) -o testcharge
#include "DataFormats/interface/KBasic.h"
#include <iostream>

using namespace std;

int getid(int pid)
{
	unsigned int id = (pid < 0) ? -pid : pid;
	id = id | (3 << KGenParticleStatusPosition);
	if (pid < 0)
		id |= KGenParticleChargeMask;
	return id;
}

void test(int pdg, int truth = 0, string comment = "")
{
	KGenParticle p;
	p.pdgid = getid(pdg);
	cout << std::setw(7) << std::fixed << std::setprecision(2) << p.pdgId()
		 << ": c = " << std::setw(5) << p.charge()
		 << ", c3 =" << std::setw(3) << p.chargeTimesThree();
	if (p.chargeTimesThree() != truth)
		cout << " ERROR: should be: " << truth << " (" << (truth / 3.0) << ") " << comment;
	cout << endl;
}

int main()
{
	cout << "Empty:\n";
	test(0);

	cout << "Quarks:\n";
	test(1, -1);
	test(-1, +1);
	test(4, +2);
	test(-5, +1);
	test(-6, -2);

	cout << "Leptons:\n";
	test(13, -3);
	test(-13, +3);
	test(16);
	test(-14);

	cout << "Bosons:\n";
	test(22);
	test(23);
	test(24, +3);
	test(-21);
	test(-24, -3);

	cout << "Mesons:\n";
	test(111);
	test(-113);
	test(211, +3);
	test(-211, -3);
	test(-221);
	test(9000111);
	test(3000111);

	cout << "Baryons:\n";
	test(2212, +3);
	test(-2212, -3);
	test(2224, +6);
	test(-2224, -6);

	cout << "Exotics:\n";
	test(1103, -2);
	test(9331122, -6, "[OK, pentaquarks are not covered]");

	return 0;
}
