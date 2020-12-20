import random, string
import numpy as np
from gridGenerator import *
import time

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) 
games = {}
#maxGameLength = 55 + (10 * gridSize) + (90 * (howManyEachAction * clientCount))

### CLASSES USED TO DESCRIBE GAMES AND CLIENTS ###

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

    def __init__(self, gameName, ownerID, gridDim):
        self.gameName = gameName
        self.gameIDNum = None
        self.ownerID = ownerID
        self.gridDim = gridDim
        self.turnNum = -1
        self.chosenTiles = []

        self.clients = {}

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        if self.whichBoardAmI() == None:
            BOARDS.append([[self.gameName, self.ownerID, self.gridDim], []])
            np.save("boards.npy", BOARDS)
            print(self.gameName, "@@@@ CREATED by client", str(ownerID), "with", gridDim, "dimensions.")
        else:
            print(self.gameName, "@@@@ RECOVERED by client", str(ownerID), "with", gridDim, "dimensions.")
        
    def genNewTile():
        options = []
        for x in range(self.gridDim[0]):
            for y in range(self.gridDim[1]):
                if (x,y) not in self.chosenTiles:
                    options.append((x,y))
        return random.choice(options)
    
    def whoIsOnThatLine(rOrC, coord):
        victims = []
        for client in self.clients:
            if rOrC == 1:
                if self.clients[client].about[column] == coord:
                    victims.append(client)
            else:
                if self.clients[client].about[row] == coord:
                    victims.append(client)
        return victims

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

    def start(self, clients):
        self.gameIDNum = self.whichBoardAmI()
        self.clientCount = len(clients)

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        for client in range(self.clientCount):
            BOARDS[self.gameIDNum][1].append([])
        np.save("boards.npy", BOARDS)   

        for key in clients:
            self.clients[key] = clientHandler(key, clients[key])

        self.randomCoords = []
        for x in range(gridDim[0]):
            for y in range(gridDim[1]):
                self.randomCoords.append((x,y))
        random.shuffle(self.randomCoords)
        print(self.gameName, "@@@ STARTED with", self.clientCount, "clients.")

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

class clientHandler(gameHandler):
    def __init__(self, clientName, isPlaying):
        if isPlaying:
            self.about = {"name":clientName, "money":0, "bank":0, "shield":False, "mirror":False, "column":random.randint(0,self.gridDim[0]), "row":random.randint(0,self.gridDim[1])}
        else:
            self.about = {"name":clientName}

    def act(whatHappened, clients, chosenTiles):
        if whatHappened == "A": #A - Rob
            return random.choice(self.clients)
        if whatHappened == "B": #B - Kill
            return random.choice(self.clients)
        if whatHappened == "C": #C - Present (Give someone 1000 of YOUR OWN cash)
            return random.choice(self.clients)
        if whatHappened == "D": #D - Skull and Crossbones (Wipe out (Number of players)/3 people)
            rOrC = random.randint(0,1)
            if rOrC == 1:
                columns = [i for i in range(self.gridDim[0])]
                columns.remove(self.about[column])
                choice = random.choice(columns)
            else:
                rows = [i for i in range(self.gridDim[1])]
                rows.remove(self.about[rows])
                choice = random.choice(rows)
            victims = whoIsOnThatLine(rOrC, choice)
            for victim in victims:
                self.clients[victim].beActedOn("D", self.about) ###ACT
        if whatHappened == "E": #E - Swap
            choice = random.choice(self.clients)
            self.clients[choice].beActedOn("E", self.about) ###ACT
        if whatHappened == "F": #F - Choose Next Square
            return self.genNewTile()
        if whatHappened == "G": #G - Shield
            self.about[shield] = True ###ACT
        if whatHappened == "H": #H - Mirror
            self.about[mirror] = True ###ACT
        if whatHappened == "I": #I - Bomb (You go to 0)
            self.about[money] = 0 ###ACT
        if whatHappened == "J": #J - Double Cash
            self.about[money] *= 2 ###ACT
        if whatHappened == "K": #K - Bank
            self.about[bank] += money ###ACT
            self.about[money] = 0 ###ACT
        if whatHappened == "5000": #£5000
            self.about[money] += 5000 ###ACT
        if whatHappened == "3000": #£3000
            self.about[money] += 3000 ###ACT
        if whatHappened == "1000": #£1000
            self.about[money] += 1000 ###ACT
        if whatHappened == "200": #£200
            self.about[money] += 200 ###ACT
    
    def beActedOn(whatHappened, aboutTheSender):
        #if self.about[shield] or self.about[mirror]:
            ###check with the vue server here about whether the user wants to use a shield or mirror?
        if whatHappened == "D":
            self.about[money], self.clients[aboutTheSender[name]].about[money] = self.clients[aboutTheSender[name]].about[money], self.about[money]


### FUNCTIONS THAT ARE NOT INDEPENDENT OF GAMES OR CLIENTS ###

#if not playing will they need an id to see the game stats or is that spoiling the fun?
def makeGame(gameName, ownerID, gridDim):
    if gameName not in games:
        if gameName == "":
            chars = string.ascii_letters + string.punctuation
            gameName = ''.join(random.choice(chars) for x in range(6))

        g = gameHandler(gameName, ownerID, gridDim)
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
            gridDim = BOARDS[gameIDNum][0][3]
            makeGame(gameName, ownerID, gridDim)
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

    makeGame(gameName, ownerID, gridDim)
    clients = {"Jamie":True}
    games[gameName].start(clients)

    ###Simulating the interaction with the vue server, pinging the processing of each successive turn like the Vue server will every time it's happy with client responses turn-by-turn.
    print("Enter any key to begin turn iteration...")
    shallIContinue = input()
    for turn in range(turnCount): #Simulate the frontend calling the new turns over and over.
        time.sleep(0.01)
        games[gameName].turnHandle()
    print(gameName, "@@@ Game over.")