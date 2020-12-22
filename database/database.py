import pymongo
from uri import URI

client = pymongo.MongoClient(URI)
db = client.pirategame

users = db.users