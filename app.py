from flask import Flask, render_template, request, jsonify, redirect
import random, string
import numpy as np
import game
from game import gameHandler, clientHandler, prettyPrinter


app = Flask(__name__)

#Make the app
app = Flask(__name__)

#Bootstrap old games
game.bootstrap({"purge":True})


def auth(playerName, gameName, code):
    secret = game.clientInfo({"gameName":gameName, "clientName":playerName})["about"]["authCode"]
    if code == secret:
        return True
    else:
        return False

def isHost(gameName, playerName):
    secret = game.gameInfo(gameName)["about"]["admins"][0]["name"]
    if playerName == secret:
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
    playerCap = 12 #MODIFY THIS
    debug=True

    if gameName is None:
        gameName = ''
    if ownerName is None:
        ownerName = ''

    for char in gameName:
        if char not in string.ascii_letters:
            data = {"error": "Game name can only contain letters"}
            return jsonify(data)

    for char in ownerName:
        if char not in (string.ascii_letters + ' '):
            data = {"error": "Your name can only contain letters"}
            return jsonify(data)

    gridDim = (Sizex, Sizey)
    #This sets the standard decision time
    turnTime = 30

    nameUniqueFilter = None
    nameNaughtyFilter = None

    gameAbout = {"gameName":gameName, "admins":[{"name":ownerName, "type":"human"}], "isSim":False, "debug":debug, "gridDim":gridDim, "turnTime":turnTime, "playerCap":playerCap, "nameUniqueFilter":nameUniqueFilter, "nameNaughtyFilter":nameNaughtyFilter}
    if not isPlaying:
        gameAbout["admins"] = [{"name":ownerName, "type":"spectator"}]

    out = game.makeGame(gameAbout)
    if not out:
        data = {"error": "could not create game"}
        return jsonify(data)
    else:
        gameName = out["gameName"]
        admins = out["admins"]

    authcode = game.clientInfo({"gameName":gameName, "clientName":admins[0]["name"]})["about"]["authCode"]
    
    data = {"error": False, "authcode": authcode, "playerName":admins[0]["name"], "gameName":gameName}
    return jsonify(data)



#TODO this needs major fixing, check that game exists and playercap stuff
@app.route('/api/join_game', methods=['POST'])
def joinGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]


    if len(gameName)<1:
        data = {"error": "Please enter a game name"}
        return jsonify(data)
    if len(playerName)<1:
        data = {"error": "please enter a name"}
        return jsonify(data)


    for char in gameName:
        if char not in string.ascii_letters:
            data = {"error": "Game name can only contain letters"}
            return jsonify(data)

    for char in playerName:
        if char not in (string.ascii_letters + ' '):
            data = {"error": "Your name can only contain letters"}
            return jsonify(data)


    if game.joinLobby(gameName, [{"name":playerName, "type":"human"}]):
        authcode = game.clientInfo({"gameName":gameName, "clientName":playerName})["about"]["authCode"]
        print(playerName + " joined game " + gameName)
        data = {"error": False, "authcode": authcode}
        return jsonify(data)
    else:
        data = {"error": "Something went wrong"}
        return jsonify(data)

@app.route('/api/getPlayers', methods=['POST'])
def getPlayers():
    
    data = request.get_json()
    gameName = data["gameName"]
    session = game.gameInfo(gameName)
    if session == False:
        data = {"error": "game not found"}
        return jsonify(data)
    
    clientList = game.listClients(gameName)
    toSend = []
    for clientName,about in clientList.items():
        text = str(about["type"]) + ": " + str(clientName)
        toSend.append(text)
    data = {"names":toSend}

    data.update({"error": False})
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
    out = {"x": data[0], "y": data[1]}

    return jsonify(out)

@app.route('/api/startGame', methods=['POST'])
def startGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            if game.start(gameName):
                game.turnHandle(gameName)
                data = ({"error":False})
                return jsonify(data)
            else:
                data = ({"error":"game not found"})
                return jsonify(data)
        else:
            data = ({"error":"You can't do this"})
            return jsonify(data)
    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)


def tryNewTurn(gameName):
    rQ = game.getRemainingQuestions(gameName)
    fE = game.filterEvents(gameName, {}, ['len(event["whoToShow"]) > 0'])
    tN = game.gameInfo(gameName)["about"]["turnNum"]
    if len(rQ) == 0 and len(fE) == 0 and tN != -1:
        #print("Starting next round as all events have been shown and there are no remaining questions.")
        game.turnHandle(gameName)
        return True
    else:
        #print("A new turn can't be triggered as there are still questions to be answered or events to be shown.")
        #print(rQ, fE, tN)
        return False

@app.route('/api/getEvent', methods=['POST'])
def getEvent():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        print("all the events", game.filterEvents(gameName))
        unshownEvents = game.sortEvents(gameName, "timestamp", game.filterEvents(gameName, {}, ['"' + playerName + '"' + ' in event["whoToShow"]']))
        print("unshownEvents", unshownEvents)
        questions = game.clientInfo({"gameName":gameName, "clientName": playerName})["about"]["FRONTquestions"]
        print("unshownQuestions", questions)

        if len(unshownEvents) == 0 and len(questions) == 0 and game.gameInfo(gameName)["about"]["turnNum"] > -1:
            #tryNewTurn(gameName)
            data = ({"error": "empty"})
            return jsonify(data)
        else:
            descriptions = game.describeEvents(gameName, unshownEvents)
            timestamps = [event["timestamp"] for event in unshownEvents]

            questions = game.clientInfo({"gameName":gameName, "clientName": playerName})["about"]["FRONTquestions"]
            
            tiles = game.gameInfo(gameName)["about"]["chosenTiles"]
            width = game.gameInfo(gameName)["about"]["gridDim"][1]
            ids = []
            #print(tiles)
            for i in range(len(tiles)):
                ids.append((tiles[i][0] * width) + tiles[i][1])
            #except IndexError:
                ##this will happen if there are no tiles in the chosenTiles list, probably because the game hasn't started.
                #data = ({"error": "Game Not Started Yet"})
                #return jsonify(data)

            money = game.clientInfo({"gameName":gameName, "clientName": playerName})["about"]["money"]
            bank = game.clientInfo({"gameName":gameName, "clientName": playerName})["about"]["bank"]
            shield = game.clientInfo({"gameName":gameName, "clientName": playerName})["about"]["shield"]
            mirror = game.clientInfo({"gameName":gameName, "clientName": playerName})["about"]["mirror"]

            #print("----------------EVENTS---------------------")
            #for desc in descriptions:
                #print(desc)
            #print("----------------QUESTIONS------------------")
            #for question in questions:
                #print(question["labels"])
            #print("-------------------------------------------")

            data = {"error": False, "events": descriptions, "questions": questions, "ids":ids, "money": money, "bank": bank, "shield": shield, "mirror": mirror}
            game.shownToClient(gameName, playerName, timestamps)
            return jsonify(data)
    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)

@app.route('/api/submitResponse', methods=['POST'])
def submitResponse():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    choice = data["choice"]

    game.FRONTresponse(gameName, playerName, choice)

    data = {"error": False}
    return jsonify(data)

@app.route('/api/modifyGame', methods=['POST'])
def modifyGame():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    naughty = data["naughty"]
    similar = data["similar"]
    DecisionTime = data["DecisionTime"]
    randmoiseOnly = data["randomiseOnly"]
    playerCap = int(data["playerLimit"])

    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            game.alterGames([gameName], {"nameUniqueFilter":similar, "nameNaughtyFilter":naughty, "turnTime":DecisionTime, "playerCap": playerCap})
            data = ({"error": False})
            return jsonify(data)
        else:
            data = ({"error": "You do not have permission to do this"})
            return jsonify(data)

    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)


#Set team/ship
@app.route('/api/setTeam', methods=['POST'])
def setTeam():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    Captain = data["Captain"]
    ship = ["A","B","C"][data["Ship"]]

    if auth(playerName, gameName, authCode):
        game.alterClients(gameName, [playerName], {"row": str(ship)}) #Ship
        game.alterClients(gameName, [playerName], {"column": str(Captain)}) #captain
        data = ({"error": False})
        return jsonify(data)
    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)
    return


@app.route('/api/saveBoard', methods=['POST'])
def saveBoard():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    board = data["board"]

    if auth(playerName, gameName, authCode):
        if game.serialWriteBoard(gameName, playerName, board):
            game.readyUp(gameName, playerName)
            data = {"error": False}
            return jsonify(data)
        else:

            data = {"error": "board did not fit requirements"}
            return jsonify(data)
    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)


@app.route('/api/randomiseBoard', methods=['POST'])
def randomiseBoard():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        game.randomiseBoard(gameName, playerName)

        board = game.serialReadBoard(gameName, playerName)
        return jsonify(board)
    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)

@app.route('/api/getBoard', methods=['POST'])
def getBoard():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        board = game.serialReadBoard(gameName, playerName)
        return jsonify(board)
    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)
    

@app.route('/api/getGameState', methods=['POST'])
def getGameState():
    data = request.get_json()
    gameName = data["gameName"]

    state = game.status(gameName)

    data = {"error": False, "state":state}

    #if player number == number of boards submitted then we should send a state of ready to the host.
    #this will turn their start button from red to green, and allow them to press it.
    if game.readyPerc(gameName) == 1 and game.status(gameName) != "active" and game.status(gameName) != "paused":
        data = {"error": False, "state":"ready"}
        return jsonify(data)
    else:
        data = data
        return jsonify(data)

@app.route('/api/amIHost', methods=['POST'])
def amIHost():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            data = ({"error": False})
            return jsonify(data)
        else:
            data = ({"error": "You do not have permission to do this"})
            return jsonify(data)

    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)


@app.route('/api/kickPlayer', methods=['POST'])
def kickPlayer():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    playerToKick = data["playerToKick"]
    
    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            if game.leave(gameName, [playerToKick]):
                print("hopefully that kicked a player?")
                data = ({"error": False})
                return jsonify(data)
            else:
                data = ({"error": "Player kick failed"})
                return jsonify(data)
        else:
            data = ({"error": "You do not have permission to do this"})
            return jsonify(data)

    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)

@app.route('/api/addAI', methods=['POST'])
def addAI():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    
    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            if game.joinLobby(gameName, [{"name":"", "type":"AI"}]):
                data = ({"error": False})
                return jsonify(data)
            else:
                data = ({"error": "adding AI failed"})
                return jsonify(data)
        else:
            data = ({"error": "You do not have permission to do this"})
            return jsonify(data)

    else:
        data = ({"error": "Authentication failed"})
        return jsonify(data)

@app.route('/api/lobbyCheck', methods=['POST'])
def lobbyCheck():
    data = request.get_json()
    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if game.gameInfo(gameName)["about"]["turnNum"] != -1:
        data = {"error": False, "state":"started"}
        return jsonify(data)

    if game.readyPerc(gameName) == 1 and game.status(gameName) != "active" and game.status(gameName) != "paused":
        data = {"error": False, "state":"ready"}
        return jsonify(data)
    else:
        data = {"error": False, "state":"Waiting For Other Players"}
        return jsonify(data)

if __name__ == "__main__":
    app.run(debug=False, host="localhost")