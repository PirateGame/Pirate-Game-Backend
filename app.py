from flask import Flask, render_template, request
import random
import numpy as np
import multiprocessing
import game


### SET UP DATABASE ###
import pymongo
from uri import URI

app = Flask(__name__)

game.deleteGame([key for key in game.games])

#Connect to database and assign it to the db object
client = pymongo.MongoClient(URI)
db = client.pirategame

#Access the users collection
users = db.users


@app.route('/api/create_game', methods=['POST'])
def hostGame():
    data = request.get_json()
    gameName = data["gameName"]
    ownerName = data["ownerName"]
    Sizex = data["Sizex"]
    Sizey = data["Sizey"]
    isPlaying = data["isHostPlaying"]





#Route that will return the first user in the users collection
@app.route('/')
def index():
    #Returns the first item of the users collection
    return users.find_one()



@app.route('/api/host_game', methods=['POST'])
def hostGame():
    gridDim = (Sizex, Sizey)
    #TODO this needs adjusting in the host control panel
    decisionTime = 30

    session = game.makeGame(gameName, ownerName, gridDim, decisionTime)
    print(game.status(gameName))
    print(game.getGame(gameName))
    if isPlaying:
        player = game.getGame(gameName).lobbyJoin({ownerName:{"isPlaying":True}})
        print(game.status(gameName))
    #print(game.about["clients"][ownerName].about)
    
    
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
    session = game.getGame(gameName)
    if session == False:
        print("game not found")
        data = {"game": False}
        return jsonify(data)
    print(session.status(gameName))



### MAIN THREAD ###
app = Flask(__name__)

processes = []
if __name__ == "__main__":
    '''
    p = multiprocessing.Process(target=gameHandlerThread, args=())
    p.daemon = True
    processes.append(p)
    processes[-1].start()
    processes[-1].join()
    '''
    app.run(debug=False, host="localhost")
