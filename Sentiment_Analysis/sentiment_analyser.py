from textblob import TextBlob
import pandas as pd
import textpreprocessing as tp
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ast 
import numpy as np

testimonial = TextBlob("Textblob is amazingly simple to use. What great fun!")

headers_for_basic_files = ["created_at", "id", "text", "entities", "source", 
                           "user.id", "user.screen_name", "user.location", 
                           "user.followers_count", "user.friends_count", 
                           "user.verified", "user.statuses_count", "geo", "coordinates",
                           "place_name", "user_location2", "retweet_count", 
                           "tweet_favorite_count", "tweet_favorited", "tweet_retweeted"]

class sentiment_analyser:
    def __init__(self, file_name, tweet_column_name):
        self.file_name = file_name
        self.tweet_column_name = tweet_column_name

        self.df = pd.read_csv(filepath_or_buffer = self.file_name, sep = ",", 
                              error_bad_lines=False)
        self.df.columns = headers_for_basic_files
        self.tweet_col = self.df[self.tweet_column_name]    
        
    def textblob_sentiment(self, text):
        return TextBlob(text).sentiment.subjectivity

    def nltk_sentiment(self, text):
        sid = SentimentIntensityAnalyzer()
        return sid.polarity_scores(text)["compound"]
    
   # def flair_sentiment(self, text):
        # this issue is that they've just trained their pre-trained model on the IMDB dataset!!!
     #   classifier = TextClassifier.load("en-sentiment")
      #  sentence = Sentence(text)
       # classifier.predict(sentence)
        #sentiment_polarity = ast.literal_eval(str(sentence.labels[0]).split(" ")[1])
        #return sentiment_polarity
        
    def aggregate_sentiment_analysis(self):
        
        sentiment_scores = []
        
        for i,tweet in enumerate(self.tweet_col.values):
            print(i)
            preprocessed_tweet = tp.clean_doc(tweet)
            mean_sentiment = np.mean([self.textblob_sentiment(preprocessed_tweet), 
                                      self.nltk_sentiment(preprocessed_tweet)])
                                      #self.flair_sentiment(preprocessed_tweet)])
            sentiment_scores.append(mean_sentiment)
        
        self.df["Sentiment Polarity"] = sentiment_scores
        
    
    
test = sentiment_analyser("twitter_nlp_ONS/ScrapingTwitterRealTime/datasets/scrape_data_2020-02-03-2020-02-04/brexit.csv", "text")
test.aggregate_sentiment_analysis()   

