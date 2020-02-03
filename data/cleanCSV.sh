#!/bin/bash
cp $1 ${1}.original
sed -i 's#\([^,]\+\),v,#F,#g' $1
sed -i 's#\([^,]\+\),\^,#R,#g' $1
grep -v "(arrival)" $1 > ${1}_clean
mv ${1}_clean $1
# perl -0777 -pe 's/\n([RF])/@\1/g' $1
perl -0777 -i.perl -pe 's/\n([RF])/@\1/g' $1
sed -i 's#^Path[ ]\+[0-9]\+,\([^,]\+\,[^,]\+\),#Path \1 #g' $1
awk '!seen[$2]++' $1 > unique_$1
mv unique_$1 $1
sed -i 's#Path[ ]\+\([^ ]\+\)[ ]\+#Path 0,\1,#g ; s#@#\n#g' $1
