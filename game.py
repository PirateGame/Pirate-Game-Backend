import random, string, time
import numpy as np
from gridGenerator import *
import time

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) 
games = {}
#maxGameLength = 55 + (10 * gridSize) + (90 * (howManyEachAction * clientCount))

### CLASSES USED TO DESCRIBE GAMES AND CLIENTS ###

class gameHandler():
    def __init__(self, gameName, ownerID, gridDim):
        def updateBOARDS(whatToUpdate):
            BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
            if whatToUpdate[0] == None:
                BOARDS[self.about["gameName"]][1] = whatToUpdate[1]
            elif whatToUpdate[1] == None:
                BOARDS[self.about["gameName"]][0] = whatToUpdate[0]
            else:
                BOARDS[self.about["gameName"]] = whatToUpdate
            np.save("boards.npy", BOARDS)
        
        self.about = {"gameName": gameName, "ownerID": ownerID, "gridDim":gridDim, "turnNum":-1, "tileOverride":False, "chosenTiles":[], "clients":{}}

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        if self.about["gameName"] not in BOARDS:
            updateBOARDS([self.about, {}])
            print(self.about["gameName"], "@@@@ CREATED by client", str(ownerID), "with", gridDim, "dimensions.")
        else:
            print(self.about["gameName"], "@@@@ RECOVERED by client", str(ownerID), "with", gridDim, "dimensions.")

    def genNewTile(self):
        options = []
        for x in range(self.about["gridDim"][0]):
            for y in range(self.about["gridDim"][1]):
                if (x,y) not in self.about["chosenTiles"]:
                    options.append((x,y))
        return random.choice(options)
    
    def whoIsOnThatLine(self, rOrC, coord):
        victims = []
        for client in self.about["clients"]:
            if rOrC == 1:
                if self.about["clients"][client].about["column"] == coord:
                    victims.append(client)
            else:
                if self.about["clients"][client].about["row"] == coord:
                    victims.append(client)
        return victims

    def newTurn(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        print(self.about["gameName"], "@@ ------------ Turn", self.about["turnNum"] + 1, "------------")
        if self.about["tileOverride"] == False:
            newTile = (self.randomCoords[self.about["turnNum"]-1][0], self.randomCoords[self.about["turnNum"]-1][1]) #x,y
        else:
            newTile = self.about["tileOverride"]
            self.about["tileOverride"] = False
        self.about["chosenTiles"].append(newTile)
        actions = []
        for client in self.about["clients"]:
            self.about["clients"][client].act(BOARDS[self.about["gameName"]][1][client][newTile[0]][newTile[1]])
            
            #actions.append(BOARDS[self.gameIDNum][client][newTile[0]][newTile[1]])
        #for a in range(len(actions)):
            #if actions[a] == #B for bomb, K for kill, so on...
            #This needs to be ASYNC so that whenever a client response comes in on what they've chosen to do, it's executed immediately
            #Each client's turn should be processed based on the new tile coordinate, and if it requires user input or not, broadcasted back to the Vue server to be presented to the clients.
        #A signal should be emitted here to the Vue Server holding the new turn's tile coordinates, for each vue client to process what on their grid
    def status(self):
        return self.about
    
    def leaderboard(self):
        for client in self.about["clients"]:
            print(self.about["clients"][client].about["name"], "has score", self.about["clients"][client].about["bank"] + self.about["clients"][client].about["money"])
    
    def lobbyJoin(self, clients):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        #BOARDS[self.gameIDNum][client] = [[]] #whatever the fuck the vue server sent back about each user's grid

        for client, isPlaying in clients.items():
            gr = makeGrid(gridDim)
            self.about["clients"][client] = clientHandler(self, client, isPlaying)
            if isPlaying:
                BOARDS[self.about["gameName"]][1][client] = gr[0]
        BOARDS = np.save("boards.npy", BOARDS)

    def start(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()

        np.save("boards.npy", BOARDS)   

        self.randomCoords = []
        for x in range(gridDim[0]):
            for y in range(gridDim[1]):
                self.randomCoords.append((x,y))
        random.shuffle(self.randomCoords)
        print(self.about["gameName"], "@@@ STARTED with", len(self.about["clients"]), "clients.")

    def turnHandle(self):
        self.about["turnNum"] += 1
        self.newTurn()
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        for client in self.about["clients"]:
            print(self.about["gameName"], "@ Client", self.about["clients"][client].about["name"], "has stats", self.about["clients"][client].about, "and board...")
            for y in range(self.about["gridDim"][1]):
                thisRow = BOARDS[self.about["gameName"]][1][client][y]
                thisRowPrintable = []
                for x in range(len(thisRow)):
                    if (x,y) not in self.about["chosenTiles"]:
                        thisRowPrintable.append(thisRow[x])
                    else:
                        thisRowPrintable.append("#")
                print(self.about["gameName"], "@", thisRowPrintable)
    
    def delete(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        del BOARDS[self.about["gameName"]]
        np.save("boards.npy", BOARDS)

class clientHandler():
    def __init__(self, game, clientName, isPlaying):
        self.game = game

        self.authCode = 45

        if isPlaying:
            self.about = {"name":clientName, "isPlaying": isPlaying, "authCode":''.join(random.choice(string.ascii_letters + string.digits) for x in range(60)), "money":0, "bank":0, "shield":False, "mirror":False, "column":random.randint(0,self.game.about["gridDim"][0]-1), "row":random.randint(0,self.game.about["gridDim"][1]-1)}
        else:
            self.about = {"name":clientName, "isPlaying": isPlaying}
        

    def act(self, whatHappened): ###THIS IS CURRENTLY ALL RANDOMISED, ALL THE RANDOM CODE PARTS SHOULD BE REPLACED WITH COMMUNICATION WITH VUE.
        if whatHappened == "A": #A - Rob
            choice = random.choice([client for client in self.game.about["clients"]])
            self.game.about["clients"][choice].beActedOn("A", self.about) ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "robs", self.game.about["clients"][choice].about["name"])
        if whatHappened == "B": #B - Kill
            choice = random.choice([client for client in self.game.about["clients"]])
            self.game.about["clients"][choice].beActedOn("B", self.about) ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "kills", self.game.about["clients"][choice].about["name"])
        if whatHappened == "C": #C - Present (Give someone 1000 of YOUR OWN cash)
            choice = random.choice([client for client in self.game.about["clients"]])
            self.game.about["clients"][choice].beActedOn("C", self.about) ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "gifts", self.game.about["clients"][choice].about["name"])
        if whatHappened == "D": #D - Skull and Crossbones (Wipe out (Number of players)/3 people)
            rOrC = random.randint(0,1)
            if rOrC == 1:
                columns = [i for i in range(self.game.about["gridDim"][0])]
                columns.remove(self.about["column"])
                choice = random.choice(columns)
            else:
                rows = [i for i in range(self.game.about["gridDim"][1])]
                rows.remove(self.about["row"])
                choice = random.choice(rows)
            victims = self.game.whoIsOnThatLine(rOrC, choice)
            for victim in victims:
                self.game.about["clients"][victim].beActedOn("D", self.about) ###ACT
            if rOrC == 1:
                print(self.game.about["gameName"], "@", self.about["name"], "wiped out column", choice, "which held", [self.game.about["clients"][victim].about["name"] for victim in victims])
            else:
                print(self.game.about["gameName"], "@", self.about["name"], "wiped out row", choice, "which held", [self.game.about["clients"][victim].about["name"] for victim in victims])
        if whatHappened == "E": #E - Swap
            choice = random.choice([client for client in self.game.about["clients"]])
            self.game.about["clients"][choice].beActedOn("E", self.about) ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "swaps with", self.game.about["clients"][choice].about["name"])
        if whatHappened == "F": #F - Choose Next Square
            self.game.about["tileOverride"] = self.game.genNewTile()
            print(self.game.about["gameName"], "@", self.about["name"], "chose the next square", (self.game.about["tileOverride"][0] + 1, self.game.about["tileOverride"][1] + 1))
        if whatHappened == "G": #G - Shield
            self.about["shield"] = True ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "gains a shield.")
        if whatHappened == "H": #H - Mirror
            self.about["mirror"] = True ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "gains a mirror.")
        if whatHappened == "I": #I - Bomb (You go to 0)
            self.about["money"] = 0 ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "got bombed.")
        if whatHappened == "J": #J - Double Cash
            self.about["money"] *= 2 ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "got their cash doubled.")
        if whatHappened == "K": #K - Bank
            self.about["bank"] += self.about["money"] ###ACT
            self.about["money"] = 0 ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "banked their money.")
        if whatHappened == "5000": #£5000
            self.about["money"] += 5000 ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "gained £5000.")
        if whatHappened == "3000": #£3000
            self.about["money"] += 3000 ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "gained £3000.")
        if whatHappened == "1000": #£1000
            self.about["money"] += 1000 ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "gained £1000.")
        if whatHappened == "200": #£200
            self.about["money"] += 200 ###ACT
            print(self.game.about["gameName"], "@", self.about["name"], "gained £200.")
    
    def beActedOn(self, whatHappened, aboutTheSender): #These are all the functions that involve interaction between players
        #if self.about[shield] or self.about[mirror]:
            ###check with the vue server here about whether the user wants to use a shield or mirror?
        if self.about["mirror"]:
            choice = random.randint(0,1)
            if choice == 1:
                if whatHappened == "A":
                    self.game.about["clients"][aboutTheSender["name"]].beActedOn("A", self.about)
                if whatHappened == "B":
                    self.game.about["clients"][aboutTheSender["name"]].beActedOn("B", self.about)
                if whatHappened == "C":
                    self.game.about["clients"][aboutTheSender["name"]].beActedOn("C", self.about)
                if whatHappened == "E":
                    self.game.about["clients"][aboutTheSender["name"]].beActedOn("E", self.about)
        else:
            if self.about["shield"]:
                choice = random.randint(0,1)
            if not self.about["shield"] or choice == 0:
                if whatHappened == "A":
                    self.game.about["clients"][aboutTheSender["name"]].about["money"] += self.about["money"]
                    self.about["money"] = 0
                if whatHappened == "B":
                    self.about["money"], self.about["bank"] = 0, 0
                if whatHappened == "C":
                    if self.game.about["clients"][aboutTheSender["name"]].about["money"] >= 1000:
                        self.about["money"] += 1000
                        self.game.about["clients"][aboutTheSender["name"]].about["money"] -= 1000
                    elif self.game.about["clients"][aboutTheSender["name"]].about["money"] > 0:
                        self.about["money"] += self.game.about["clients"][aboutTheSender["name"]].about["money"]
                        self.game.about["clients"][aboutTheSender["name"]].about["money"] = 0
                if whatHappened == "E":
                    self.about["money"], self.game.about["clients"][aboutTheSender["name"]].about["money"] = self.game.about["clients"][aboutTheSender["name"]].about["money"], self.about["money"]
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
        for gameName in BOARDS:
            gameName = gameName
            ownerID = BOARDS[gameName][0]["ownerID"]
            gridDim = BOARDS[gameName][0]["gridDim"]
            makeGame(gameName, ownerID, gridDim)
    except:
        BOARDS = {}
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
            games[gameName].lobbyJoin({client:clients[client]})

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