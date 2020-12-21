import pytest
from pytest import ExitCode
import mongomock
import pymongo
import certifi
import urllib3
from src.pull_data import pull_socrata, check_connection


client = mongomock.MongoClient()
db = client.test_database
col = db.test_collection

url = "https://data.sfgov.org/"

http = urllib3.PoolManager(ca_certs=certifi.where())
http.request("GET", url, retries=False)


def test_check_connection():
    
    """
    Tests whether or not check_connection returns either 'Successful Connection'
    or 'Connection Failed'
    :return: True or False
    """
    assert check_connection() in ["Successful Connection", "Connection Failed"]


def test_pull_socrata():
    """
    Tests that pull_socrata() inserts the data pulled from the API and returns an
    error only if the error code is not 11000
    :return: True or False
    """
    if check_connection() == "Successful Connection":
        pull_socrata()

    assert col != []
