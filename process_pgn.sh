#!/bin/bash

if [[ -f data/.data_downloaded ]] then
    echo "Data already downloaded. remove data/.data_downloaded if you want to download the data again"e
    exit
fi

clear

set -x

rm urls.txt
touch urls.txt
seq 1300 1399 | xargs -n1 -P2 bash -c 'i=$0; url="https://theweekinchess.com/zips/twic${i}g.zip"; output="data/twic${i}g.zip"; echo -e "url = \"$url\"\noutput = \"$output\"" >> urls.txt'

curl -v -k -H 'Cache-Control: no-cache' --parallel --parallel-immediate --parallel-max 10 --config urls.txt

find . -type f -name "twic**.zip" -exec unzip -qq {} \;

find . -maxdepth 1 -type f -name "*.pgn" | while read -r file; do
    iconv -f "$(uchardet "$file")" -t UTF-8 "$file" > "$file.tmp"
    mv $file.tmp $file
done

mv *.pgn data/
rm -fdr data/*.zip
cat data/*.pgn > data/twic_full.pgn1
rm data/*.pgn
mv data/twic_full.pgn1 data/twic_full.pgn

touch data/.data_downloaded