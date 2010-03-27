#include "../interface/KBaseProducer.h"
#include <TTree.h>
#include <boost/regex.hpp>
#include <boost/algorithm/string/regex.hpp>

bool KBaseProducer::onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
{
	return true;
}

bool KBaseProducer::onEvent(const edm::Event &event, const edm::EventSetup &setup)
{
	return true;
}

bool KBaseProducer::onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
{
	return true;
}

bool KBaseProducer::regexMatch(const std::string &in, const std::string &filter)
{
	if (verbosity > 2)
		std::cout << in << " ";
	try
	{
		boost::regex pattern(filter, boost::regex::icase | boost::regex::extended);
		if ((filter != "") && boost::regex_search(in, pattern))
		{
			if (verbosity > 2)
				std::cout << "matched" << std::endl;
			return true;
		}
	} catch (...)
	{
		std::cout << "Error while matching \"" << in << "\" against regular expression \"" << filter << "\"" << std::endl;
	}
	if (verbosity > 2)
		std::cout << "not matched" << std::endl;
	return false;
}

bool KBaseProducer::regexMatch(const std::string &in, const std::vector<std::string> &whitelist,
	const std::vector<std::string> &blacklist)
{
	bool accept = false;
	if (whitelist.size() == 0)
		accept = true;
	else
	{
		if (verbosity > 1)
			std::cout << "Whitelist matching..." << std::endl;
		for (size_t wIdx = 0; wIdx < whitelist.size(); ++wIdx)
			if (regexMatch(in, whitelist[wIdx]))
			{
				accept = true;
				break;
			}
	}
	if (accept && (blacklist.size() > 0))
	{
		if (verbosity > 1)
			std::cout << "Blacklist matching..." << std::endl;
		for (size_t bIdx = 0; bIdx < blacklist.size(); ++bIdx)
			if (regexMatch(in, blacklist[bIdx]))
			{
				accept = false;
				break;
			}
	}
	if (verbosity > 1)
		std::cout << in << " was " << ((accept) ? "" : "not ") << "accepted!" << std::endl;
	return accept;
}

std::string KBaseProducer::regexRename(std::string in, const std::vector<std::string> &patterns)
{
	if (verbosity > 1)
		std::cout << std::endl;
	for (unsigned int i = 0; i < patterns.size(); ++i)
	{
		std::vector<std::string> rename_tok;
		boost::algorithm::split_regex(rename_tok, patterns[i], boost::regex("( )?=>( )?"));
		if (rename_tok.size() != 2)
			continue;

		if (verbosity > 1)
			std::cout << "\t(" << i + 1 << "): " << rename_tok[0] << " => " << rename_tok[1] << std::endl;

		std::string tmp;
		boost::regex rx(rename_tok[0], boost::regex::icase | boost::regex::extended);
		boost::regex_replace(std::back_inserter(tmp), in.begin(), in.end(), rx,
			rename_tok[1], boost::match_default | boost::format_all);

		if ((verbosity == 1) && (in != tmp))
			std::cout << in << " => ";
		if (verbosity > 1)
			std::cout << "\t\t" << in << " => " << tmp << std::endl;

		in = tmp;
	}
	if (verbosity > 1)
		std::cout << "\t";
	return in;
}

bool KBaseProducer::fail(const std::ostream &s)
{
	return false;
}
