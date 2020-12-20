from flask import Flask, render_template, request,jsonify
import game


app = Flask(__name__)

@app.route('/api/create_game', methods=['POST'])
def hostGame():
    data = request.get_json()
    gameID = data["gameID"]
    ownerID = data["ownerID"]
    Sizex = data["Sizex"]
    Sizey = data["Sizey"]
    Host = data["isHostPlaying"]

    result = game.makeGame(gameID, ownerID, Sizex, Sizey, Host)
    print(result)
    data = {'game': result[1], 'pass': result[0]}
    return jsonify(data)
    #this should tell the client if everything is ok, or custom name already taken.



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")