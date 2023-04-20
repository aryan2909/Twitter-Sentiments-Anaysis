import tweepy
from textblob import TextBlob
from flask import Flask, jsonify, render_template, request
from textblob import TextBlob

app = Flask(__name__)

consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

# Initialize the API object
api = tweepy.API(auth, wait_on_rate_limit=True)

# api = tweepy.API(auth)

def get_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0:
        return 'positive'
    elif sentiment_score == 0:
        return 'neutral'
    else:
        return 'negative'

def get_sentiment_scores(tweets):
    scores = {
        'positive': 0,
        'neutral': 0,
        'negative': 0
    }
    for tweet in tweets:
        sentiment = get_sentiment(tweet.text)
        scores[sentiment] += 1
    return scores

def get_tweet_sentiment(tweet):
    # create TextBlob object of passed tweet text
    analysis = TextBlob(tweet)
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'
        
def get_sentiment_analysis(tweet_list):
    # create a list to store the sentiment of each tweet
    sentiment_list = []
    for tweet in tweet_list:
        # get the sentiment of the tweet and append it to the list
        sentiment = get_tweet_sentiment(tweet)
        sentiment_list.append(sentiment)
    return sentiment_list

def search_tweets(api, query, count=1000):
    tweets = api.search(q=query, count=count)
    return [tweet.text for tweet in tweets]



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # get the user input from the form
    query = request.form['query']
    count = int(request.form['count'])
    # search for tweets containing the query
    tweets = api.search_tweets(q=query, lang='en', count=count)
    # extract the text of each tweet
    tweet_texts = [tweet.text for tweet in tweets]
    # perform sentiment analysis on the tweet texts
    sentiment_list = get_sentiment_analysis(tweet_texts)
    # count the number of each sentiment
    positive_count = sentiment_list.count('positive')
    neutral_count = sentiment_list.count('neutral')
    negative_count = sentiment_list.count('negative')
    # render the results template with the sentiment counts
    return render_template('results.html', query=query, count=count, 
                           positive_count=positive_count, neutral_count=neutral_count, negative_count=negative_count)



@app.route('/search')
def search():
    query = request.args.get('q')
    tweets = api.search_tweets(q=query, count=1000)

    scores = get_sentiment_scores(tweets)
    return jsonify(scores)

if __name__ == '__main__':
    app.run(debug=True)
