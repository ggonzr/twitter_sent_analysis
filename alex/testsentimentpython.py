from pandas.core.frame import DataFrame
import textblob            #to import
from textblob import TextBlob
import tweepy 
import json 
import pandas as pd
import re
import time
import csv

credentials_df = pd.read_csv('credentials.csv',header=None,names=['name','key'])

credentials_df

consumer_key = credentials_df.loc[credentials_df['name']=='consumer_key','key'].iloc[0]
consumer_secret = credentials_df.loc[credentials_df['name']=='consumer_secret','key'].iloc[0]
access_token = credentials_df.loc[credentials_df['name']=='access_token','key'].iloc[0]
access_token_secret = credentials_df.loc[credentials_df['name']=='access_secret','key'].iloc[0]


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)

# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#    print(tweet.text)

# Function created to extract coordinates from tweet if it has coordinate info
# Tweets tend to have null so important to run check
# Make sure to run this cell as it is used in a lot of different functions below

def extract_coordinates(row):
    if row['Tweet Coordinates']:
        return row['Tweet Coordinates']['coordinates']
    else:
        return None

# Function created to extract place such as city, state or country from tweet if it has place info
# Tweets tend to have null so important to run check
# Make sure to run this cell as it is used in a lot of different functions below

def extract_place(row):
    if row['Place Info']:
        return row['Place Info'].full_name
    else:
        return None

def remove_url(txt):
    """Replace URLs found in a text string with nothing 
    (i.e. it will remove the URL from the string).

    Parameters
    ----------
    txt : string
        A text string that you want to parse and remove urls.

    Returns
    -------
    The same txt string with url's removed.
    """

    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())
 
def replace_values(sentiment_df):
    for val in sentiment_df['polarity']:
        if (float(val)<0):
            sentiment_df['polarity'].replace(val, -1)
        elif (float(val)==0):
            sentiment_df['polarity'].replace(val, 0)
        else:
            sentiment_df['polarity'].replace(val, 1)
    #print("Sentiment polarity: ",sentiment_df)   
    sentiment_df.head()
    return sentiment_df

# username = 'ELTIEMPO'
max_tweets = 500
hagstags = "#Colombia OR #FARC OR #droga OR #Uribe OR #paramilitarismo OR #guerrilla OR #Guerra OR #Violencia OR #secuestro"
tweets = tweepy.Cursor(api.search,q=hagstags,count=100, lang="es",since="2018-04-03").items(max_tweets)

# Pulling information from tweets iterable object
# Add or remove tweet information you want in the below list comprehension
tweets_list = [[remove_url(tweet.text), tweet.created_at, tweet.id_str, tweet.user.screen_name, tweet.coordinates, tweet.place, tweet.retweet_count, tweet.favorite_count, tweet.lang, tweet.source, tweet.in_reply_to_status_id_str, tweet.in_reply_to_user_id_str, tweet.is_quote_status] for tweet in tweets]


# tweets_no_urls = [remove_url(tweet.text) for tweet in tweets]
# Creation of dataframe from tweets_list
# Add or remove columns as you remove tweet information
tweets_df1 = pd.DataFrame(tweets_list,columns=['Tweet Text', 'Tweet Datetime', 'Tweet Id', 'Twitter @ Name', 'Tweet Coordinates', 'Place Info', 'Retweets', 'Favorites', 'Language', 'Source', 'Replied Tweet Id', 'Replied Tweet User Id Str', 'Quote Status Bool'])
 
# Checks if there are coordinates attached to tweets, if so extracts them
tweets_df1['Tweet Coordinates'] = tweets_df1.apply(extract_coordinates,axis=1)
 
# Checks if there is place information available, if so extracts them
tweets_df1['Place Info'] = tweets_df1.apply(extract_place,axis=1)

# tweets_no_urls = [tweets_list[0][tweet] for tweet in tweets_list] 

tweets_no_urls = tweets_df1['Tweet Text']


sentiment_objects = [TextBlob(tweet) for tweet in tweets_no_urls]

# sentiment_objects[0].polarity, sentiment_objects[0]

sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]

# sentiment_values[0]

sentiment_df = pd.DataFrame(sentiment_values, columns=["polarity", "tweet"])

polarity_df=replace_values(sentiment_df)

tweets_df1.to_csv(r'datatest.csv', index = False, header=True, sep = ';', line_terminator = '', encoding = 'utf-8')
polarity_df.to_csv(r'datatest2.csv', index = False, header=True, sep = ';', line_terminator = '', encoding = 'utf-8')



