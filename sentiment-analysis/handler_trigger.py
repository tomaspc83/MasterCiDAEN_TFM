import boto3, json, os

sns_client = boto3.client('sns', region_name=os.environ['REGION'])
topic_arn = os.environ['TOPIC_ARN']

def trigger_process(event, context):
    sns_client.publish(TopicArn=topic_arn,
                       Subject='EXECUTE_PROCESS',
                       Message='Execute COVID sentiment analysis'
                       )
    
    body = {
        "message": "Function executed successfully!",
        "input": event
    }
    
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    
    return response

