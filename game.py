import random, string, time
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
            if BOARDS[boardNum][0]["gameName"] == self.gameName:
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
        self.tileOverride = False
        self.chosenTiles = []

        self.clients = {}

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        if self.whichBoardAmI() == None:
            BOARDS.append([{"gameName":self.gameName, "ownerID":self.ownerID, "gridDim":self.gridDim, "clientCount":0}, {}])
            np.save("boards.npy", BOARDS)
            print(self.gameName, "@@@@ CREATED by client", str(ownerID), "with", gridDim, "dimensions.")
        else:
            print(self.gameName, "@@@@ RECOVERED by client", str(ownerID), "with", gridDim, "dimensions.")
        
    def genNewTile(self):
        options = []
        for x in range(self.gridDim[0]):
            for y in range(self.gridDim[1]):
                if (x,y) not in self.chosenTiles:
                    options.append((x,y))
        return random.choice(options)
    
    def whoIsOnThatLine(self, rOrC, coord):
        victims = []
        for client in self.clients:
            if rOrC == 1:
                if self.clients[client].about["column"] == coord:
                    victims.append(client)
            else:
                if self.clients[client].about["row"] == coord:
                    victims.append(client)
        return victims

    def newTurn(self):
        print(self.gameName, "@@ ------------ Turn", self.turnNum + 1, "------------")
        self.gameIDNum = self.whichBoardAmI()
        if self.turnNum == 0:
            toReturn = [False, []] #no user decision on which tile to play next yet so return False, and no turns have been played yet so return an empty list
        else:
            if self.tileOverride == False:
                newTile = (self.randomCoords[self.turnNum-1][0], self.randomCoords[self.turnNum-1][1]) #x,y
            else:
                newTile = self.tileOverride
                self.tileOverride = False
            self.chosenTiles.append(newTile)
            actions = []
            for client in self.clients:
                self.clients[client].act(BOARDS[self.gameIDNum][1][client][newTile[0]][newTile[1]])
                
                #actions.append(BOARDS[self.gameIDNum][client][newTile[0]][newTile[1]])
            #for a in range(len(actions)):
                #if actions[a] == #B for bomb, K for kill, so on...

                #This needs to be ASYNC so that whenever a client response comes in on what they've chosen to do, it's executed immediately
                #Each client's turn should be processed based on the new tile coordinate, and if it requires user input or not, broadcasted back to the Vue server to be presented to the clients.
            #A signal should be emitted here to the Vue Server holding the new turn's tile coordinates, for each vue client to process what on their grid
            tileOverride = False #Sample = (1,2) #x,y #If one of the client's processed above was to choose the next turn's tile, this would change accordingly.
            toReturn = [self.tileOverride, self.chosenTiles]
        return toReturn
    def status(self):
        return {"turnNum":self.turnNum}
    
    def leaderboard(self):
        for client in self.clients:
            print(self.clients[client].about["name"], "has score", self.clients[client].about["bank"] + self.clients[client].about["money"])
    
    def lobbyJoin(self, client):
        self.gameIDNum = self.whichBoardAmI()
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        #BOARDS[self.gameIDNum][client] = [[]] #whatever the fuck the vue server sent back about each user's grid
        gr = makeGrid(gridDim)
        BOARDS[self.gameIDNum][1][client] = gr[0]
        BOARDS[self.gameIDNum][0]["clientCount"] += 1
        BOARDS = np.save("boards.npy", BOARDS)

    def start(self):
        self.gameIDNum = self.whichBoardAmI()

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()

        for key in clients:
            self.clients[key] = clientHandler(self, key, clients[key])

        np.save("boards.npy", BOARDS)   

        self.randomCoords = []
        for x in range(gridDim[0]):
            for y in range(gridDim[1]):
                self.randomCoords.append((x,y))
        random.shuffle(self.randomCoords)
        print(self.gameName, "@@@ STARTED with", BOARDS[self.gameIDNum][0]["clientCount"], "clients.")

    def turnHandle(self):
        self.turnNum += 1
        result = self.newTurn() #This is the information necessary for the next turn to be processed.
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        for client in self.clients:
            print(self.gameName, "@ Client", self.clients[client].about["name"], "has stats", self.clients[client].about, "and board...")
            for y in range(self.gridDim[1]):
                thisRow = BOARDS[self.gameIDNum][1][client][y]
                thisRowPrintable = []
                for x in range(len(thisRow)):
                    if (x,y) not in self.chosenTiles:
                        thisRowPrintable.append(thisRow[x])
                    else:
                        thisRowPrintable.append("#")
                print(self.gameName, "@", thisRowPrintable)
        self.tileOverride, self.chosenTiles = result
    
    def delete(self):
        self.gameIDNum = self.whichBoardAmI()
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        del BOARDS[self.gameIDNum]
        np.save("boards.npy", BOARDS)

class clientHandler():
    def __init__(self, game, clientName, isPlaying):
        self.game = game
        if isPlaying:
            self.about = {"name":clientName, "isPlaying": isPlaying, "money":0, "bank":0, "shield":False, "mirror":False, "column":random.randint(0,self.game.gridDim[0]-1), "row":random.randint(0,self.game.gridDim[1]-1)}
        else:
            self.about = {"name":clientName, "isPlaying": isPlaying}

    def act(self, whatHappened): ###THIS IS CURRENTLY ALL RANDOMISED, ALL THE RANDOM CODE PARTS SHOULD BE REPLACED WITH COMMUNICATION WITH VUE.
        if whatHappened == "A": #A - Rob
            choice = random.choice([client for client in clients])
            self.game.clients[choice].beActedOn("A", self.about) ###ACT
            print(self.game.gameName, "@", self.about["name"], "robs", self.game.clients[choice].about["name"])
        if whatHappened == "B": #B - Kill
            choice = random.choice([client for client in clients])
            self.game.clients[choice].beActedOn("B", self.about) ###ACT
            print(self.game.gameName, "@", self.about["name"], "kills", self.game.clients[choice].about["name"])
        if whatHappened == "C": #C - Present (Give someone 1000 of YOUR OWN cash)
            choice = random.choice([client for client in clients])
            self.game.clients[choice].beActedOn("C", self.about) ###ACT
            print(self.game.gameName, "@", self.about["name"], "gifts", self.game.clients[choice].about["name"])
        if whatHappened == "D": #D - Skull and Crossbones (Wipe out (Number of players)/3 people)
            rOrC = random.randint(0,1)
            if rOrC == 1:
                columns = [i for i in range(self.game.gridDim[0])]
                columns.remove(self.about["column"])
                choice = random.choice(columns)
            else:
                rows = [i for i in range(self.game.gridDim[1])]
                rows.remove(self.about["row"])
                choice = random.choice(rows)
            victims = self.game.whoIsOnThatLine(rOrC, choice)
            for victim in victims:
                self.game.clients[victim].beActedOn("D", self.about) ###ACT
            if rOrC == 1:
                print(self.game.gameName, "@", self.about["name"], "wiped out column", choice, "which held", [self.game.clients[victim].about["name"] for victim in victims])
            else:
                print(self.game.gameName, "@", self.about["name"], "wiped out row", choice, "which held", [self.game.clients[victim].about["name"] for victim in victims])
        if whatHappened == "E": #E - Swap
            choice = random.choice([client for client in clients])
            self.game.clients[choice].beActedOn("E", self.about) ###ACT
            print(self.game.gameName, "@", self.about["name"], "swaps with", self.game.clients[choice].about["name"])
        if whatHappened == "F": #F - Choose Next Square
            self.game.tileOverride = self.game.genNewTile()
            print(self.game.gameName, "@", self.about["name"], "chose the next square", (self.game.tileOverride[0] + 1, self.game.tileOverride[1] + 1))
        if whatHappened == "G": #G - Shield
            self.about["shield"] = True ###ACT
            print(self.game.gameName, "@", self.about["name"], "gains a shield.")
        if whatHappened == "H": #H - Mirror
            self.about["mirror"] = True ###ACT
            print(self.game.gameName, "@", self.about["name"], "gains a mirror.")
        if whatHappened == "I": #I - Bomb (You go to 0)
            self.about["money"] = 0 ###ACT
            print(self.game.gameName, "@", self.about["name"], "got bombed.")
        if whatHappened == "J": #J - Double Cash
            self.about["money"] *= 2 ###ACT
            print(self.game.gameName, "@", self.about["name"], "got their cash doubled.")
        if whatHappened == "K": #K - Bank
            self.about["bank"] += self.about["money"] ###ACT
            self.about["money"] = 0 ###ACT
            print(self.game.gameName, "@", self.about["name"], "banked their money.")
        if whatHappened == "5000": #£5000
            self.about["money"] += 5000 ###ACT
            print(self.game.gameName, "@", self.about["name"], "gained £5000.")
        if whatHappened == "3000": #£3000
            self.about["money"] += 3000 ###ACT
            print(self.game.gameName, "@", self.about["name"], "gained £3000.")
        if whatHappened == "1000": #£1000
            self.about["money"] += 1000 ###ACT
            print(self.game.gameName, "@", self.about["name"], "gained £1000.")
        if whatHappened == "200": #£200
            self.about["money"] += 200 ###ACT
            print(self.game.gameName, "@", self.about["name"], "gained £200.")
    
    def beActedOn(self, whatHappened, aboutTheSender): #These are all the functions that involve interaction between players
        #if self.about[shield] or self.about[mirror]:
            ###check with the vue server here about whether the user wants to use a shield or mirror?
        if self.about["mirror"]:
            choice = random.randint(0,1)
            if choice == 1:
                if whatHappened == "A":
                    self.game.clients[aboutTheSender["name"]].beActedOn("A", self.about)
                if whatHappened == "B":
                    self.game.clients[aboutTheSender["name"]].beActedOn("B", self.about)
                if whatHappened == "C":
                    self.game.clients[aboutTheSender["name"]].beActedOn("C", self.about)
                if whatHappened == "E":
                    self.game.clients[aboutTheSender["name"]].beActedOn("E", self.about)
        else:
            if self.about["shield"]:
                choice = random.randint(0,1)
            if not self.about["shield"] or choice == 0:
                if whatHappened == "A":
                    self.game.clients[aboutTheSender["name"]].about["money"] += self.about["money"]
                    self.about["money"] = 0
                if whatHappened == "B":
                    self.about["money"], self.about["bank"] = 0, 0
                if whatHappened == "C":
                    if self.game.clients[aboutTheSender["name"]].about["money"] >= 1000:
                        self.about["money"] += 1000
                        self.game.clients[aboutTheSender["name"]].about["money"] -= 1000
                    elif self.game.clients[aboutTheSender["name"]].about["money"] > 0:
                        self.about["money"] += self.game.clients[aboutTheSender["name"]].about["money"]
                        self.game.clients[aboutTheSender["name"]].about["money"] = 0
                if whatHappened == "E":
                    self.about["money"], self.game.clients[aboutTheSender["name"]].about["money"] = self.game.clients[aboutTheSender["name"]].about["money"], self.about["money"]
            else:
                self.about["shield"] = False


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
    elif len(success) > 0:
        print(success, "@@@@ DELETED")
    else:
        print("@@@@ NOTHING DELETED")

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
            gameName = BOARDS[gameIDNum][0]["gameName"]
            ownerID = BOARDS[gameIDNum][0]["ownerID"]
            gridDim = BOARDS[gameIDNum][0]["gridDim"]
            makeGame(gameName, ownerID, gridDim)
    except:
        BOARDS = []
        np.save("boards.npy", BOARDS)
    
    ###And then deleting all those recovered games, because they're not necessary to test one new game.
    deleteGame([key for key in games])

    while True:
        ###Making a new demo game...
        gridDim = (8,8)
        gridSize = gridDim[0] * gridDim[1]
        turnCount = gridSize + 1 #maximum of gridSize + 1
        ownerID = 1
        gameName = "Test-Game " + str(time.time())

        ###Setting up a test game, and adding each player sequentially.
        makeGame(gameName, ownerID, gridDim)
        clients = {"Jamie":True, "Tom":True} #Player name, whether they're playing.
        for client in clients:
            games[gameName].lobbyJoin(client)

        ###Simulating the interaction with the vue server, pinging the processing of each successive turn like the Vue server will every time it's happy with client responses turn-by-turn.
        print("Enter any key to begin turn iteration...")
        shallIContinue = input()

        games[gameName].start()
        for turn in range(turnCount): #Simulate the frontend calling the new turns over and over.
            games[gameName].turnHandle()
        print(gameName, "@@@ Game over.")
        games[gameName].leaderboard()
        deleteGame([key for key in games])
        for i in range(3):
            print("")