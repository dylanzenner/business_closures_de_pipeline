import boto3
import json
import urllib3
import certifi

http = urllib3.PoolManager(ca_certs=certifi.where())


def launch_ec2():
    """
    Gets EC2 secret from secrets manager and launches the EC2 instance
    :return: Launch EC2 Instance
    """
    secrets_manager_client = boto3.client("secretsmanager", "us-east-1")
    response = secrets_manager_client.get_secret_value(SecretId="EC2_instanceID")
    secretDict = json.loads(response["SecretString"])

    EC2_client = boto3.client("ec2")
    # Launce the instance
    response = EC2_client.start_instances(InstanceIds=[secretDict["SSM_instanceID"]])
    return response


def launch_docdb():
    """
    Gets DocDB secret from secrets manager and launches the DocDB Cluster
    :return: Launch DBCluster
    """
    secrets_manager_client = boto3.client("secretsmanager", "us-east-1")
    response = secrets_manager_client.get_secret_value(SecretId="DocDB")
    secretDict = json.loads(response["SecretString"])

    docdbclient = boto3.client("docdb", "us-east-1")
    # Launce DocDB
    response2 = docdbclient.start_db_cluster(
        DBClusterIdentifier=secretDict["dbClusterIdentifier"]
    )
    return response2


def get_slack_secret():
    """
    Obtains the secret for the slack endpoint
    :return: Secrete for Slack Endpoint
    """
    secrets_manager_client = boto3.client("secretsmanager", "us-east-1")
    response = secrets_manager_client.get_secret_value(
        SecretId="Slack_Channel_Endpoint"
    )
    secretDict = json.loads(response["SecretString"])

    slack_endpoint = secretDict["Slack_Channel"]
    return slack_endpoint


def lambda_handler(event, context):
    """
    Launches EC2 instance and DocDB Cluster
    :return: None
    """
    launch_ec2()
    launch_docdb()

    slack_url = get_slack_secret()
    msg = {
        "channel": "DE-Project",
        "username": "webhook-username",
        "text": "Hello, from AWS Lambda! I am a notification letting you know \
         that your Lambda function has successfully started your services.",
        "icon_emoji": "",
    }

    encoded_msg = json.dumps(msg).encode("utf-8")
    resp = http.request("POST", slack_url, body=encoded_msg)
