from flask import Flask, render_template, request,jsonify
import game
import pymongo
import random, string

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]

mycol = mydb["accounts"]

app = Flask(__name__)

@app.route('/api/create_game', methods=['POST'])
def hostGame():
    data = request.get_json()
    gameName = data["gameName"]
    ownerName = data["ownerName"]
    Sizex = data["Sizex"]
    Sizey = data["Sizey"]
    isPlaying = data["isHostPlaying"]

    Dim = (Sizex, Sizey)
    #session = game.gameHandler(gameName, ownerName, Dim)
    #result = game.clientHandler(gameName, ownerName, isPlaying)
    #authCode = result.authCode


    temp = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(60))
    
    
    data = {"authCode": temp}
    return jsonify(data)


@app.route('/api/join_game', methods=['POST'])
def joinGame():
    data = request.get_json()
    print(data)
    gameName = data["gameName"]
    playerName = data["playerName"]

    #join game

    data = {
        "authCode": "not-implemented",
        "gameAvaliable": "not-implemeted"
    }
    return jsonify(data)




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")