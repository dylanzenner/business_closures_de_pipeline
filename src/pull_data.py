import urllib3
import json
import certifi
import pymongo
from pymongo import MongoClient
from sodapy import Socrata
import boto3


# First we must retrive our secrets from secrets manager so we can make our connections

# Get secret for DocDB
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


# Get secrete for API Token
APIclient = boto3.client("secretsmanager", "us-east-1")
response3 = APIclient.get_secret_value(SecretId="API_Access_Token")
secretDict3 = json.loads(response3["SecretString"])
API_Token = secretDict3["api_token"]


# Make our connection to the DocumentDB cluster
client = MongoClient(connection_string)


# Specify the database to use
db = client.de_project


# Specify the collection to use
col = db.businesses
# Create an index
col.create_index("ttxid", unique=True)


# url to access
url = "https://data.sfgov.org/"


# specify the certificates to use
http = urllib3.PoolManager(ca_certs=certifi.where())


def check_connection():
    """
    Checks the connection status of the url to access
    :return: If the connection is available: "Successful Connection"
             If the connection is not available: "Connection Failed"
    """
    try:
        http.request("GET", url, retries=False)
        return "Successful Connection"
    except urllib3.exceptions.NewConnectionError:
        return "Connection Failed"


def pull_socrata():
    """
    Checks the connection to the API.
    If connection status code is 200: Pulls the data from the specified url and inserts each record into an array
    If connection status code is not 200: Prints out status code
    :return: An array of dictionaries
    """
    if check_connection() == "Successful Connection":
        with Socrata("data.sfgov.org", API_Token) as c:
            data = c.get_all("g8m3-pdis")
            try:
                col.insert_many(data, ordered=False)
            except pymongo.errors.BulkWriteError as e:
                panic = (lambda x: x["code"] != 11000, e.details["writeErrors"])
                if len(panic) > 0:
                    print("really panic")
    else:
        print(check_connection())


def insert_into_docdb(event, context):
    """
    Takes the returned data from the function pull_socrata and
    inserts it into a DocumentDB collection
    :return: None
    """
    pull_socrata()

    # Send a message to slack
    slack_url = slack_endpoint
    msg = {
        "channel": "DE-Project",
        "username": "webhook-username",
        "text": "Hello, from AWS Lambda! I am messaging you to let you know that \
        your Lambda function has successfully stored API data to your DocumentDB \
        database!",
        "icon_emoji": "",
    }

    encoded_msg = json.dumps(msg).encode("utf-8")
    resp = http.request("POST", slack_url, body=encoded_msg)

    print("Successful Response")


# Close the conection to our DocumentDB database
client.close()
