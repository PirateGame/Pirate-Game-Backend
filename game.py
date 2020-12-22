import random, string, time
import numpy as np
from gridGenerator import *
import time

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) 
games = {}
#maxGameLength = 55 + (10 * gridSize) + (90 * (howManyEachAction * clientCount))

### I may have stole this from https://stackoverflow.com/a/25588771 and edited it quite a bit. -used to make printing pretty of course! ###

class prettyPrinter():
    def flattenList(self, t):
        flat_list = [item for sublist in t for item in sublist]
        return flat_list

    def format__1(self, digits,num):
        if digits<len(str(num)):
            raise Exception("digits<len(str(num))")
        return ' '*(digits-len(str(num))) + str(num)
    def printmat(self, arr,row_labels, col_labels): #print a 2d numpy array (maybe) or nested list
        max_chars = max([len(str(item)) for item in self.flattenList(arr)+col_labels]) #the maximum number of chars required to display any item in list
        if row_labels==[] and col_labels==[]:
            for row in arr:
                print('[%s]' %(' '.join(self.format__1(max_chars,i) for i in row)))
        elif row_labels!=[] and col_labels!=[]:
            rw = max([len(str(item)) for item in row_labels]) #max char width of row__labels
            print('%s %s' % (' '*(rw+1), ' '.join(self.format__1(max_chars,i) for i in col_labels)))
            for row_label, row in zip(row_labels, arr):
                print('%s [%s]' % (self.format__1(rw,row_label), ' '.join(self.format__1(max_chars,i) for i in row)))
        else:
            raise Exception("This case is not implemented...either both row_labels and col_labels must be given, or neither.")

### CLASSES USED TO DESCRIBE GAMES AND CLIENTS ###

class gameHandler():
    def __init__(self, gameName, ownerID, gridDim, decisionTime):
        def updateBOARDS(whatToUpdate):
            BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
            if whatToUpdate[0] == None:
                BOARDS[self.about["gameName"]][1] = whatToUpdate[1]
            elif whatToUpdate[1] == None:
                BOARDS[self.about["gameName"]][0] = whatToUpdate[0]
            else:
                BOARDS[self.about["gameName"]] = whatToUpdate
            np.save("boards.npy", BOARDS)
        
        self.about = {"gameName": gameName, "decisionTime":decisionTime, "ownerID": ownerID, "gridDim":gridDim, "turnNum":-1, "tileOverride":False, "chosenTiles":[], "clients":{}}

        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        if self.about["gameName"] not in BOARDS:
            updateBOARDS([self.about, {}])
            print(self.about["gameName"], "@@@@ CREATED by client", str(ownerID), "with", gridDim, "dimensions.")
        else:
            print(self.about["gameName"], "@@@@ RECOVERED by client", str(ownerID), "with", gridDim, "dimensions.")
        
        self.pP = prettyPrinter()

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
        if self.about["tileOverride"] == False:
            notUnique = True
            while notUnique:
                newTile = (self.randomCoords[self.about["turnNum"]-1][0], self.randomCoords[self.about["turnNum"]-1][1]) #x,y
                if newTile not in self.about["chosenTiles"]:
                    notUnique = False
        else:
            newTile = self.about["tileOverride"]
            self.about["tileOverride"] = False
        self.about["chosenTiles"].append(newTile)
        print(self.about["gameName"], "@@ ------------------------ Turn", self.about["turnNum"] + 1, "--- Tile", (newTile[0] + 1, newTile[1] + 1), "------------------------")

        actions = []
        for client in self.about["clients"]:
            self.about["clients"][client].logScore()
            self.about["clients"][client].act(BOARDS[self.about["gameName"]][1][client][newTile[1]][newTile[0]])
            
            #actions.append(BOARDS[self.gameIDNum][client][newTile[0]][newTile[1]])
        #for a in range(len(actions)):
            #if actions[a] == #B for bomb, K for kill, so on...
            #This needs to be ASYNC so that whenever a client response comes in on what they've chosen to do, it's executed immediately
            #Each client's turn should be processed based on the new tile coordinate, and if it requires user input or not, broadcasted back to the Vue server to be presented to the clients.
        #A signal should be emitted here to the Vue Server holding the new turn's tile coordinates, for each vue client to process what on their grid
    def status(self):
        return self.about

    def leaderboard(self):
        #for w in sorted(d, key=d.get, reverse=True):
            #print(w, d[w])
        for client in self.about["clients"]: # sort this using the above code.
            print(self.about["clients"][client].about["name"], "has score", self.about["clients"][client].about["bank"] + self.about["clients"][client].about["money"])
    
    def lobbyJoin(self, clients):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        #BOARDS[self.gameIDNum][client] = [[]] #whatever the fuck the vue server sent back about each user's grid
        out = []
        for client, about in clients.items():
            try:
                gr = makeGrid(gridDim)
                self.about["clients"][client] = clientHandler(self, client, about)
                if about["isPlaying"]:
                    BOARDS[self.about["gameName"]][1][client] = gr[0]
                out.append(True)
            except:
                out.append(False)
        BOARDS = np.save("boards.npy", BOARDS)
        return out
    
    def exit(self, clients):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        #BOARDS[self.gameIDNum][client] = [[]] #whatever the fuck the vue server sent back about each user's grid
        out = []
        for client in clients:
            try:
                del self.about["clients"][client]
                del BOARDS[self.about["gameName"]][1][client]
                out.append(True)
            except:
                out.append(False)
        BOARDS = np.save("boards.npy", BOARDS)
        return out

    def printBoards(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        for client in self.about["clients"]:
            print(self.about["gameName"], "@ Client", self.about["clients"][client].about["name"], "has stats", self.about["clients"][client].about, "and board...")
            row_labels = [str(y+1) for y in range(self.about["gridDim"][1])]
            col_labels = [str(x+1) for x in range(self.about["gridDim"][0])]
            tempBOARD = BOARDS[self.about["gameName"]][1][client]
            for tile in self.about["chosenTiles"]:
                tempBOARD[tile[1]][tile[0]] = "-"
            self.pP.printmat(tempBOARD, row_labels, col_labels)

    def start(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()

        np.save("boards.npy", BOARDS)   

        self.randomCoords = []
        for x in range(gridDim[0]):
            for y in range(gridDim[1]):
                self.randomCoords.append((x,y))
        random.shuffle(self.randomCoords)
        print(self.about["gameName"], "@@@ STARTED with", len(self.about["clients"]), "clients.")
        self.printBoards()

    def turnHandle(self):
        self.about["turnNum"] += 1
        self.newTurn()
        self.printBoards()
    
    def delete(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        del BOARDS[self.about["gameName"]]
        np.save("boards.npy", BOARDS)

class clientHandler():
    def __init__(self, game, client, about):
        self.game = game

        if about["isPlaying"]:
            self.about = {"name":client, "isPlaying": about["isPlaying"], "authCode":''.join(random.choice(string.ascii_letters + string.digits) for x in range(60)), "money":0, "bank":0, "scoreHistory":[], "shield":False, "mirror":False, "column":random.randint(0,self.game.about["gridDim"][0]-1), "row":random.randint(0,self.game.about["gridDim"][1]-1)}
        else:
            self.about = {"name":client, "isPlaying": about["isPlaying"]}
    
    def logScore(self):
        self.about["scoreHistory"].append(self.about["money"] + self.about["bank"])

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


### FUNCTIONS THAT ALLOW APP.PY TO INTERACT WITH GAME AND CLIENT OBJECTS, ###
### and also the main thread, which includes demo code. ###

#if not playing will they need an id to see the game stats or is that spoiling the fun?
def makeGame(gameName, ownerID, gridDim, decisionTime):
    if gameName not in games:
        if gameName == "":
            chars = string.ascii_letters + string.punctuation
            gameName = ''.join(random.choice(chars) for x in range(6))

        g = gameHandler(gameName, ownerID, gridDim, decisionTime)
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

#get the status of a game by name
def status(gameName):
    try:
        return games[gameName].status()
    except:
        return False

#get the clients of a game by name
def listClients(gameName):
    return games[gameName].about["clients"]

### MAIN THREAD ###
if __name__ == "__main__":
    ###Loading games that are "running", stored in boards.npy in case the backend crashes or something.
    try:
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        for gameName in BOARDS:
            gameName = gameName
            ownerID = BOARDS[gameName][0]["ownerID"]
            gridDim = BOARDS[gameName][0]["gridDim"]
            decisionTime = BOARDS[gameName][0]["decisionTime"]
            makeGame(gameName, ownerID, gridDim, decisionTime)
    except:
        BOARDS = {}
        np.save("boards.npy", BOARDS)
    
    ###And then deleting all those recovered games, because they're not necessary to test one new game.
    deleteGame([key for key in games])

    while True:
        ###Let's set up a few variables about our new test game...
        gridDim = (8,8)
        gridSize = gridDim[0] * gridDim[1]
        turnCount = gridSize + 1 #maximum of gridSize + 1
        ownerID = 1
        gameName = "Test-Game " + str(time.time())[-6:]
        decisionTime = 10

        ###Setting up a test game
        makeGame(gameName, ownerID, gridDim, decisionTime)

        ###Adding each of the imaginary players to the lobby sequentially.
        clients = {"Jamie":{"isPlaying":True}, "Tom":{"isPlaying":True}, "Alex":{"isPlaying":True}} #Player name, then info about them which currently consists of whether they're playing.
        games[gameName].lobbyJoin(clients) #This will create all the new players listed above so they're part of the gameHandler instance as individual clientHandler instances.
        #In future, when a user decides they don't want to play but still want to be in a game, the frontend will have to communicate with the backend to tell it to replace the isPlaying attribute in self.game.about["clients"][client].about
        
        ###Kicking one of the imaginary players. (regardless of whether the game is in lobby or cycling turns)
        games[gameName].exit(["Jamie"])

        ###Simulating the interaction with the vue server, pinging the processing of each successive turn like the Vue server will every time it's happy with client responses turn-by-turn.
        print("Enter any key to iterate a turn...")
        shallIContinue = input()

        games[gameName].start()
        for turn in range(turnCount): #Simulate the frontend calling the new turns over and over.
            shallIContinue = input()
            games[gameName].turnHandle()
        print(gameName, "@@@ Game over.")
        games[gameName].leaderboard()
        deleteGame([key for key in games])
        for i in range(3):
            print("")