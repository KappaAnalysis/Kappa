/* Copyright (c) 2011 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 */

template<typename T>
void displayVector(std::ostream &os, const T &v, size_t n = 0)
{
	if (n == 0)
	{
		os << "Size: " << v.size() << std::endl;
		n = v.size();
	}
	n = std::min(n, v.size());
	for (typename T::const_iterator it = v.begin(); (it != v.end()) && (n != 0); ++it, --n)
		os << *it << " ";
	os << std::endl;
}
