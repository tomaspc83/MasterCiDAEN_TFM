import json
import datetime
import boto3, os
 
#Servicio DynamoDb
dynamodb_client = boto3.resource('dynamodb', region_name=os.environ['REGION'])

def compute_statistics(event, context):
    table = dynamodb_client.Table('tweets_statistics')
    
    for new_tweet in event['Records']:
        if new_tweet['eventName'] == 'INSERT':
            positive = 0
            negative = 0
            neutral = 0
            mixed = 0
            
            tweet_date = new_tweet['dynamodb']['NewImage']['tweet_date']['S']
            sentiment = new_tweet['dynamodb']['NewImage']['sentiment']['S']
            
            if sentiment == 'POSITIVE':
                positive += 1
            elif sentiment == 'NEGATIVE':
                negative += 1
            elif sentiment == 'NEUTRAL':
                neutral += 1
            else:
                mixed += 1
            
            response = table.update_item(
                Key={
                    'TweetDate': tweet_date,
                },
                
                UpdateExpression='ADD positive :val1, negative :val2, neutral :val3, mixed :val4',
                ExpressionAttributeValues={
                    ':val1': positive,
                    ':val2': negative,
                    ':val3': neutral,
                    ':val4': mixed
                }
            )   
            
            print('Tweet añadido a la estadística')