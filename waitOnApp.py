import app
import threading

### WAIT FOR RESPONSE FROM THE WEBSITE...

result_available = threading.Event()
global response
response = []
def awaitResponse(choice):
    print(choice)
    thread = threading.Thread(target=app.awaitResponseProcess, args=[choice])
    thread.start()
    # wait here for the result to be available before continuing
    result_available.wait()
    return response