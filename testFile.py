import socket
import time

soc = socket.socket()

soc.connect(("127.0.0.1", 5000))

while True:
    soc.send(b"gameLoop")
    time.sleep(1)