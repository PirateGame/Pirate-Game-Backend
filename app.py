from flask import Flask, render_template, request
import database

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/style.css')
def stylesheet():
    return 


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")