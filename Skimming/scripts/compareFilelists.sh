# Helper scipt to compare filelists
# adjust file paths to your needs
# Argument 1 and 2 are used to specify the path, e.g. "7TeV" and "Data"
base_folder=$CMSSW_BASE/src/Kappa/Skimming/higgsTauTau/
newfolder=new
oldfolder=samples

cat $base_folder/$newfolder/$1/$2.conf | grep -v dataset | grep -v Advanced | cut -d':' -f 2 | sort > $1-$2.new
cat $base_folder/$oldfolder/$1/$2.conf | grep -v dataset | grep -v Advanced | cut -d':' -f 2 | sort > $1-$2.old
diff -s $1-$2.new $1-$2.old 
rm $1-$2.new
rm $1-$2.old

cat $base_folder/$newfolder/$1/$2.conf | grep -v dataset | grep -v Advanced | cut -d':' -f 1 | sort > nicknames.new
a=$(cat nicknames.new | uniq -u | wc -l)
b=$(cat nicknames.new | wc -l)
rm nicknames.new
if [ $a -eq $b ] 
	then
	echo "Pass"
	else
	echo "Duplicate nicknames found! Change the make_nickname() function in registerDatasetsHelper.py so that the nicknames are unique."
fi

