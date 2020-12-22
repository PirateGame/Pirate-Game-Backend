from flask import Flask, render_template, request, jsonify
import random
import numpy as np
import multiprocessing
import game


# SET UP DATABASE #
import pymongo
from uri import URI

app = Flask(__name__)

#Connect to database and assign it to the db object
client = pymongo.MongoClient(URI)
db = client.pirategame

#Access the users collection
users = db.users

#Make the app
app = Flask(__name__)

#Route that will return the first user in the users collection
@app.route('/')
def index():
    #Returns the first item of the users collection
    return users.find_one()

@app.route('/api/create_game', methods=['POST'])
def createGame():
    data = request.get_json()
    gameName = data["gameName"]
    ownerName = data["ownerName"]
    Sizex = data["Sizex"]
    Sizey = data["Sizey"]
    isPlaying = data["isHostPlaying"]

    gridDim = (Sizex, Sizey)
    #TODO this needs adjusting in the host control panel
    decisionTime = 30

    game.makeGame(gameName, ownerName, gridDim, decisionTime)

    if isPlaying:
        game.joinLobby(gameName, {ownerName:{"isPlaying":True}})

    status = game.status(gameName)

    print(status)
    
    
    data = {"stuff":True}#{"authCode": player.about["authCode"]}
    return jsonify(data)


@app.route('/api/join_game', methods=['POST'])
def joinGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]

    try:
        game.getGame(gameName)
    except:
        print("no game found")
        data = {"game":False}
        return jsonify(data)
    
    print("game found")
    session = game.getGame(gameName).lobbyJoin({playerName:{"isPlaying":True}})
    print(game.status(gameName))

    data = {"game": True}
    return jsonify(data)

@app.route('/api/getPlayers', methods=['POST'])
def getPlayers():
    
    data = request.get_json()
    gameName = data["gameName"]
    session = game.status(gameName)
    if session == False:
        print("game not found")
        data = {"game": False}
        return jsonify(data)
    
    data = game.listClients(gameName)

    return jsonify(data)
    

    
    return jsonify(data)

processes = []
if __name__ == "__main__":
    app.run(debug=False, host="localhost")
