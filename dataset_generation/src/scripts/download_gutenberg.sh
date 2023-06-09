mkdir -p $1
chmod -R 777 $1
# generated collection
rsync -av --del --include='*.txt.utf8' --include='*/' --exclude='*' ftp@ftp.ibiblio.org::gutenberg-epub $1
cd $1 || exit
# moves txt files to root directory
find . -name *.utf8 -exec mv {}  .  \;
## removes subdirectories
find . -type d -delete
mkdir -p tmp
chmod -R 777 tmp
# main collection
rsync -av --del --include='*.txt' --include='*/' --exclude='*' ftp.ibiblio.org::gutenberg tmp
cd tmp || exit
rm donate-howto.txt
# moves txt files to $1
find -name "*.txt" -exec mv -t ../ {} +
echo "removed files from tmp"
cd ../ || exit
rm -rf tmp