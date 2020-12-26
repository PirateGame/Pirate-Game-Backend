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
    secret = game.clientInfo({"gameName":gameName, "clientName":playerName})
    secret = secret["about"]["authCode"]
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

    if not game.makeGame(gameName, ownerName, gridDim, decisionTime):
        data = {"game": False}
        return jsonify(data)

    if isPlaying:
        game.joinLobby(gameName, {ownerName:{"isPlaying":True}})
    else:
        game.joinLobby(gameName, {ownerName:{"isPlaying":False}})

    authcode = game.clientInfo({"gameName":gameName, "clientName":ownerName})
    authcode = authcode["about"]["authCode"]
    
    
    data = {"game":True, "authcode": authcode}
    return jsonify(data)


@app.route('/api/join_game', methods=['POST'])
def joinGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]

    if not game.joinLobby(gameName, playerName):
        data = {"game": False}
        return jsonify(data)


    authcode = game.clientInfo({"gameName":gameName, "clientName":ownerName})
    authcode = authcode["about"]["authCode"]


    data = {
        "game": True,
        "authcode": authcode,
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

    #TODO add {"game":True} if game exists.

    
    #TODO format like this: {content: 'Kill',noResize: true, noMove:false}
        
    data = game.gameInfo(gameName)["gridTemplate"]["tileNums"]
    print(data)

    bigdata = []
    for i in range (0,data["A"]):
        bigdata.append({"content": 'Steal', "noResize": True, "noMove":False})

    for i in range (0, data["B"]):
        bigdata.append({"content": 'Kill', "noResize": True, "noMove":False})

    for i in range (0,data["C"]):
        bigdata.append({"content": 'Present', "noResize": True, "noMove":False})

    for i in range (0, data["D"]):
        bigdata.append({"content": 'Skull and Crossbones', "noResize": True, "noMove":False})

    for i in range (0,data["E"]):
        bigdata.append({"content": 'Swap', "noResize": True, "noMove":False})

    for i in range (0, data["F"]):
        bigdata.append({"content": 'Choose Next Square', "noResize": True, "noMove":False})

    for i in range (0,data["G"]):
        bigdata.append({"content": 'Shield', "noResize": True, "noMove":False})

    for i in range (0, data["H"]):
        bigdata.append({"content": 'Mirror', "noResize": True, "noMove":False})

    for i in range (0,data["I"]):
        bigdata.append({"content": 'Bomb', "noResize": True, "noMove":False})

    for i in range (0, data["J"]):
        bigdata.append({"content": 'Double', "noResize": True, "noMove":False})

    for i in range (0,data["K"]):
        bigdata.append({"content": 'Bank', "noResize": True, "noMove":False})

    for i in range (0,data["5000"]-1): #one less as one already in grid
        bigdata.append({"content": '5000', "noResize": True, "noMove":False})

    for i in range (0, data["3000"]):
        bigdata.append({"content": '3000', "noResize": True, "noMove":False})

    for i in range (0,data["1000"]):
        bigdata.append({"content": '1000', "noResize": True, "noMove":False})

    for i in range (0, data["200"]):
        bigdata.append({"content": '200', "noResize": True, "noMove":False})
    
    print(bigdata)
    return jsonify(bigdata)

@app.route('/api/startGame', methods=['POST'])
def startGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        if game.start(gameName):
            data = ({"auth": True}, {"game":True})
            return jsonify(data)
        else:
            data = ({"auth": True}, {"game":False})
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


@app.route('/api/saveBoard', methods=['POST'])
def saveBoard():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    board = data["board"]

    if sucess:
        data = {"game": True}
        return jsonify(data)
    else:
        data = {"game": False}
        return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, host="localhost")
