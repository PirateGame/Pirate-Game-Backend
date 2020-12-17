from flask import Flask, render_template, request
import database

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play')
def play():
    return render_template('play.html')



if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")