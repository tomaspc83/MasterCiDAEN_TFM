import tweepy, json, boto3, re, os

user_id = os.environ['USER_ID']
pass_key = os.environ['PASS_KEY']

access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

# CONFIGURACION AUTENTICACIÓN TWEETER 
auth = tweepy.OAuthHandler(user_id, pass_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# CONFIGURACION ACCESO SQS
sqs = boto3.client('sqs', region_name=os.environ['REGION'])
queue_url = os.environ['QUEUE_URL']

key_words = os.environ['KEY_WORDS']

#geocode='40.4165000,-3.7025600,700km'
def get_tweets(event, context):
    covid_tweets = api.search(key_words, lang='es', result_type='recent', count=100, include_entities=False)

    for tweet in covid_tweets:
        tweet_removed = False
        
        try:
            status = api.get_status(tweet.id, tweet_mode="extended")
        except:
            tweet_removed = True
            
        if not tweet_removed:
            
            tweet_text = ''
    
            try:
                tweet_text = status.retweeted_status.full_text
    
            except AttributeError:  # Not a Retweet
                tweet_text = status.full_text
    
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody='{}{}'.format(tweet.id, remove_url(tweet_text))
            )
            
            print('Tweet añadido a la cola:', tweet_text)
            
        else:
            print('El tweet fue eliminado. No ha sido posible leerlo.')
            

def remove_url(txt):
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())