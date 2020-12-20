from flask import Flask, render_template, request
import json
import game


app = Flask(__name__)

@app.route('/api/create_game', methods=['POST'])
def hostGame():
    data = request.get_json()
    id = data["ID"]
    Sizex = data["Sizex"]
    Sizey = data["Sizey"]

    #game.makeGame(id, Sizex, Sizey)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    #this should tell the client if everything is ok, or custom name already taken.



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")