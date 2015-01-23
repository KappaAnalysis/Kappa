# Script to update the author information in C++ and python files
# It replaces the current author information (recognized by //- or #-#) with
# the authors in git commits for each file separately.
# This makes a clear attribution and makes it easier to find people to ask for help.
# Usage in the Kappa folder:
# . update_authors.sh > AUTHORS
# IMPORTANT: Do not commit the changes done by this script unless you have changed
#            your git settings to name=root email=<root@github> !!!
# Otherwise the script will never work again in future.
MAPSTRING=""
MAPSTRING="$MAPSTRING;s/Fred-Markus Stober <bd105@ic1n991.localdomain>/Fred Stober <stober@cern.ch>/"
MAPSTRING="$MAPSTRING;s/Armin Burgmeier <Armin Burgmeier>/Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>/"
MAPSTRING="$MAPSTRING;s/Manuel Zeise <zeise@ekplx37.(none)>/Manuel Zeise <zeise@cern.ch>/"
MAPSTRING="$MAPSTRING;s/Raphael <Raphael.Friese@cern.ch>/Raphael Friese <Raphael.Friese@cern.ch>/"
MAPSTRING="$MAPSTRING;s/rfriese <raphael.friese@cern.ch>/Raphael Friese <Raphael.Friese@cern.ch>/"
MAPSTRING="$MAPSTRING;s/rfriese <rfriese>/Raphael Friese <Raphael.Friese@cern.ch>/"
MAPSTRING="$MAPSTRING;s/rfriese <rfriese@cern.ch>/Raphael Friese <Raphael.Friese@cern.ch>/"
MAPSTRING="$MAPSTRING;s/fcolombo <fabio.colombo@cern.ch>/Fabio Colombo <fabio.colombo@cern.ch>/"
MAPSTRING="$MAPSTRING;s/bkargoll <bastian.kargoll@cern.ch>/Bastian Kargoll <bastian.kargoll@cern.ch>/"
MAPSTRING="$MAPSTRING;s/Roger <roger.wolf@cern.ch>/Roger Wolf <roger.wolf@cern.ch>/"
MAPSTRING="$MAPSTRING;s/Yasmin <yasmin.anstruther@kit.edu>/Yasmin Anstruther <yasmin.anstruther@kit.edu>/"
MAPSTRING="$MAPSTRING;s/stefan <stefan.wayand@gmail.com>/Stefan Wayand <stefan.wayand@gmail.com>/"
MAPSTRING="$MAPSTRING;s/Thomas Müller <tmueller@ekp.uni-karlsruhe.de>/Thomas Mueller <tmuller@cern.ch>/"
MAPSTRING="$MAPSTRING;s/Georg <sieber@cern.ch>/Georg Sieber <sieber@cern.ch>/"

# exit if tmp file exists:
test -f tmp && echo "Please move your file 'tmp' as it will be overwritten!" >&2 && return

# C++ files
find | grep -e "\.h$" -e "\.hxx$" -e "\.cpp$" -e "\.cxx$" -e "\.cc$" | grep -v "classes.h" | grep -v "Kappa.h" | grep -v "KDebug.h" | while read FILE; do
(
	CYEAR=$(git log --follow $FILE | grep Date | tail -n 1 | sed -e 's/.* ..:..:.. \(....\) .*/\1'/)
cat << EOF
//- Copyright (c) $CYEAR - All Rights Reserved
EOF
	(
	git log --follow $FILE | grep Author | grep -v root | sort | uniq | sed -e 's@Author: @@' | while read AUTHOR; do
		echo -e "//-  * $AUTHOR" | sed -e "$MAPSTRING";
	done
	) | sort | uniq
echo
cat $FILE | grep -v "//-" | sed '/./,$!d'
) > tmp
cat tmp > $FILE
done

# python files
find | grep -e "\.py$" | while read FILE; do
(
cat $FILE | grep "#!"
cat $FILE | grep "# -\*-"
	CYEAR=$(git log --follow $FILE | grep Date | tail -n 1 | sed -e 's/.* ..:..:.. \(....\) .*/\1'/)
cat << EOF
#-# Copyright (c) $CYEAR - All Rights Reserved
EOF
	(
	git log --follow $FILE | grep Author | grep -v root | sort | uniq | sed -e 's@Author: @@' | while read AUTHOR; do
		echo -e "#-#   $AUTHOR" | sed -e "$MAPSTRING";
	done
	) | sort | uniq
echo
cat $FILE | grep -v "#!" | grep -v "# -\*-" | grep -v "#-#" | sed '/./,$!d'
) > tmp
cat tmp > $FILE
done

(
find | grep -e "\.h$" -e "\.hxx$" -e "\.cpp$" -e "\.cxx$" -e "\.cc$" | while read FILE; do
	git log --follow $FILE | grep Author | grep -v root | sort | uniq | sed -e 's@Author: @@' | while read AUTHOR; do
		echo "$AUTHOR" | sed -e "$MAPSTRING"
	done
done
) | sort | uniq

rm tmp