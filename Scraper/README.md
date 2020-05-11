# Real Time Scraper

`scrape.sh` is used to crawl through the public facing twitter endpoint and scrape tweets containing a set of specified hashtags.

The free twitter API allows scraping of up to 7 days in the past.


### Instructions:

1. `git clone` this repository and `cd ScrapingTwitterRealTime`


2. Create a `config.yaml` file containing your authentication to the Twitter API:


`consumerKey: XXXX`

`consumerSecret: XXXX`

`accessToken: XXXX`

`accessTokenSecret: XXXX`


3. Edit `scrape.sh` to include any hashtags you want to run


4. Create the executable: `chmod +x scrape.sh`


5. Run! `./scrape.sh` and view the results

