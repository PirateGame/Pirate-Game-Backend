import socketio
import time
import datetime
sio = socketio.Client()
sio.connect("http://localhost:5000")

while True:
    time.sleep(5)
    sio.emit("looper")
    print("loop: " + str(datetime.datetime.now()))
