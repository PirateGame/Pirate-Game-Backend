import random
import numpy as np
import multiprocessing
from gridGenerator import *

games = []

class gameHandler():
    def __init__(self, gameIDNum, gameID, ownerID, turnCount, gridDim):
        self.gameID = gameID
        self.gameIDNum = gameIDNum
        self.ownerID = ownerID
        self.turnCount = turnCount
        self.gridDim = gridDim
        self.turnNum = -1
        self.chosenTiles = []

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        if self.gameIDNum >= len(BOARDS):
            BOARDS.append([[self.ownerID, self.turnCount, self.gridDim], []])
            np.save("boards.npy", BOARDS)   
    def newTurn(self, turnNum, tileOverride, clientCount, chosenTiles, randomCoords):
        if turnNum == 0:
            BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
            for client in range(clientCount):
                print(clientCount)
                #BOARDS[self.gameIDNum][client] = [[]] #whatever the fuck the vue server sent back about each user's grid
                gr = makeGrid(gridDim)
                BOARDS[self.gameIDNum][1][client] = gr[0]
            BOARDS = np.save("boards.npy", BOARDS)
            toReturn = [False, []] #no user decision on which tile to play next yet so return False, and no turns have been played yet so return an empty list
        else:
            if tileOverride == False:
                newTile = (randomCoords[turnNum-1][0], randomCoords[turnNum-1][1]) #x,y
            else:
                newTile = tileOverride
            chosenTiles.append(newTile)
            actions = []
            for client in range(clientCount):
                BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
                #actions.append(BOARDS[self.gameIDNum][client][newTile[0]][newTile[1]])
            #for a in range(len(actions)):
                #if actions[a] == #B for bomb, K for kill, so on...

                #This needs to be ASYNC so that whenever a client response comes in on what they've chosen to do, it's executed immediately
                #Each client's turn should be processed based on the new tile coordinate, and if it requires user input or not, broadcasted back to the Vue server to be presented to the clients.
            #A signal should be emitted here to the Vue Server holding the new turn's tile coordinates, for each vue client to process what on their grid
            tileOverride = False #Sample = (1,2) #x,y #If one of the client's processed above was to choose the next turn's tile, this would change accordingly.
            toReturn = [tileOverride, chosenTiles]
        print("@@ Turn", turnNum + 1, "has been processed.")
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        print("@ The game board looks like this...")
        for client in range(len(BOARDS[self.gameIDNum][1])):
            print("@ Client", client)
            for x in range(len(BOARDS[self.gameIDNum][1][client])):
                thisRow = BOARDS[self.gameIDNum][1][client][x]
                thisRowPrintable = []
                for y in range(len(thisRow)):
                    if (x,y) not in chosenTiles:
                        thisRowPrintable.append(thisRow[y])
                    else:
                        thisRowPrintable.append("#")
                print(thisRowPrintable)
        return toReturn
    def status(self):
        return {"turnNum":self.turnNum}

    def start(self, clientCount):
        print("@@@ Game", self.gameIDNum, "has started.")
        self.clientCount = clientCount

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        for client in range(clientCount):
            BOARDS[self.gameIDNum][1].append([])
        np.save("boards.npy", BOARDS)   

        self.randomCoords = []
        for x in range(gridDim[0]):
            for y in range(gridDim[1]):
                self.randomCoords.append((x,y))
        random.shuffle(self.randomCoords)

    def turnHandle(self):
        self.tileOverride = False
        self.turnNum += 1
        result = self.newTurn(self.turnNum, self.tileOverride, self.clientCount, self.chosenTiles, self.randomCoords) #This is the information necessary for the next turn to be processed.
        self.tileOverride, self.chosenTiles = result
    
    def delete(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        del BOARDS[self.gameIDNum]
        np.save("boards.npy", BOARDS)


def makeGame(gameIDNum, gameID, ownerID, turnCount, gridDim):
    print("@@@@ A game has been made by client", str(ownerID), "with", turnCount, "turns,", gridDim, "dimensions.")
    g = gameHandler(gameIDNum, gameID, ownerID, turnCount, gridDim)
    games.append(g)

def clearAllGames():
    print("@@@@ All games have been cleared.")
    for i in range(len(processes)):
        processes[i].terminate()
    try:
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
    except:
        BOARDS = []
        np.save("boards.npy", BOARDS)

def deleteGame(idToDelete):
    try:
        games[idToDelete].delete()
        del games[idToDelete]
        print("@@@@ A game has been deleted with the ID", idToDelete)
    except:
        print("@@@@ Game", idToDelete, "doesn't exist, so it can't be deleted!")
        pass

def status(gameIDNum):
    if gameIDNum < len(games):
        return games[gameIDNum].status()
    else:
        return False

###Loading games that are "running"
try:
    BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
    for gameIDNum in range(len(BOARDS)):
        gameID = BOARDS[gameID][0][0]
        ownerID = BOARDS[gameID][0][1]
        turnCount = BOARDS[gameID][0][2]
        gridDim = BOARDS[gameID][0][3]
        makeGame(gameIDNum, gameID, ownerID, turnCount, gridDim)
    np.save("boards.npy", BOARDS)
except:
    BOARDS = []
    np.save("boards.npy", BOARDS)


### MAIN THREAD ###
processes = []
if __name__ == "__main__":
    for gameIDNum in range(len(games)):
        deleteGame(gameIDNum)

    gridDim = (8,8)
    gridSize = gridDim[0] * gridDim[1]
    turnCount = gridSize + 1 #maximum of gridSize + 1
    ownerID = 1
    gameID = "Test-Game"
    gameIDNum = 0

    makeGame(gameIDNum, gameID, ownerID, turnCount, gridDim)
    clientCount = 1
    games[0].start(clientCount)

    for turn in range(turnCount):
        games[0].turnHandle()
    print("@@@ Game", gameID, "has ended.")
