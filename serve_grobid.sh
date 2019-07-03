# download GROBID if directory does not exist
if [ ! -d grobid-0.5.5 ]; then
  wget https://github.com/kermitt2/grobid/archive/0.5.5.zip
  unzip 0.5.5.zip
  rm 0.5.5.zip
fi

# run GROBID
cd grobid-0.5.5
./gradlew run