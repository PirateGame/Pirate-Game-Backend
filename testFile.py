import threading
import time

def foo(msg):
    print(msg)
    

T = threading.Timer(5, print, ["hello"])
T.start()
while True:
    time.sleep(1)
    print("Working...")