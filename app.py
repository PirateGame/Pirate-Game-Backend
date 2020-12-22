from flask import Flask, render_template, request
import random
import numpy as np
import multiprocessing


### SET UP DATABASE ###
import pymongo
from uri import URI

#Connect to database and assign it to the db object
client = pymongo.MongoClient(URI)
db = client.pirategame

#Access the users collection
users = db.users



#Route that will return the first user in the users collection
@app.route('/')
def index():
    #Returns the first item of the users collection
    return users.find_one()




#This can be multi/singleprocessed as a thread for asynchronous behaviour.
def gameHandlerThread():  
    def newTurn(BOARDid, turnNum, tileOverride, clientCount):
        if turnNum == 0:
            BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
            for client in range(clientCount):
                BOARDS[BOARDid][client] = [[]] #whatever the fuck the vue server sent back about each user's grid
            BOARDS = np.save("boards.npy", BOARDS)
            toReturn = [False] #no user decision on which tile to play next yet so return False
        else:
            if tileOverride == False:
                newTile = (random.randint(0,gridDim[0]-1), random.randint(0,gridDim[1]-1)) #x,y
            else:
                newTile = tileOverride
            actions = []
            for client in range(clientCount):
                BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
                #actions.append(BOARDS[BOARDid][client][newTile[0]][newTile[1]])
            #for a in range(len(actions)):
                #if actions[a] == #B for bomb, K for kill, so on...

                #This needs to be ASYNC so that whenever a client response comes in on what they've chosen to do, it's executed immediately
                #Each client's turn should be processed based on the new tile coordinate, and if it requires user input or not, broadcasted back to the Vue server to be presented to the clients.
            #A signal should be emitted here to the Vue Server holding the new turn's tile coordinates, for each vue client to process what on their grid
            tileOverride = False #Sample = (1,2) #x,y #If one of the client's processed above was to choose the next turn's tile, this would change accordingly.
            toReturn = [tileOverride]
        print("@ Turn", turnNum, "has been processed.")
        return toReturn
    
    def clearAllGames():
        print("@@@ All games have been cleared.")
        try:
            BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        except:
            BOARDS = []
            np.save("boards.npy", BOARDS)

    def makeGame(ownerID, turnCount, gridDim, clientCount):
        print("@@@ A game has been made by client", str(ownerID), "with", turnCount, "turns,", gridDim, "dimensions and", clientCount, "clients.")
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        BOARDid = len(BOARDS)
        BOARDS.append([[] for i in range(clientCount)])
        np.save("boards.npy", BOARDS)

    def runGame(idToRun):

        print("@@ Game", idToRun, "has started.")

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        clientCount = len(BOARDS[idToRun])
        tileOverride = False
        for turnNum in range(turnCount):
            results = newTurn(idToRun, turnNum, tileOverride, clientCount) #This is the information necessary for the next turn to be processed.
            tileOverride = results[0]
        print("@@ Game", idToRun, "has ended.")
    
    def deleteGame(idToDelete):
        try:
            BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
            del BOARDS[idToDelete]
            np.save("boards.npy", BOARDS)
        except:
            pass

    ###RUN (main of this thread)
    
    shouldMakeGame = True #This should be ASYNC and waiting for a signal from the vue server that a client has decided to host a game.
    shouldDeleteGame = True#For testing purposes, we're only going to run one game at a time, so this makes sure there's only one in the array.
    shouldRunGame = True
    if shouldDeleteGame:
        deleteGame(0)
    if shouldMakeGame:
        turnCount = 10
        gridDim = (5,5)
        clientCount = 2
        ownerID = 1
        makeGame(ownerID, turnCount, gridDim, clientCount)
    if shouldRunGame:
        runGame(0) #id of the game to run

### MAIN THREAD ###
app = Flask(__name__)

processes = []
if __name__ == "__main__":
    '''
    p = multiprocessing.Process(target=gameHandlerThread, args=())
    p.daemon = True
    processes.append(p)
    processes[-1].start()
    processes[-1].join()
    '''
    app.run(debug=False, host="localhost")
