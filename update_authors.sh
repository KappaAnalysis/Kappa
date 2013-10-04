MAPSTRING=""
MAPSTRING="$MAPSTRING;s/Fred-Markus Stober <bd105@ic1n991.localdomain>/Fred Stober <stober@cern.ch>/"
MAPSTRING="$MAPSTRING;s/Armin Burgmeier <Armin Burgmeier>/Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>/"
MAPSTRING="$MAPSTRING;s/Manuel Zeise <zeise@ekplx37.(none)>/Manuel Zeise <zeise@cern.ch>/"

function asd() {
# C++ files
find | grep -e "\.h$" -e "\.hxx$" -e "\.cpp$" -e "\.cxx$" -e "\.cc$" | while read FILE; do
(
	CYEAR=$(git log $FILE | grep Date | tail -n 1 | sed -e 's/.* ..:..:.. \(....\) .*/\1'/)
cat << EOF
/* Copyright (c) $CYEAR - All Rights Reserved
EOF
	(
	git log $FILE | grep Author | sort | uniq | sed -e 's@Author: @@' | while read AUTHOR; do
		echo -e " *   $AUTHOR" | sed -e "$MAPSTRING";
	done
	) | sort | uniq
cat << EOF
 */

EOF
cat $FILE
) > tmp
mv tmp $FILE
done

# python files
find | grep -e "\.py$" | while read FILE; do
(
	CYEAR=$(git log $FILE | grep Date | tail -n 1 | sed -e 's/.* ..:..:.. \(....\) .*/\1'/)
cat << EOF
# Copyright (c) $CYEAR - All Rights Reserved
EOF
	(
	git log $FILE | grep Author | sort | uniq | sed -e 's@Author: @@' | while read AUTHOR; do
		echo -e "#   $AUTHOR" | sed -e "$MAPSTRING";
	done
	) | sort | uniq
cat << EOF
#

EOF
cat $FILE
) > tmp
mv tmp $FILE
done
}

(
find | grep -e "\.h$" -e "\.hxx$" -e "\.cpp$" -e "\.cxx$" -e "\.cc$" | while read FILE; do
	git log $FILE | grep Author | sort | uniq | sed -e 's@Author: @@' | while read AUTHOR; do
		echo $AUTHOR" | sed -e "$MAPSTRING"
	done
done
) | sort | uniq
