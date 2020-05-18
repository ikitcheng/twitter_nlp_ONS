#!/bin/bash

# Twitter Scraping tool

# languages
lang="en"

# month by month
declare -a since=("2020-03-01" "2020-03-07" "2020-03-14" "2020-03-21" "2020-03-28")
declare -a until=("2020-03-07" "2020-03-14" "2020-03-21" "2020-03-28" "2020-03-31")
sincelength=${#since[@]}

limit="1000000"


home_dir=""

for (( i=0; i<${sincelength}; i++ ));
do

  # save the file to this path
  filename="twitter-covid-"${since[$i]}"-"${until[$i]}".csv"

  echo "Beginning scrape..."
  python ${home_dir}parallel-word-scrape.py -s ${since[$i]} -u ${until[$i]} -l ${lang} -i ${limit} -f ${filename}
  echo "Scrape complete!"

done

#compress_dir=""
#echo "Compress data..."
#tar -czvf ${compress_dir}february_test.tar.gz ${compress_dir}february_test/
#echo "Compress complete!"
