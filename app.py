from flask import Flask, render_template, request, jsonify
import random, string
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
    playerCap = 10 #MODIFY THIS

    if len(gameName)<1:
        gameName = ''.join(random.choice(string.ascii_letters) for x in range(6))
    if len(ownerName)<1:
        ownerName = ''.join(random.choice(string.ascii_letters) for x in range(6))

    for char in gameName:
        if char not in string.ascii_letters:
            data = {"error": "Game name can only contain letters"}
            return jsonify(data)

    for char in ownerName:
        if char not in string.ascii_letters:
            data = {"error": "Your name can only contain letters"}
            return jsonify(data)

    gridDim = (Sizex, Sizey)
    #This sets the standard decison time
    decisionTime = 30

    nameUniqueFilter = None
    nameNaughtyFilter = None

    gameAbout = {"gameName":gameName, "ownerName":ownerName, "gridDim":gridDim, "turnTime":turnTime, "playerCap":playerCap, "nameUniqueFilter":nameUniqueness, "nameNaughtyFilter":nameNaughtyFilter}

    if not game.makeGame(gameAbout):
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



#TODO this needs major fixing, check that game exists and playercap stuff
@app.route('/api/join_game', methods=['POST'])
def joinGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]

    

    join = game.joinLobby(gameName, playerName)

    if join:
        authcode = game.clientInfo({"gameName":gameName, "clientName":playerName})
        authcode = authcode["about"]["authCode"]
        data = {
        "game": True,
        "authcode": "not - authcode",
        }


    #authcode = game.clientInfo({"gameName":gameName, "clientName":playerName})
    #authcode = authcode["about"]["authCode"]


    data = {
        "game": True,
        "authcode": "not - authcode",
        }
    return jsonify(data)

@app.route('/api/getPlayers', methods=['POST'])
def getPlayers():
    
    data = request.get_json()
    gameName = data["gameName"]
    session = game.gameInfo(gameName)
    if session == False:
        data = {"game": False}
        return jsonify(data)
    
    data = {"names":game.listClientNames(gameName)}

    data.update({"game": True})
    return jsonify(data)

@app.route('/api/getBarTiles', methods=['POST'])
def getBarTiles(): #This is used for building the list of tiles that are going to be displayed in the side board for the user to drag across.
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
        
    data = game.gameInfo(gameName)["gridTemplate"]["tileNums"]
    
    return jsonify(game.serialReadBoard(gameName, playerName, positions=False))

@app.route('/api/getGridDim', methods=['POST'])
def getGridDim():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]

    data = game.gameInfo(gameName)["about"]["gridDim"]
    print(data)
    out = {"x": data[0], "y": data[1]}

    return jsonify(out)



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

    print(board)

    if game.serialWriteBoard(gameName, playerName, board):
        data = {"game": True}
        return jsonify(data)
    else:
        data = {"game": "board did not fit requirements"}
        return jsonify(data)



@app.route('/api/randomiseBoard', methods=['POST'])
def randomiseBoard():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    game.randomiseBoard(gameName, playerName)

    board = game.serialReadBoard(gameName, playerName)

    return jsonify(board)

@app.route('/api/getGameState', methods=['POST'])
def getGameState():
    data = request.get_json()
    gameName = data["gameName"]

    data = game.status(gameName)

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, host="localhost")
