import boto3
import json
import time
import dateutil.parser

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    
    processed = False
    DYNAMODB_TABLE = "DEVOPS_SES_DELIVERIES"
    
    DDBtable = boto3.resource('dynamodb').Table(DYNAMODB_TABLE)
    
    # Generic SNS headers
    SnsMessageId = event['Records'][0]['Sns']['MessageId']
    SnsPublishTime = event['Records'][0]['Sns']['Timestamp']
    SnsTopicArn = event['Records'][0]['Sns']['TopicArn']
    SnsMessage = event['Records'][0]['Sns']['Message']
    
    print("Read SNS Message with ID " + SnsMessageId + " published at " + SnsPublishTime)
    
    now = time.strftime("%c")
    LambdaReceiveTime = now;
    
    # SES specific fields
    SESjson = json.loads(SnsMessage)
    sesNotificationType = SESjson['notificationType']
    sesMessageId = SESjson['mail']['messageId']
    sesTimestamp = SESjson['mail']['timestamp']
    sender = SESjson['mail']['source']
    
    print("Processing an SES " + sesNotificationType + " with mID " + sesMessageId )
    
    if (sesNotificationType == "Delivery"):
        print "Processing SES delivery messsage"
        
        reportingMTA = SESjson['delivery']['reportingMTA']
        deliveryRecipients = SESjson['delivery']['recipients']
        smtpResponse = SESjson['delivery']['smtpResponse']
        deliveryTimestamp = SESjson['delivery']['timestamp']
        processingTime = SESjson['delivery']['processingTimeMillis']
        
        # there can be multiple recipients but the SMTPresponse is the same for each
        for recipient in deliveryRecipients:
            recipientEmailAddress = recipient
            
            print("Delivery recipient: " + recipientEmailAddress )
            
            sesTimestamp_parsed = dateutil.parser.parse(sesTimestamp)
            sesTimestamp_seconds = sesTimestamp_parsed.strftime('%s')
            
            deliveryTimestamp_parsed = dateutil.parser.parse(deliveryTimestamp)
            deliveryTimestamp_seconds = deliveryTimestamp_parsed.strftime('%s')
            
            # Add entry to DB for this recipient
            Item={
                'recipientAddress': recipientEmailAddress,
                'sesMessageId': sesMessageId,
                'sesTimestamp': long(sesTimestamp_seconds),
                'deliveryTimestamp': long(deliveryTimestamp_seconds),
                'processingTime': long(processingTime),
                'reportingMTA': reportingMTA,
                'smtpResponse': smtpResponse,
                'sender': sender.lower()
            }
            
            response = DDBtable.put_item(Item=Item)
            print("PutItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))
            
            processed = True
        
    else:
        print("Unhandled notification type: " +  sesNotificationType)       
    
    return processed
