import json, boto3, os
from datetime import datetime
from decimal import Decimal

#Servicio DynamoDb
dynamodb_client = boto3.resource('dynamodb', region_name=os.environ['REGION'])

#Servicio Comprehend
comprehend = boto3.client('comprehend', region_name=os.environ['REGION'])

#Servicio CloudWatch
cloudwatch = boto3.client('cloudwatch', os.environ['REGION'])

def analyze_tweets(event, context):
    tweet_id = event['Records'][0]['body'][0:18]
    tweet_text = event['Records'][0]['body'][19:]

    response = comprehend.detect_sentiment(Text=tweet_text, LanguageCode='es')

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        sentiment = response['Sentiment']
        
        sent_pos = response['SentimentScore']['Positive']
        sent_neg = response['SentimentScore']['Negative']
        polarity = Decimal(sent_pos - sent_neg)

        table = dynamodb_client.Table('tweets')
        table.put_item(
            Item={
                'tweet_id': tweet_id,
                'tweet_text': tweet_text,
                'sentiment': sentiment,
                'polarity': polarity,
                'tweet_date': datetime.today().strftime("%d/%m/%Y")
                }
        )
        
        namespace = 'cidaen_TFM_tomas'
        dimension_sentiment = [
                {
                    'Name': 'TEST Sentiment Analysis',
                    'Value': 'TEST Polarity'
                }
        ]
        
        cloudwatch.put_metric_data(
            MetricData = [
                {
                    'MetricName': 'Co',
                    'Dimensions': dimension_sentiment,
                    'Unit': 'None',
                    'Timestamp': datetime(datetime.today().year, datetime.today().month, datetime.today().day),
                    'Value': polarity,
                },
            ],
            Namespace=namespace
        )
        
        print('Tweet añadido correctamente')
    else:
        print('No hay mensajes en la cola')