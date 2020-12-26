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
    secret = "test"#get auth code
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
    #This sets the standard decison time
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

    #TODO get auth code.
    authcode = game.clientInfo({"gameName":gameName, "clientName":playerName})


    data = {
        "game": True
        }
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
    
    data = {"names":game.listClientNames(gameName)}

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
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        game.start(gameName)
        data = ({"auth": True})
        return jsonify(data)
    else:
        data = ({"auth": False})
        return jsonify(data)


#This should return what has just happened in the game.
@app.route('/api/getNext', methods=['POST'])
def getNext():
    return

#Set randomize only and decision time.
#when requesting from here, use json to with 
@app.route('/api/modifyGame', methods=['POST'])
def modifyGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    action = data["action"]
    print(action)
    #TODO work out how to get action into dict
    if auth(playerName, gameName, authCode):
        game.alterGames([gameName], {"name":"game2"})
        data = ({"auth": True})
        return jsonify(data)
    else:
        data = ({"auth": False})
        return jsonify(data)

    #use altergames function
    return


#Set team/ship
@app.route('/api/setTeam', methods=['POST'])
def setTeam():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    team = data["Team"]
    ship = data["Ship"]

    if auth(playerName, gameName, authCode):
        game.alterClients(gameName, [playerName], {"row": ship}) #Ship
        game.alterClients(gameName, [playerName], {"column": team}) #team
        data = ({"auth": True})
        return jsonify(data)
    else:
        data = ({"auth": False})
        return jsonify(data)
    return

#This should be used for the client to respond with what they want to do.
@app.route('/api/Action', methods=['POST'])
def Action():
    return

if __name__ == "__main__":
    app.run(debug=False, host="localhost")
