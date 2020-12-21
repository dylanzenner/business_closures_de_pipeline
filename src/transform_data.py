import urllib3
import boto3
import certifi
import json
import pymongo
from pymongo import MongoClient

# First we must retrieve our secrets from secrets manager so we can make our connections

# Get DocDB secret
DocDBclient = boto3.client("secretsmanager", "us-east-1")
response = DocDBclient.get_secret_value(
    SecretId="DocDB",
)
secretDict = json.loads(response["SecretString"])


# This will be our MongoClient connection string
connection_string = (
    "mongodb://"
    + secretDict["username"]
    + ":"
    + secretDict["password"]
    + "@"
    + secretDict["host"]
    + ":"
    + str(secretDict["port"])
    + "/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet"
    "=rs0&readPreference=secondaryPreferred&retryWrites=false"
)


# Get secret for Slack Channel
Slackclient = boto3.client("secretsmanager", "us-east-1")
response2 = Slackclient.get_secret_value(SecretId="Slack_Channel_Endpoint")
secretDict2 = json.loads(response2["SecretString"])
slack_endpoint = secretDict2["Slack_Channel"]


# Get instance Ids for SSM run command
EC2client = boto3.client("secretsmanager", "us-east-1")
response3 = EC2client.get_secret_value(SecretId="EC2_instanceID")
secretDict3 = json.loads(response3["SecretString"])
instanceId = secretDict3["SSM_instanceID"]


# Make our connection to the DocumentDB cluster
client = MongoClient(connection_string)


# Specify which database to use
db = client.de_project


# Specify which collection to use
col = db.businesses


# specify the certificates to use
http = urllib3.PoolManager(ca_certs=certifi.where())


# Specify the variable for SSM
SSM = boto3.client("ssm")


def transformations():
    """
    Does some transformations on the data and loads the newly transformed data
    into a new collection
    :return: None
    """ ""
    
    col.aggregate(
        [
            {
                "$match": {
                    "$or": [
                        {"state": "CA"},
                        {
                            "business_zip": {
                                "$in": [
                                    94016,
                                    94102,
                                    94103,
                                    94104,
                                    94105,
                                    94107,
                                    94108,
                                    94109,
                                    94110,
                                    94111,
                                    94112,
                                    94114,
                                    94115,
                                    94116,
                                    94117,
                                    94118,
                                    94119,
                                    94120,
                                    94121,
                                    94122,
                                    94123,
                                    94124,
                                    94125,
                                    94126,
                                    94127,
                                    94129,
                                    94130,
                                    94131,
                                    94132,
                                    94133,
                                    94134,
                                    94137,
                                    94139,
                                    94140,
                                    94141,
                                    94142,
                                    94143,
                                    94144,
                                    94145,
                                    94146,
                                    94147,
                                    94151,
                                    94153,
                                    94154,
                                    94156,
                                    94158,
                                    94159,
                                    94160,
                                    94161,
                                    94162,
                                    94163,
                                    94164,
                                    94171,
                                    94172,
                                    94177,
                                    94188,
                                ]
                            }
                        },
                        {"city": {"$regex": "/San Fran/i"}},
                    ]
                }
            },
            {
                "$project": {
                    "mailing_address_1": 0,
                    "mail_city": 0,
                    "mail_zipcode": 0,
                    "mail_state": 0,
                }
            },
            {"$out": "transformations"},
        ]
    )


def run_command():
    """
    Invokes the SSM run command to export the transformed data to S3 and shut down the services
    """
    SSM.send_command(
        InstanceIds=[instanceId], DocumentName="Export_Data_Shutdown_Services"
    )


def lambda_handler(event, context):
    """
    Handler for lambda, calls the transformations function and sends message to slack
    """
    transformations()
    # Send a message to slack
    slack_url = slack_endpoint
    msg = {
        "channel": "DE-Project",
        "username": "webhook-username",
        "text": "Hello, from AWS Lambda! I am messaging you to let you know that \
        your Lambda function has successfully transformed your data and output \
        the results to a new collection! Your EC2 Instance and DocumentDB Cluster \
        have also been stopped.",
        "icon_emoji": "",
    }

    encoded_msg = json.dumps(msg).encode("utf-8")
    resp = http.request("POST", slack_url, body=encoded_msg)

    # Shut down services
    run_command()


# close the connection
client.close()
