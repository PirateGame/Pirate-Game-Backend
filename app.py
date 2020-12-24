from flask import Flask, render_template, request, jsonify
import random
import numpy as np
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
    Sizex = int(data["Sizex"])
    Sizey = int(data["Sizey"])
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
    
    print(game.joinLobby(gameName, {playerName:{"isPlaying":True}})) #This will show what happened when trying to join each player to the lobby
    print(game.status(gameName)) #This will show the general status of the game

    data = {"game": True}
    return jsonify(data) #This is mega broken

@app.route('/api/getPlayers', methods=['POST'])
def getPlayers():
    
    data = request.get_json()
    gameName = data["gameName"]
    session = game.status(gameName)
    if session == False:
        print("game not found")
        data = {"game": False}
        return jsonify(data)
    
    data = game.listClients({"gameName":gameName, "private":True})
    print(data)
    players = list(data.keys())

    return jsonify(players)

@app.route('/api/getNumTiles', methods=['POST'])
def getNumTiles():
    return

#This should return what has just happened in the game.
@app.route('/api/getNext', methods=['POST'])
def getNext():
    return

@app.route('/api/setDecisionTime', methods=['POST'])
def setDecisionTime():
    return
    

@app.route('/api/setRandomizeOnly', methods=['POST'])
def setRandomizeOnly():
    return

#This should be used for the client to respond with what they want to do.
@app.route('/api/Action', methods=['POST'])
def Action():
    return

if __name__ == "__main__":
    app.run(debug=False, host="localhost")
