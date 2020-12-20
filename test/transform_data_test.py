import pytest
from pytest import ExitCode
import mongomock
import pymongo
import certifi
import urllib3
from pull_data import pull_socrata, check_connection
from transform_data import transformations


client = mongomock.MongoClient()
db = client.test_database
col = db.test_collection

url = "https://data.sfgov.org/"

http = urllib3.PoolManager(ca_certs=certifi.where())
http.request("GET", url, retries=False)

check_connection()
pull_socrata()


def test_transformations_keys():
    """
    Tests that "mailing_address", "mail_city", "mail_zipcode", and "mail_state" 
    are successfully dropped from the collection
    """
    false_keys = ["mailing_address", "mail_city", "mail_zipcode", "mail_state"]
    for i in transformations():
        for item in false_keys:
            assert item not in i.keys()


def test_transformations():
    """
    Tests that every item returned by the transformation stage either has the key 
    'state' equal to 'CA' or the key 'business_zip' is in the array of zips
    """
    for i in transformations():
        assert i["state"] == "CA" or i["business_zip"] in [
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
