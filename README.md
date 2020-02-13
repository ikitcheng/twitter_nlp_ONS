# Twitter NLP Project:

This repo contains tools to pull data from Twitter and analyse tweets according to the metadata contained with them. We have put together tools which have enabled a pipeline to execute NLP sentiment analysis on the data obtained Twitter, as well as providing visualization amongst out findings, this includes user group classification, topic modelling & wordclouds.


## Breakdown of repository:

- Scraper:
  - Scraper script is set up to automate the continuous pull of twitter data containing specified hashtags; limited to the last 7 days
  - Scraper can be extended to pull tweets containing any tweet attribute
  - User config file must be provided to authenticate against the Twitter API
- Cleaner:
  - Clean twitter metadata
- FeX:
  - Feature Extraction
- WordCloudGen:
  - Word Cloud Generator
- Classifier:
  - User Classification
- GeoTagger
  - Used to determine geo-spatial sentiment analysis / region based
