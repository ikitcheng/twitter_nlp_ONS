#!/bin/bash

## declare an array variable
declare -a array=("brexit" "brexiteve" "leave" "remain" "eu" "referendum" "ukref" "voteleave" "voteremain" "boris" "farage")

# get length of an array
arraylength=${#array[@]}

# use for loop to read all values and indexes
for (( i=0; i<${arraylength}; i++ ));
do
  echo "---------------------------------------------"
  echo "scraping twitter for: #${array[$i]}"
  echo "---------------------------------------------"
  echo ""
  echo "python scrape.py -t" ${array[$i]} "-f scrape_data/${array[$i]}.csv -c config.yaml" 
  python scrape.py -t ${array[$i]} -f scrape_data/${array[$i]}.csv -c config.yaml
  #echo "python scrape.py -t" ${array[$i]} "-f 31_Jan_2020_scrape_data/${array[$i]}.csv -c config.yaml" 
  #python 31_Jan_2020_scrape.py -t ${array[$i]} -f 31_Jan_2020_scrape_data/${array[$i]}.csv -c config.yaml
  echo "---------------------------------------------"
  echo "scrape ${i+1} / ${arraylength} complete"
  echo "---------------------------------------------"
  echo ""
done

echo "scrape complete!"
