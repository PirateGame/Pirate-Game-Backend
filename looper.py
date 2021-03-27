import socketio
import time
import datetime
sio = socketio.Client()

while True:
    time.sleep(5)
    try:
        sio.emit("looper")
        print("loop: " + str(datetime.datetime.now()))
    except:
        try:
            print("disconnected")
            sio.connect("http://localhost:5000")
        except:
            pass
