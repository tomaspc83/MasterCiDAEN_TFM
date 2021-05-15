import tweepy, json, boto3

user_id = 'H6UFCAg0yfiYRjESSwdkMDQGC'
pass_key = 'iqiM2j0XvK8Q1WzgdmUTYCnUHfXDJ2fqcJvwkB56YEOVJOew9z'

access_token = '139041030-VCSNagPSbknNaoUxpoxFjHLUCDUbMdYlB9dXWXfl'
access_token_secret = 'gq4DYHBlHXJDQhc9pdBgOCG51L3UJnUwU0ZJpzcFMLPWI'

# CONFIGURACION AUTENTICACIÓN TWEETER
auth = tweepy.OAuthHandler(user_id, pass_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# CONFIGURACION ACCESO SQS
sqs = boto3.client('sqs', region_name='us-east-1')
queue_url = 'https://sqs.us-east-1.amazonaws.com/266474703085/new_tweets'

key_words = '#CORONAVIRUS OR #COVID OR #COVID-19 OR #SARS OR #SARS-CoV'

def lambda_handler(event, context):
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
            MessageBody='{}{}'.format(tweet.id, tweet_text)
            )
            print('Tweet añadido a la cola')
        else:
            print('El tweet fue eliminado. No ha sido posible leerlo.')