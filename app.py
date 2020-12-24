from flask import Flask, render_template, request, jsonify
import random
import numpy as np
import game
from game import gameHandler, clientHandler


app = Flask(__name__)

#Make the app
app = Flask(__name__)

#Bootstrap old games
game.bootstrap({"purge":True})


def auth(playerName, gameName, code):
    secret = game.getAuthCode(playerName, gameName)
    if code == secret:
        return True
    else:
        return False

### ROUTES...

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
        print(game.joinLobby(gameName, {ownerName:{"isPlaying":True}}))

    info = game.gameInfo(gameName)
    print(info)
    
    
    data = {"stuff":True}#{"authCode": player.about["authCode"]}
    return jsonify(data)


@app.route('/api/join_game', methods=['POST'])
def joinGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    print(game.joinLobby(gameName, {playerName:{"isPlaying":True}})) #This will show what happened when trying to join each player to the lobby
    print(game.gameInfo(gameName)) #This will show the general info of the game

    data = {"game": True}
    return jsonify(data) #This is mega broken

@app.route('/api/getPlayers', methods=['POST'])
def getPlayers():
    
    data = request.get_json()
    gameName = data["gameName"]
    session = game.gameInfo(gameName)
    if session == False:
        print("game not found")
        data = {"game": False}
        return jsonify(data)
    
    data = game.listClientNames(gameName)

    data.update({"game": True})
    return jsonify(data)

@app.route('/api/getNumTiles', methods=['POST'])
def getNumTiles():
    data = request.get_json()
    gameName = data["gameName"]

    data = game.gameInfo(gameName)["gridTemplate"]["tileNums"]
    return jsonify(data)

@app.route('/api/startGame', methods=['POST'])
def startGame():
    data = request.get_json()
    gameName = data["gameName"]
    authCode = data["authCode"]
    
    data = {}

    data.update({"game": True})
    return jsonify(data)


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
