from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')