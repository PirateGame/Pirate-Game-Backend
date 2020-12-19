from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/api/create_game', methods=['POST'])
def hostGame():
    print("it has worked")
    print(request.data)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")