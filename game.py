import random, string
import numpy as np
from gridGenerator import *
import time

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) 

games = {}

#maxGameLength = 55 + (10 * gridSize) + (90 * (howManyEachAction * clientCount))

class gameHandler():
    def whichBoardAmI(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        notFound = True
        boardNum = -1
        while notFound and boardNum + 1 < len(BOARDS):
            boardNum += 1
            if BOARDS[boardNum][0][0] == self.gameName:
                notFound = False
        if notFound:
            return None
        else:
            return boardNum

    def __init__(self, gameName, ownerID, turnCount, gridDim):
        self.gameName = gameName
        self.gameIDNum = None
        self.ownerID = ownerID
        self.turnCount = turnCount
        self.gridDim = gridDim
        self.turnNum = -1
        self.chosenTiles = []

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        if self.whichBoardAmI() == None:
            BOARDS.append([[self.gameName, self.ownerID, self.turnCount, self.gridDim], []])
            np.save("boards.npy", BOARDS)
            print(self.gameName, "@@@@ CREATED by client", str(ownerID), "with", turnCount, "turns,", gridDim, "dimensions.")
        else:
            print(self.gameName, "@@@@ RECOVERED by client", str(ownerID), "with", turnCount, "turns,", gridDim, "dimensions.")

    def newTurn(self, turnNum, tileOverride, clientCount, chosenTiles, randomCoords):
        self.gameIDNum = self.whichBoardAmI()
        if turnNum == 0:
            BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
            for client in range(clientCount):
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
        print(self.gameName, "@@ Turn", turnNum + 1, "has been processed.")
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        print(self.gameName, "@ The game board looks like this...")
        for client in range(len(BOARDS[self.gameIDNum][1])):
            print(self.gameName, "@ Client", client)
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
        self.gameIDNum = self.whichBoardAmI()
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
        print(self.gameName, "@@@ STARTED with", clientCount, "clients.")

    def turnHandle(self):
        self.tileOverride = False
        self.turnNum += 1
        result = self.newTurn(self.turnNum, self.tileOverride, self.clientCount, self.chosenTiles, self.randomCoords) #This is the information necessary for the next turn to be processed.
        self.tileOverride, self.chosenTiles = result
    
    def delete(self):
        self.gameIDNum = self.whichBoardAmI()
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        del BOARDS[self.gameIDNum]
        np.save("boards.npy", BOARDS)


#turncount should initialise to 0
#if not playing will they need an id to see the game stats or is that spoiling the fun?

def makeGame(gameName, ownerID, turnCount, gridDim):
    if gameName not in games:
        if gameName == "":
            chars = string.ascii_letters + string.punctuation
            gameName = ''.join(random.choice(chars) for x in range(6))

        g = gameHandler(gameName, ownerID, turnCount, gridDim)
        games[gameName] = g
    else:
        print(gameName, "@@@@ FAILED GAME CREATION, that game name is already in use.")

#delete game(s) by Name
def deleteGame(gameNames):
    success = []
    fail = []
    for gameName in gameNames:
        try:
            games[gameName].delete()
            del games[gameName]
            success.append(gameName)
        except:
            fail.append(gameName)
    if len(fail) > 0:
        print(fail, "@@@@ NOT DELETED", success, "DELETED")
    else:
        print(success, "@@@@ DELETED")


#get the status of a game by ID number
def status(gameName):
    try:
        return games[gameName].status()
    except:
        return False



### MAIN THREAD ###
if __name__ == "__main__":
    ###Loading games that are "running", stored in boards.npy in case the backend crashes or something.
    try:
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        for gameIDNum in range(len(BOARDS)):
            gameName = BOARDS[gameIDNum][0][0]
            ownerID = BOARDS[gameIDNum][0][1]
            turnCount = BOARDS[gameIDNum][0][2]
            gridDim = BOARDS[gameIDNum][0][3]
            makeGame(gameName, ownerID, turnCount, gridDim)
    except:
        BOARDS = []
        np.save("boards.npy", BOARDS)

    ###And then deleting all those recovered games, because this is testing.
    deleteGame([key for key in games])

    ###Making a new demo game...
    gridDim = (8,8)
    gridSize = gridDim[0] * gridDim[1]
    turnCount = gridSize + 1 #maximum of gridSize + 1
    ownerID = 1
    gameName = "Test-Game"

    makeGame(gameName, ownerID, turnCount, gridDim)
    clientCount = 1
    games[gameName].start(clientCount)

    ###Simulating the interaction with the vue server, pinging the processing of each successive turn like the Vue server will every time it's happy with client responses turn-by-turn.
    print("Enter any key to begin turn iteration...")
    shallIContinue = input()
    for turn in range(turnCount): #Simulate the frontend calling the new turns over and over.
        time.sleep(0.01)
        games[gameName].turnHandle()
    print(gameName, "@@@ Game over.")