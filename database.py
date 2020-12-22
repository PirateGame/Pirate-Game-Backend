import pymongo


client = pymongo.MongoClient("mongodb+srv://user123:bjADXameSKXGGD76@cluster0.pcoof.mongodb.net/pirategame?retryWrites=true&w=majority")
db = client.test

#use this file for interacting with the database.
#probably don't need  use auth, just games and game state.