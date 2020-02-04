#!/bin/bash

# nlad 04/02/2020

## declare hashtags variable
declare -a hashtags=("brexit" "brexitshambles" "brexiteve" "leave" "remain" "eu" "referendum" 
                  "ukref" "voteleave" "voteremain" "boris" "farage" "brexit50p" "brexiteers" "tory"
                  "labour" "gotbrexitdone" "getbrexitdone" "bluecollarbritain" "bluewall" "notmybrexit")

## time period to scrape
declare -a since=("2020-01-28" "2020-01-29" "2020-01-30" "2020-01-31" "2020-02-01" "2020-02-02" "2020-02-03")

declare -a until=("2020-01-29" "2020-01-30" "2020-01-31" "2020-02-01" "2020-02-02" "2020-02-03" "2020-02-04")

# get length of arrays
hashtaglength=${#hashtags[@]}
sincelength=${#since[@]}


for (( i=0; i<${sincelength}-5; i++ ));
do

  dir="${since[$i]}-${until[$i]}"
  mkdir -p scrape_data_${dir}

  # use for loop to read all values and indexes
  for (( j=0; j<${hashtaglength}-17; j++ ));
  do

    echo '---------------------------------------------'
    echo "scraping twitter for: #${hashtags[$j]}"
    echo $'--------------------------------------------- \n'
    python scrape.py -t ${hashtags[$j]} -s ${since[$i]} -u ${until[$i]} -f scrape_data_${dir}/${hashtags[$j]}.csv -c config.yaml
    echo $'\n---------------------------------------------'
    echo "scrape ${j} / ${hashtaglength} complete"
    echo $'--------------------------------------------- \n'

  done

done

echo "scrape complete!"
