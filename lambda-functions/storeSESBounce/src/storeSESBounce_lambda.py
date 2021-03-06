import boto3
import json
import time
import dateutil.parser
import datetime
import calendar


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
    DYNAMODB_TABLE = "DEVOPS_SES_BOUNCES"

    DDBtable = boto3.resource('dynamodb').Table(DYNAMODB_TABLE)

    # Generic SNS headers
    SnsMessageId = event['Records'][0]['Sns']['MessageId']
    SnsPublishTime = event['Records'][0]['Sns']['Timestamp']
    SnsTopicArn = event['Records'][0]['Sns']['TopicArn']
    SnsMessage = event['Records'][0]['Sns']['Message']

    print("Read SNS Message with ID " + SnsMessageId + " published at " + SnsPublishTime)

    now = time.strftime("%c")
    LambdaReceiveTime = now

    # SES specific fields
    SESjson = json.loads(SnsMessage)
    sesNotificationType = SESjson['notificationType']

    if 'mail' in SESjson:
        sesMessageId = SESjson['mail']['messageId']
        sesTimestamp = SESjson['mail']['timestamp'] #the time the original message was sent
        sender = SESjson['mail']['source']

        print("Processing an SES " + sesNotificationType + " with mID " + sesMessageId)

        if (sesNotificationType == "Bounce"):
            print("Processing SES bounce messsage")

            try:
                reportingMTA = SESjson['bounce']['reportingMTA']
            except:
                print("No reportingMTA provided in bounce notification")
                print("Received event: " + json.dumps(event, indent=2))
                reportingMTA = "UNKNOWN"

            bounceType = SESjson['bounce']['bounceType']
            bounceRecipients = SESjson['bounce']['bouncedRecipients']
            bounceType = SESjson['bounce']['bounceType']
            bounceSubType = SESjson['bounce']['bounceSubType']
            bounceTimestamp = SESjson['bounce']['timestamp'] # the time at which the bounce was sent by the ISP

            # There can be a seperate bounce reason per recipient IF it's not a suppression bounce
            for recipient in bounceRecipients:
                try:
                    recipientEmailAddress = recipient['emailAddress']
                except:
                    print("No recipient email provided in bounce notification")
                    print("Received event: " + json.dumps(event, indent=2))
                    recipientEmailAddress = "UNKNOWN"

                try:
                    diagnosticCode = recipient['diagnosticCode']
                except:
                    print("No diagnosticCode provided in bounce notification")
                    print("Received event: " + json.dumps(event, indent=2))
                    diagnosticCode = "UNKNOWN"

                print("Bounced recipient: " + str(recipientEmailAddress) + " reason: " + str(diagnosticCode))

                sesTimestamp_parsed = dateutil.parser.parse(sesTimestamp)
                sesTimestamp_seconds = sesTimestamp_parsed.strftime('%s')

                bounceTimestamp_parsed = dateutil.parser.parse(bounceTimestamp)
                bounceTimestamp_seconds = bounceTimestamp_parsed.strftime('%s')

                # Set an expiry time for this record so we can use Dynamo TTLs to remove
                future = datetime.datetime.utcnow() + datetime.timedelta(days=120)
                expiry_ttl = calendar.timegm(future.timetuple())

                # Add entry to DB for this recipient
                Item={
                    'recipientAddress': recipientEmailAddress,
                    'sesMessageId': sesMessageId,
                    'sesTimestamp': int(sesTimestamp_seconds),
                    'bounceTimestamp': int(bounceTimestamp_seconds),
                    'reportingMTA': reportingMTA,
                    'diagnosticCode': diagnosticCode,
                    'bounceType': bounceType,
                    'bounceSubType': bounceSubType,
                    'sender': sender.lower(),
                    'expiry': int(expiry_ttl)
                }

                response = DDBtable.put_item(Item=Item)
                print("PutItem succeeded:")
                print(json.dumps(response, indent=4, cls=DecimalEncoder))

                processed = True

        else:
            print("Unhandled notification type: " +  sesNotificationType)
    else:
        print("Incoming event is not a mail event")
        print("Received event was: " + json.dumps(event, indent=2))
        processed = True

    return processed
