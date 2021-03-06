from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from prometheus_flask_exporter import PrometheusMetrics, Gauge, Counter, Summary
import random, string
import numpy as np
import random, string, time, os, ast
import grid
import time
import events
import nameFilter
import csv
import traceback
import subprocess

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) 

import eventlet
app = Flask(__name__)
metrics = PrometheusMetrics(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True, logger=True)

CONNECTED_SOCKETS = Gauge('socket_io_connected', 'Number of currently connected sockets')
REQUEST_TIME = Summary('turn_processing_seconds', 'Time spent processing turnhandle')
TURN = Counter('turns_total', 'total number of turns')
REQUEST = Counter('requests_total', 'socket requests', ['endpoint'])

ERROR = Counter('error_total', 'socket errors')
REQUEST.labels('/createGame')
REQUEST.labels('/joinGame')
REQUEST.labels('/getTiles')
REQUEST.labels('/getGridDim')
REQUEST.labels('/startGame')
REQUEST.labels('/submitResponse')
REQUEST.labels('/modifyGame')
REQUEST.labels('/setTeam')
REQUEST.labels('/saveBoard')
REQUEST.labels('/randomiseBoard')
REQUEST.labels('/getBoard')
REQUEST.labels('/amIHost')
REQUEST.labels('/kickPlayer')
REQUEST.labels('/addAI')
REQUEST.labels('/requestGameState')
REQUEST.labels('/requestPlayerList')
REQUEST.labels('/requstAllEvents')
REQUEST.labels('/requstLeaderboard')

########################################################################################################################################################################################################
#██████╗ ██╗██████╗  █████╗ ████████╗███████╗     ██████╗  █████╗ ███╗   ███╗███████╗
#██╔══██╗██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝
#██████╔╝██║██████╔╝███████║   ██║   █████╗      ██║  ███╗███████║██╔████╔██║█████╗  
#██╔═══╝ ██║██╔══██╗██╔══██║   ██║   ██╔══╝      ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  
#██║     ██║██║  ██║██║  ██║   ██║   ███████╗    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗
#╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
########################################################################################################################################################################################################

games = {}
schedule = {}
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

def debugPrint(message, debug=True):
    if debug:
        print("~"*220)
        print("BACK:wrappers(debug):", message)

########################################################################################################################################################################################################
#   ___       .    __   __ .____           .    __    _ .___          ___  .     _ .____  __    _  _______        ___   ____    _______ .____    ___   _______   _____
# .'   \     /|    |    |  /              /|    |\   |  /   `       .'   \ /     | /      |\   |  '   /         .'   `. /   \  '   /    /      .'   \ '   /     (     
# |         /  \   |\  /|  |__.          /  \   | \  |  |    |      |      |     | |__.   | \  |      |         |     | |,_-<      |    |__.   |          |      `--. 
# |    _   /---'\  | \/ |  |            /---'\  |  \ |  |    |      |      |     | |      |  \ |      |         |     | |    `     |    |      |          |         | 
#  `.___|,'      \ /    /  /----/     ,'      \ |   \|  /---/        `.__, /---/ / /----/ |   \|      /          `.__.' `----'  `--/    /----/  `.__,     /    \___.' 
### CLASSES USED TO DESCRIBE GAMES AND CLIENTS ###
########################################################################################################################################################################################################


class eventHandlerWrap():
    def __init__(self, game):
        self.game = game
        self.eventHandler = events.gameEventHandler(game)
    def make(self, about):
        event = self.eventHandler.make(about)
        if self.game.about["live"]:
            whoToShow = event["whoToShow"]
            for clientName in whoToShow:
                descriptions = self.eventHandler.describe(sortEvents(self.game.about["name"], "timestamp", filterEvents(self.game.about["name"], {}, ['"' + clientName + '"' + ' in event["whoToShow"]'])))
                turnUpdate(self.game.about["name"], clientName, descriptions)

class gameHandler():
    def debugPrint(self, message):
        if self.about["debug"]:
            print("BACK:gameHandler(debug):", message)
    
    def debugPrintBoards(self):
        if self.about["debug"]:
            BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
            for client in self.about["clients"]:
                print("~"*220)
                print("BACK:gameHandler(debug):", self.about["name"], "@ Client", self.about["clients"][client].about["name"], "has info", self.about["clients"][client].about, "and board...")
                row_labels = [str(y+1) for y in range(self.about["gridDim"][1])]
                col_labels = [str(x+1) for x in range(self.about["gridDim"][0])]
                tempBOARD = BOARDS[self.about["name"]][1][client]
                for tile in self.about["chosenTiles"]:
                    tempBOARD[tile[1]][tile[0]] = "-"
                self.pP.printmat(tempBOARD, row_labels, col_labels)

    def updateBOARDS(self, gameName, whatToUpdate):
        #if self.about["live"]:
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        if whatToUpdate[0] == None:
            BOARDS[gameName][1] = whatToUpdate[1]
        elif whatToUpdate[1] == None:
            BOARDS[gameName][0] = whatToUpdate[0]
        else:
            BOARDS[gameName] = whatToUpdate
        np.save("boards.npy", BOARDS)

    def __init__(self, about, overwriteAbout):
        maxEstTime = about["turnTime"] * about["gridDim"][0] * about["gridDim"][1]
        self.about = {"name":about["gameName"], "gameLoop":about["gameLoop"], "live":about["live"], "quickplay":about["quickplay"], "handleNum":0, "startTime":None, "debug":about["debug"], "status":["lobby"], "playerCap":about["playerCap"], "randomiseOnly":about["randomiseOnly"], "nameUniqueFilter":about["nameUniqueFilter"], "nameNaughtyFilter":about["nameNaughtyFilter"], "turnTime":about["turnTime"], "maxEstTime":maxEstTime, "admins":about["admins"], "gridDim":about["gridDim"], "turnNum":-1, "tileOverride":None, "chosenTiles":{}, "clients":{}, "gridTemplate":grid.grid(about["gridDim"])}

        if overwriteAbout == None:
            self.updateBOARDS(self.about["name"], [self.about, {}])
            self.join(about["admins"])
        else:
            self.about = overwriteAbout.copy()
            self.about["clients"] = {}
            for clientName, obj in overwriteAbout["clients"].items():
                clientsToJoin = [{"name":clientName, "type":obj.about["type"]}]
                self.join(clientsToJoin)
                self.about["clients"][clientName].about = obj.about
            self.updateBOARDS(self.about["name"], [self.about, None])
        
        self.pP = prettyPrinter()
        self.about["eventHandlerWrap"] = eventHandlerWrap(self)
        self.about["eventHandler"] =  self.about["eventHandlerWrap"].eventHandler #events.gameEventHandler(self)
        self.about["tempGroupChoices"] = {}
        self.about["randomCoords"] = []
    
    def writeAboutToBoards(self):
        self.updateBOARDS(self.about["name"], [self.about, None])
    
    def whoIsOnThatLine(self, choice):
        coord = choice
        if type(choice) == int:
            rOrC = 1
        else:
            rOrC = 0
        victims = []
        for client in self.about["clients"]:
            if rOrC == "column":
                if self.about["clients"][client].about["column"] == coord:
                    victims.append(client)
            else:
                if self.about["clients"][client].about["row"] == coord:
                    victims.append(client)
        return victims
    
    def groupDecisionAdd(self, clientName, event, choice):
        if event["event"] == "D":
            self.about["tempGroupChoices"][clientName] = choice
            if len(self.about["tempGroupChoices"]) == len(event["targets"]):
                self.groupDecisionConclude(event)

    def groupDecisionConclude(self, event):
        if event["event"] == "D":
            whoMirrored = []
            whoShielded = []
            for key, value in self.about["tempGroupChoices"].items():
                if value == "2":
                    whoMirrored.append(key)
                elif value == "3":
                    whoShielded.append(key)
            
            if len(whoMirrored) > 1: #Mirror
                print("GROUP MIRROR")
                rOrC = event["other"][0]
                if rOrC == 1:
                    choice = event["sources"][0].about["column"]
                else:
                    choice = event["sources"][0].about["row"]
                print("THIS IS UNFINISHED.")
                victims = self.whoIsOnThatLine(choice)
                self.about["eventHandlerWrap"].make({"owner":self.about["clients"][random.choice(whoMirrored)], "public":True, "event":event["event"], "sources":[self.about["clients"][i] for i in whoMirrored], "targets":[self.about["clients"][victim] for victim in victims], "isMirrored":True, "isShielded":False, "other":[rOrC, choice]}) #EVENT HANDLER
                for victim in victims:
                    self.about["clients"][victim].about["beActedOnQueue"].append(["D", self.about["clients"][random.choice(whoMirrored)], time.time()]) ###DELAYED ACT
            
            elif len(whoShielded) > 1: #Shield
                self.about["eventHandlerWrap"].make({"owner":self.about["clients"][random.choice(whoShielded)], "public":True, "event":event["event"], "sources":[self.about["clients"][i] for i in whoShielded], "targets":[], "isMirrored":False, "isShielded":True, "other":[]}) #EVENT HANDLER
            else:
                for clientName in self.about["tempGroupChoices"]:
                    self.about["clients"][clientName].forceActedOn("D")
        self.about["tempGroupChoices"] = {}
            
    def info(self):
        return {"about":self.about, "gridTemplate":self.about["gridTemplate"].about}
    
    def status(self): #= lobby, active, awaiting, paused, dormant
        return self.about["status"][-1]

    def leaderboard(self):
        clientByScore = {}
        for client in self.about["clients"]:
            clientByScore[client] = self.about["clients"][client].about["scoreHistory"][-1]
        out = {}
        for client in sorted(clientByScore, key=clientByScore.get, reverse=True):
            out[client] = {"score":clientByScore[client], "money":self.about["clients"][client].about["money"], "bank":self.about["clients"][client].about["bank"]}
        return out
    
    def join(self, clients):
        out = []
        for i in range(len(clients)):
            if clients[i]["name"] == "":
                nameCheck = "bla"
                while nameCheck != None:
                    temp = ''.join(random.choice(string.ascii_letters) for x in range(6))
                    nameCheck = nameFilter.checkString(self.about["clients"].keys(), temp, self.about["nameNaughtyFilter"], self.about["nameUniqueFilter"])
                clients[i]["name"] = temp
            else:
                nameCheck = nameFilter.checkString(self.about["clients"].keys(), clients[i]["name"], nameNaughtyFilter = 0.85, nameUniqueFilter = 0.85)
            if nameCheck == None: #(no problems with the name)
                if len(self.about["clients"].items()) < self.about["playerCap"]:
                    #if self.about["status"] == "lobby":
                    try:
                        self.about["clients"][clients[i]["name"]] = clientHandler(self, clients[i]["name"], clients[i])
                        self.about["clients"][clients[i]["name"]].buildRandomBoard()
                        self.writeAboutToBoards()
                        out.append(True)
                        self.debugPrint(str(self.about["name"]) + " @@@@ " + str(clients[i]["name"]) + " has joined on turn " + str(self.about["turnNum"] + 1))
                    except Exception as e:
                        out.append(e)
                    #else:
                        #out.append("The game is not in the lobby stage, it is in: " + self.about["status"])
                else:
                    out.append("The player cap of " + str(self.about["playerCap"]) + " has been reached.")
            else:
                out.append("The username " + clients[i]["name"] + " doesn't pass the name filters: " + str(nameCheck))
        return out
    
    def leave(self, clients):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        out = []
        for clientName in clients:
            try:
                del self.about["clients"][clientName]
                del BOARDS[self.about["name"]][1][clientName]
                self.writeAboutToBoards()
                out.append(True)
                self.debugPrint(str(self.about["name"]) + " @@@@ " + str(clientName) + "has left the lobby.")
            except:
                out.append(False)
        BOARDS = np.save("boards.npy", BOARDS)
        return out
    
    def serialReadBoard(self, clientName, positions):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        return self.about["gridTemplate"].serialReadBoard(BOARDS[self.about["name"]][1][clientName], positions)
    
    def serialWriteBoard(self, gameName, clientName, serial):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        BOARDS[self.about["name"]][1][clientName] = self.about["gridTemplate"].serialWriteBoard(BOARDS[self.about["name"]][1][clientName], serial)
        BOARDS = np.save("boards.npy", BOARDS)
    
    def filterClients(self, requirements, clients=[]):
        if clients == []:
            clients = self.about["clients"]
        out = {}
        for clientName,about in clients.items():
            wrongTally = 0
            for key,value in requirements.items():
                if clients[clientName].about[key] != value:
                    wrongTally += 1
            if wrongTally == 0:
                out[clientName] = about
        return out
        
    def gameLoop(self):
        try:
            print("GAMELOOP", self.about["turnNum"])
            if self.about["status"] == "dormant":
                print("GAMELOOP CLOSED.")
                return
            else:
                clientsShuffled = list(self.about["clients"].keys())
                random.shuffle(clientsShuffled)
                hasQuestions = {}
                for clientName in clientsShuffled:
                    if self.about["clients"][clientName].about["type"] == "human":
                        if len(self.about["clients"][clientName].about["FRONTquestions"]) > 0 or len(self.about["clients"][clientName].about["FRONTresponses"]) > 0:
                            hasQuestions[clientName] = True
                        else:
                            hasQuestions[clientName] = False
                print("HASQUESTIONS(HUMANS)", hasQuestions)
                if True in hasQuestions.values():
                    for clientName in hasQuestions.keys():
                        if hasQuestions[clientName]:
                            self.about["clients"][clientName].about["type"] = "AI"
                    for clientName, obj in self.about["clients"].items():
                        if len(obj.about["FRONTquestions"]) > 0:
                            choice = random.choice(obj.about["FRONTquestions"][0]["options"])
                            self.about["clients"][clientName].FRONTresponse(choice)
                    self.turnHandle()
                    for clientName in hasQuestions.keys():
                        if hasQuestions[clientName]:
                            self.about["clients"][clientName].about["type"] = "human"
                self.turnHandle()
                self.writeAboutToBoards()

        except:
            self.debugPrint("ERROR IN GAMELOOP!")
            traceback.print_exc()


    def turnLoop(self):
        schedule[self.about["name"]] = None
        try:
            print(self.about["name"], "TURNLOOP", self.about["turnNum"])
            if self.about["status"] == "dormant":
                print("TURNLOOP CLOSED.")
                return

            for clientName, obj in self.about["clients"].items():
                if len(obj.about["FRONTquestions"]) > 0:
                    choice = random.choice(obj.about["FRONTquestions"][0]["options"])
                    self.about["clients"][clientName].FRONTresponse(choice)
            self.turnHandle()
            self.writeAboutToBoards()

        except:
            self.debugPrint("ERROR IN TURNLOOP!")
            traceback.print_exc()
    
    def start(self):
        #Tell clients that the game has started
        if self.about["turnNum"] == -1:
            if self.about["live"]:
                sendGameStatusToClient(self.about["name"], {"state": "started"})
            self.about["status"].append("active")
            self.about["startTime"] = time.time()
            self.about["turnNum"] += 1
            self.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":"start", "sources":[], "targets":[], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER

            self.about["randomCoords"] = []
            for x in range(self.about["gridDim"][0]):
                for y in range(self.about["gridDim"][1]):
                    self.about["randomCoords"].append([x,y])
            random.shuffle(self.about["randomCoords"])
            self.debugPrint(str(self.about["name"]) + " @@@ STARTED with " + str(len(self.about["clients"])) + " clients, here's more info... " + str(self.info()))
            self.debugPrintBoards()
            self.writeAboutToBoards()
            if self.about["gameLoop"]:
                self.gameLoop()
        return True

    def turnProcess(self):
        actions = []
        clientsShuffled = list(self.about["clients"].keys())
        random.shuffle(clientsShuffled)
        
        out = []
        a = {}
        b = {}
        j = True
        log = []
        while j or (a != b and log[-1]):
            log.append(a != b)
            j = False
            for clientName in clientsShuffled:
                a[clientName] = self.about["clients"][clientName].about["actQueue"] + self.about["clients"][clientName].about["beActedOnQueue"]
                out.append(self.about["clients"][clientName].actHandle())
                b[clientName] = self.about["clients"][clientName].about["actQueue"] + self.about["clients"][clientName].about["beActedOnQueue"]
        for clientName in clientsShuffled:
            #print(clientName, "QUESTION QUEUE", self.about["clients"][clientName].about["FRONTquestions"])
            #print(self.about["clients"][clientName].about["FRONTquestions"])
            #print(self.about["clients"][clientName].about["FRONTresponses"])
            if len(self.about["clients"][clientName].about["FRONTquestions"]) > 0 or len(self.about["clients"][clientName].about["FRONTresponses"]) > 0:
                return False
        if False not in out:
            for clientName in clientsShuffled:
                self.about["clients"][clientName].logScore()
            return True
        else:
            return False
    
    @REQUEST_TIME.time()
    def turnHandle(self):
        TURN.inc()
        print("turn handle")
        self.about["openHandle"] = True
        if self.about["turnNum"] < 0:
            raise Exception("The game is on turn -1, which can't be handled.")
        if self.about["status"][-1] == "paused":
            raise Exception("The game is paused, which can't be handled.")
        if self.about["status"][-1] != "dormant" and self.about["turnNum"] < (self.about["gridDim"][0] * self.about["gridDim"][1]):
            if self.about["turnNum"] not in self.about["chosenTiles"].keys():
                if self.about["tileOverride"] == None:
                    newTile = random.choice(self.about["randomCoords"]) #x,y
                else:
                    newTile = self.about["tileOverride"]
                    self.about["tileOverride"] = None
                self.about["randomCoords"].remove(newTile)
                self.about["chosenTiles"][self.about["turnNum"]] = newTile
                x = newTile[0]
                y = newTile[1]
                BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
                for clientName in self.about["clients"].keys():
                    tileForClient = BOARDS[self.about["name"]][1][clientName][y][x]
                    self.about["clients"][clientName].about["tileHistory"].append(tileForClient)
                    self.about["clients"][clientName].about["actQueue"].append(tileForClient)
                self.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":"newTurn", "sources":[], "targets":[], "isMirrored":False, "isShielded":False, "other":[self.about["turnNum"]]}) #EVENT HANDLER
                self.debugPrint(str(self.about["name"]) + " @@ ------------------------ Turn " + str(self.about["turnNum"] + 1) + " --- Tile" + str(newTile[1] + 1) + "," + str(newTile[0] + 1) + " ------------------------")
            if self.turnProcess():
                print("turn complete")
                #we have a response, so move onto next turn.
                if self.about["turnNum"] < (self.about["gridDim"][0] * self.about["gridDim"][1]):
                    if self.about["status"][-1] != "active":
                        self.about["status"].append("active")
                    self.about["turnNum"] += 1
                    self.about["handleNum"] = 0
                    for clientName in self.about["clients"].keys():
                        self.about["clients"][clientName].about["actQueue"] = []
                        self.about["clients"][clientName].about["beActedOnQueue"] = []

                    #Add timer to start next round
                    schedule[self.about["name"]] = time.time() + 5

            else:
                #waiting for a response
                if self.about["status"][-1] != "awaiting":
                    self.about["status"].append("awaiting")
                if schedule[self.about["name"]] == None:
                    schedule[self.about["name"]] = time.time() + self.about["turnTime"]
        #Game is finished
        elif self.about["turnNum"] == (self.about["gridDim"][0] * self.about["gridDim"][1]):
            self.about["turnNum"] += 1
            self.about["status"].append("dormant") #this is for when the game doesn't end immediatedly after the turn count is up
            self.debugPrint(str(self.about["name"]) + " @@@ Game over.")
            self.debugPrint("Leaderboard: " + str(leaderboard(self.about["name"])))
            self.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":"end", "sources":[], "targets":[], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":"leaderboard", "sources":[], "targets":[], "isMirrored":False, "isShielded":False, "other":[leaderboard(self.about["name"])]}) #EVENT HANDLER
            GotoLeaderboard(self.game.about["name"])

    def getAllMyClientsQuestions(self):
        out = []
        for clientName,obj in self.about["clients"].items():
            out.extend(obj.about["FRONTquestions"])
        return out

    def delete(self):
        self.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":"delete", "sources":[], "targets":[], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        del BOARDS[self.about["name"]]
        np.save("boards.npy", BOARDS)
        del games[self.about["name"]]

class clientHandler():
    def __init__(self, game, clientName, about):
        self.game = game

        ##TYPE = AI, spectator, human
        if about["type"] == "human":
            self.about = {"name":clientName, "beActedOnQueue":[], "actQueue":[], "type": about["type"], "ready":False, "authCode":''.join(random.choice(string.ascii_letters + string.digits) for x in range(60)), "money":0, "bank":0, "scoreHistory":[], "tileHistory":[], "shield":0, "mirror":0, "row":random.choice(["A", "B", "C"]), "column":str(random.randint(0,2))}
        elif about["type"] == "AI":
            self.about = {"name":clientName, "beActedOnQueue":[], "actQueue":[], "type": about["type"], "ready":True, "authCode":''.join(random.choice(string.ascii_letters + string.digits) for x in range(60)), "money":0, "bank":0, "scoreHistory":[], "tileHistory":[], "shield":0, "mirror":0, "row":random.choice(["A", "B", "C"]), "column":str(random.randint(0,2))}
        elif about["type"] == "spectator":
            self.about = {"name":clientName, "type": about["type"], "ready":True, "authCode":''.join(random.choice(string.ascii_letters + string.digits) for x in range(60))}
        self.about["estimateHandler"] = events.clientEstimateHandler(self)
        self.about["FRONTresponses"] = []
        self.about["FRONTquestions"] = []


    def buildRandomBoard(self):
        BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
        gr = self.game.about["gridTemplate"].build()
        BOARDS[self.game.about["name"]][1][self.about["name"]] = gr
        BOARDS = np.save("boards.npy", BOARDS)
    
    def info(self):
        return {"about":self.about}
    
    def logScore(self):
        self.about["scoreHistory"].append(self.about["money"] + self.about["bank"])
    
    def FRONTresponse(self, choice):
        self.about["FRONTresponses"].append(choice)
        self.game.debugPrint("'" + choice + "' received for question: " + str(self.about["FRONTquestions"][-1]))
        #print("FRONTresponse")
        #print(self.about["FRONTquestions"])
        #print(self.about["actQueue"])
        #print(self.about["beActedOnQueue"])
        #del self.about["FRONTquestions"][0]
    
    def deQueueResponse(self):
        whatIsDeleted = self.about["FRONTresponses"][0]
        #print("DEQUEUE RESPONSE:", self.about["FRONTresponses"][0])
        #print(self.about["FRONTquestions"])
        del self.about["FRONTresponses"][0]
        del self.about["FRONTquestions"][0]
        #print(self.about["FRONTquestions"])
        return whatIsDeleted
    
    def makeQuestionToFRONT(self, question):
        self.game.debugPrint("A question has been raised. " + str(question) + " It should be answered by: ")
        question["timestamp"] = time.time()
        print(time.time() + self.game.about["turnTime"])

        
        schedule[self.game.about["name"]] = time.time() + self.game.about["turnTime"]
        print("SCHEDULE")
        print(schedule)

        self.about["FRONTquestions"].append(question)
        if self.game.about["live"]:
            sendQuestionToClient(self.game.about["name"], self.about["name"], {"labels":question["labels"], "options":question["options"]})
        #print("the current questions for this client are", self.about["FRONTquestions"])

    def rOrCChoice(self, whatHappened, queueType):
        self.rOrCChoiceWrapperInv = {"Jolly Rodger":"A", "Barnacle":"B", "Queen Anne's Revenge":"C", "Captain Hook":"0", "Blackbeard":"1", "Jack sparrow":"2"}
        self.rOrCChoiceWrapper = {v: k for k, v in self.rOrCChoiceWrapperInv.items()}
        options = ["A","B","C","0","1","2"]
        #options.remove(self.about["column"])
        #options.remove(self.about["row"])

        if self.about["type"] == "AI":
            choice = random.choice(options)
            return choice
        elif self.about["type"] == "human":
            if len(self.about["FRONTresponses"]) > 0:
                return self.rOrCChoiceWrapperInv[self.deQueueResponse()]
            elif len(self.about["FRONTquestions"]) == 0:
                options = [self.rOrCChoiceWrapper[option] for option in options]
                self.makeQuestionToFRONT({"gameName":self.game.about["name"], "queueType":queueType, "clientName": self.about["name"], "options":options, "labels":["You landed on a " + str(self.game.about["eventHandler"].eventDescriptions[whatHappened]) + "action.","Which team / ship do you want to attack?","Your captain is "+self.rOrCChoiceWrapper[self.about["column"]], "Your team is "+self.rOrCChoiceWrapper[self.about["row"]]]})
                return None
            else:
                return None

    def responseChoice(self, whatHappened, queueType):
        self.responseChoiceWrapperInv = {"Do nothing":"1", "Use your mirror":"3", "Use your shield":"2"}
        self.responseChoiceWrapper = {v: k for k, v in self.responseChoiceWrapperInv.items()}
        options = []
        for key,value in {"1":True, "3":self.about["mirror"] > 0, "2":self.about["shield"] > 0}.items():
            if value:
                options.append(key)
        
        if self.about["type"] == "AI":
            return random.choice(options)
        elif self.about["type"] == "human":
            options = [self.responseChoiceWrapper[option] for option in options]
            #if len(options) == 1:
                #return options[0]
            #print("FRONTRESPONSES", self.about["FRONTresponses"])
            if len(self.about["FRONTresponses"]) > 0:
                return self.responseChoiceWrapperInv[self.deQueueResponse()]
            elif len(self.about["FRONTquestions"]) == 0:
                self.makeQuestionToFRONT({"gameName":self.game.about["name"], "clientName": self.about["name"], "queueType":queueType, "options":options, "labels":["You've been targetted by a " + str(self.game.about["eventHandler"].eventDescriptions[whatHappened]) + " action.", "How will you react?"]})
                return None
            else:
                return None
    
    def victimChoice(self, whatHappened, queueType):
        if len(self.game.about["clients"]) == 1:
            return "Not enough clients"
        self.victimChoiceWrapper = {}
        options = []
        for clientName in self.game.about["clients"]:
            self.victimChoiceWrapper[clientName] = str(self.game.about["clients"][clientName].about["type"]) + ":" + clientName
            if clientName != self.about["name"]:
                options.append(clientName)
        self.victimChoiceWrapperInv = {v: k for k, v in self.victimChoiceWrapper.items()}
        
        if self.about["type"] == "AI":
            return random.choice(options)
        elif self.about["type"] == "human":
            if len(self.about["FRONTresponses"]) > 0:
                return self.victimChoiceWrapperInv[self.deQueueResponse()]
            elif len(self.about["FRONTquestions"]) == 0:
                options = [self.victimChoiceWrapper[option] for option in options]
                if whatHappened == "C":
                    self.makeQuestionToFRONT({"gameName":self.game.about["name"], "clientName": self.about["name"], "queueType":queueType, "options":options, "labels":["You landed on a Present action.", "Who do you want to give a present to?"]})
                else:
                    self.makeQuestionToFRONT({"gameName":self.game.about["name"], "clientName": self.about["name"], "queueType":queueType, "options":options, "labels":["You landed on a " + str(self.game.about["eventHandler"].eventDescriptions[whatHappened]) + " action.", "Who do you want to be your victim?"]})
                return None
            else:
                return None
    
    def tileChoice(self, whatHappened, queueType):
        optionsA = self.game.about["randomCoords"]
        options = [str([j + 1 for j in i]) for i in self.game.about["randomCoords"]]
        
        if self.about["type"] == "AI":
        #if True:
            return random.choice(optionsA)
        elif self.about["type"] == "human":
            if len(self.about["FRONTresponses"]) > 0:
                out = self.deQueueResponse()
                out = ast.literal_eval(out)
                out = [j - 1 for j in out]
                #print(out)
                #print(ast.literal_eval(out))
                return out
            if len(self.about["FRONTquestions"]) == 0:
                self.makeQuestionToFRONT({"gameName":self.game.about["name"], "clientName": self.about["name"], "queueType":queueType, "options":options, "labels":["Pick the next tile!"]})
                return None
            else:
                return None
    
    def actHandle(self):
        #print("ACT HANDLE CALLED FOR", self.about["name"], "WITH QUEUES", self.about["actQueue"], self.about["beActedOnQueue"])#
        if len(self.about["FRONTquestions"]) > 0 and len(self.about["beActedOnQueue"]) > 0 and len(self.about["actQueue"]) > 0:
            if self.about["FRONTquestions"][0]["queueType"] == "actQueue":
                self.act(self.about["actQueue"][0])
                del self.about["actQueue"][0]
                if len(self.about["actQueue"]) > 0:
                    return False
                elif len(self.about["beActedOnQueue"]) > 0:
                    return False
                return True
            elif self.about["FRONTquestions"][0]["queueType"] == "beActedOnQueue":
                self.beActedOn(*self.about["beActedOnQueue"][0])
                if len(self.about["beActedOnQueue"]) > 0:
                    return False
                elif len(self.about["actQueue"]) > 0:
                    return False
                return True
        elif len(self.about["beActedOnQueue"]) > 0:
            temp = self.about["beActedOnQueue"][0]
            del self.about["beActedOnQueue"][0]
            self.beActedOn(*temp)
            if len(self.about["beActedOnQueue"]) > 0:
                return False
            elif len(self.about["actQueue"]) > 0:
                return False
            return True
        elif len(self.about["actQueue"]) > 0:
            self.act(self.about["actQueue"][0])
            del self.about["actQueue"][0]
            if len(self.about["actQueue"]) > 0:
                return False
            elif len(self.about["beActedOnQueue"]) > 0:
                return False
            return True
        else:
            return True

    def act(self, whatHappened): 
        queueType = "actQueue"
        if whatHappened == "A": #A - Rob
            choice = self.victimChoice(whatHappened, queueType)
            if choice == "Not enough clients":
                pass
            elif choice != None:
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[self.game.about["clients"][choice]], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
                self.game.about["clients"][choice].beActedOn("A", self, time.time()) ###ACT
                #print(self.game.about["name"], "@", self.about["name"], "robs", self.game.about["clients"][choice].about["name"])
            else:
                self.about["actQueue"].append(whatHappened)
        if whatHappened == "B": #B - Kill
            choice = self.victimChoice(whatHappened, queueType)
            if choice == "Not enough clients":
                pass
            elif choice != None:
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[self.game.about["clients"][choice]], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
                self.game.about["clients"][choice].beActedOn("B", self, time.time()) ###ACT
                #print(self.game.about["name"], "@", self.about["name"], "kills", self.game.about["clients"][choice].about["name"])
            else:
                self.about["actQueue"].append(whatHappened)
        if whatHappened == "C": #C - Present (Give someone 1000 of YOUR OWN cash)
            choice = self.victimChoice(whatHappened, queueType)
            if choice == "Not enough clients":
                pass
            elif choice != None:
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[self.game.about["clients"][choice]], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
                self.game.about["clients"][choice].beActedOn("C", self, time.time()) ###ACT
                #print(self.game.about["name"], "@", self.about["name"], "gifts", self.game.about["clients"][choice].about["name"])
            else:
                self.about["actQueue"].append(whatHappened)
        if whatHappened == "D": #D - Skull and Crossbones (Wipe out (Number of players)/3 people)
            choice = self.rOrCChoice(whatHappened, queueType)
            if choice != None:
                victims = self.game.whoIsOnThatLine(choice)
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[self.game.about["clients"][victim] for victim in victims], "isMirrored":False, "isShielded":False, "other":[choice]}) #EVENT HANDLER
                for victim in victims:
                    self.game.about["clients"][victim].beActedOn("D", self, time.time()) ###ACT
                #if rOrC == "column":
                    #print(self.game.about["name"], "@", self.about["name"], "wiped out column", choice, "which held", [self.game.about["clients"][victim].about["name"] for victim in victims])
                #else:
                    #print(self.game.about["name"], "@", self.about["name"], "wiped out row", choice, "which held", [self.game.about["clients"][victim].about["name"] for victim in victims])
            else:
                self.about["actQueue"].append(whatHappened)
        if whatHappened == "E": #E - Swap
            choice = self.victimChoice(whatHappened, queueType)
            if choice == "Not enough clients":
                pass
            elif choice != None:
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[self.game.about["clients"][choice]], "isMirrored":False, "isShielded":False, "other":[self.about["money"], self.game.about["clients"][choice].about["money"]]}) #EVENT HANDLER
                self.game.about["clients"][choice].beActedOn("E", self, time.time()) ###ACT
                #print(self.game.about["name"], "@", self.about["name"], "swaps with", self.game.about["clients"][choice].about["name"])
            else:
                self.about["actQueue"].append(whatHappened)
        if whatHappened == "F": #F - Choose Next Square
            if self.game.about["turnNum"] + 1 < (self.game.about["gridDim"][0] * self.game.about["gridDim"][1]):
                choice = self.tileChoice(whatHappened, queueType)
                if choice != None:
                    self.game.about["tileOverride"] = choice
                    self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":False, "other":[self.game.about["tileOverride"]]}) #EVENT HANDLER
                    #print(self.game.about["name"], "@", self.about["name"], "chose the next square", (self.game.about["tileOverride"][0] + 1, self.game.about["tileOverride"][1] + 1))
                else:
                    self.about["actQueue"].append(whatHappened)
            else:
                pass
        if whatHappened == "G": #G - Shield
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["shield"] += 1 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "gains a shield.")
        if whatHappened == "H": #H - Mirror
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["mirror"] += 1 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "gains a mirror.")
        if whatHappened == "I": #I - Bomb (You go to 0)
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["money"] = 0 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "got bombed.")
        if whatHappened == "J": #J - Double Cash
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["money"] *= 2 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "got their cash doubled.")
        if whatHappened == "K": #K - Bank
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["bank"] += self.about["money"] ###ACT
            self.about["money"] = 0 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "banked their money.")
        if whatHappened == "5000": #£5000
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["money"] += 5000 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "gained £5000.")
        if whatHappened == "3000": #£3000
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["money"] += 3000 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "gained £3000.")
        if whatHappened == "1000": #£1000
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["money"] += 1000 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "gained £1000.")
        if whatHappened == "200": #£200
            self.game.about["eventHandlerWrap"].make({"owner":self, "public":False, "event":whatHappened, "sources":[self.game], "targets":[self], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
            self.about["money"] += 200 ###ACT
            #print(self.game.about["name"], "@", self.about["name"], "gained £200.")
    
    def beActedOn(self, whatHappened, sender, timestamp): #These are all the functions that involve interaction between players
        queueType = "beActedOnQueue"
        if whatHappened == "A":
            choice = self.responseChoice(whatHappened, queueType)
            if choice != None and len(self.about["beActedOnQueue"]) > 0:
                del self.about["beActedOnQueue"][0]
            if choice == None:
                self.about["beActedOnQueue"].append([whatHappened, sender, timestamp])
            elif choice == "1":
                self.game.about["clients"][sender.about["name"]].about["money"] += self.about["money"]
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[self.about["money"]]}) #EVENT HANDLER
                self.about["money"] = 0
            elif choice == "2":
                self.about["shield"] -= 1
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[]}) #EVENT HANDLER
            elif choice == "3":
                self.about["mirror"] -= 1
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[sender], "isMirrored":True, "isShielded":False, "other":[]}) #EVENT HANDLER
                self.game.about["clients"][sender.about["name"]].beActedOn("A", self, time.time())
        if whatHappened == "B":
            choice = self.responseChoice(whatHappened, queueType)
            if choice != None and len(self.about["beActedOnQueue"]) > 0:
                del self.about["beActedOnQueue"][0]
            if choice == None:
                self.about["beActedOnQueue"].append([whatHappened, sender, timestamp])
            elif choice == "1":
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[0]}) #EVENT HANDLER
                self.about["money"], self.about["bank"] = 0, 0
            elif choice == "2":
                self.about["shield"] -= 1
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[]}) #EVENT HANDLER
            elif choice == "3":
                self.about["mirror"] -= 1
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[sender], "isMirrored":True, "isShielded":False, "other":[]}) #EVENT HANDLER
                self.game.about["clients"][sender.about["name"]].beActedOn("B", self, time.time())
        if whatHappened == "C":
            choice = self.responseChoice(whatHappened, queueType)
            if choice != None and len(self.about["beActedOnQueue"]) > 0:
                del self.about["beActedOnQueue"][0]
            if choice == None:
                self.about["beActedOnQueue"].append([whatHappened, sender, timestamp])
            elif choice == "1":
                if self.game.about["clients"][sender.about["name"]].about["money"] >= 1000:
                    self.about["money"] += 1000
                    self.game.about["clients"][sender.about["name"]].about["money"] -= 1000
                    self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[1000]}) #EVENT HANDLER
                elif self.game.about["clients"][sender.about["name"]].about["money"] > 0:
                    self.about["money"] += self.game.about["clients"][sender.about["name"]].about["money"]
                    self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[self.game.about["clients"][sender.about["name"]].about["money"]]}) #EVENT HANDLER
                    self.game.about["clients"][sender.about["name"]].about["money"] = 0
            elif choice == "2":
                self.about["shield"] -= 1
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[]}) #EVENT HANDLER
            elif choice == "3":
                self.about["mirror"] -= 1
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[sender], "isMirrored":True, "isShielded":False, "other":[]}) #EVENT HANDLER
                self.game.about["clients"][sender.about["name"]].beActedOn("C", self, time.time())
        if whatHappened == "D":
            choice = self.responseChoice(whatHappened, queueType)
            if choice != None:
                if len(self.about["beActedOnQueue"]) > 0:
                    del self.about["beActedOnQueue"][0]
                #self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[]}) #EVENT HANDLER
                #print(sortEvents(self.game.about["name"], "timestamp", filterEvents(self.game.about["name"], {}, ['"' + sender.about["name"] + '"' + ' in event["sourceNames"]']))[-1])
                self.game.groupDecisionAdd(self.about["name"], sortEvents(self.game.about["name"], "timestamp", filterEvents(self.game.about["name"], {}, ['"' + sender.about["name"] + '"' + ' in event["sourceNames"]']))[-1], choice)
            if choice == None:
                self.about["beActedOnQueue"].append([whatHappened, sender, timestamp])
        if whatHappened == "E":
            choice = self.responseChoice(whatHappened, queueType)
            if choice != None and len(self.about["beActedOnQueue"]) > 0:
                del self.about["beActedOnQueue"][0]
            if choice == None:
                self.about["beActedOnQueue"].append([whatHappened, sender, timestamp])
            elif choice == "1":
                self.about["money"], self.game.about["clients"][sender.about["name"]].about["money"] = self.game.about["clients"][sender.about["name"]].about["money"], self.about["money"]
            elif choice == "2":
                self.about["shield"] -= 1
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[], "isMirrored":False, "isShielded":True, "other":[]}) #EVENT HANDLER
            elif choice == "3":
                self.about["mirror"] -= 1
                self.game.about["eventHandlerWrap"].make({"owner":self, "public":True, "event":whatHappened, "sources":[self], "targets":[sender], "isMirrored":True, "isShielded":False, "other":[]}) #EVENT HANDLER
                self.game.about["clients"][sender.about["name"]].beActedOn("C", self, time.time())

    def forceActedOn(self, whatHappened):
        if whatHappened == "D":
            self.about["money"] = 0

########################################################################################################################################################################################################
# .____ .     . __    _   ___   _______ _   ___   __    _   _____      .____   ___   .___           .    .___  .___ 
# /     /     / |\   |  .'   \ '   /    | .'   `. |\   |   (           /     .'   `. /   \         /|    /   \ /   \
# |__.  |     | | \  |  |          |    | |     | | \  |    `--.       |__.  |     | |__-'        /  \   |,_-' |,_-'
# |     |     | |  \ |  |          |    | |     | |  \ |       |       |     |     | |  \        /---'\  |     |    
# /      `._.'  |   \|   `.__,     /    /  `.__.' |   \|  \___.'       /      `.__.' /   \     ,'      \ /     /    
### FUNCTIONS THAT ALLOW APP.PY TO INTERACT WITH GAME AND CLIENT OBJECTS, ###
### and also the main thread, which includes demo code. ###
########################################################################################################################################################################################################

def checkGameState(gameName):
    if gameInfo(gameName)["about"]["turnNum"] != -1:
        data = {"error": False, "state":"started"}
        sendGameStatusToClient(gameName, data)

    if readyPerc(gameName) == 1 and status(gameName) != "active" and status(gameName) != "paused":
        data = {"error": False, "state":"ready"}
        sendGameStatusToClient(gameName, data)
    else:
        data = {"error": False, "state":"Waiting For Other Players"}
        sendGameStatusToClient(gameName, data)

#if not playing will they need an id to see the game stats or is that spoiling the fun?
def listGames():
    return games

def makeGame(about, overwriteAbout = None):
    for i in range(len(about["admins"])):
        if about["admins"][i]["name"] == "":
            nameCheck = "bla"
            while nameCheck != None:
                about["admins"][i]["name"] = ''.join(random.choice(string.ascii_letters) for x in range(6))
                nameCheck = nameFilter.checkString(games.keys(), about["gameName"], nameNaughtyFilter = about["nameNaughtyFilter"], nameUniqueFilter = about["nameUniqueFilter"])
    if about["gameName"] == "":
        nameCheck = "bla"
        while nameCheck != None:
            about["gameName"] = ''.join(random.choice(string.ascii_letters) for x in range(6))
            nameCheck = nameFilter.checkString(games.keys(), about["gameName"], nameNaughtyFilter = about["nameNaughtyFilter"], nameUniqueFilter = about["nameUniqueFilter"])
    else:
        nameCheck = nameFilter.checkString(games.keys(), about["gameName"], nameNaughtyFilter = about["nameNaughtyFilter"], nameUniqueFilter = about["nameUniqueFilter"])
    if nameCheck == None:
        g = gameHandler(about, overwriteAbout)
        games[about["gameName"]] = g
        if overwriteAbout != None:
            games[about["gameName"]].debugPrint(str(about["gameName"]) + " @@@@ RECOVERED with properties... " + str(games[about["gameName"]].about))
        else:
            games[about["gameName"]].debugPrint(str(about["gameName"]) + " @@@@ CREATED by clients " + str(about["admins"]) + " with properties... " + str(games[about["gameName"]].about))
        return {"gameName":about["gameName"], "admins":about["admins"]}
    else:
        print(about["gameName"], "@@@@ FAILED GAME CREATION:", ("The game name " + about["gameName"] + " doesn't pass the name filters: " + str(nameCheck)))
        return False

#delete game(s) by Name
def deleteGame(gameNames):
    success = []
    fail = []
    for gameName in gameNames:
        #try:
        games[gameName].delete()
        success.append(gameName)
        #except:
        #fail.append(gameName)
    if len(fail) > 0:
        debugPrint(str(fail) + " @@@@ NOT DELETED " + str(success) + "DELETED")
    elif len(success) > 0:
        debugPrint(str(success) + " @@@@ DELETED")
    else:
        debugPrint(str("@@@@ NOTHING DELETED"))

#get the info of a game by name
def gameInfo(gameName): #gameInfo("testGame")["about"]["admins"]
    try:
        return games[gameName].info()
    except Exception as e:
        return e

def pause(gameName):
    games[gameName].about["status"].append("paused")
    games[gameName].about["eventHandlerWrap"].make({"owner":games[gameName], "public":True, "event":"pause", "sources":[], "targets":[], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER
def resume(gameName):
    games[gameName].about["status"].append(games[gameName].about["status"][-2])
    games[gameName].about["eventHandlerWrap"].make({"owner":games[gameName], "public":True, "event":"resume", "sources":[], "targets":[], "isMirrored":False, "isShielded":False, "other":[]}) #EVENT HANDLER

#get the info of a client by name and game name
def clientInfo(about): #clientInfo({"gameName":"game1", "clientName":"Jamie"}) returns {"about":about}
    try:
        gameName = about.get("gameName")
        clientName = about.get("clientName")
        return games[gameName].about["clients"][about["clientName"]].info()
    except Exception as e:
        return e

#get the clients of a game by name and return either public or private information
def listClients(gameName, toReturn={"private":False, "human":True, "spectator":True, "AI":True}):
    typesToReturn = []
    for key,value in toReturn.items():
        if value and key != "private":
            typesToReturn.append(key)
    if toReturn["private"]:
        out = {}
        for client in games[gameName].about["clients"]:
            if games[gameName].about["clients"][client].about["type"] in typesToReturn:
                out[client] = games[gameName].about["clients"][client].about
    elif not toReturn["private"]:
        out = {}
        for clientName, obj in games[gameName].about["clients"].items():
            tempAbout = obj.about.copy()
            if tempAbout["type"] in typesToReturn:
                tempAbout["authCode"] = None
                tempAbout["money"] = None
                tempAbout["bank"] = None
                tempAbout["scoreHistory"] = None
                tempAbout["shield"] = None
                tempAbout["mirror"] = None
                tempAbout["column"] = None
                tempAbout["row"] = None
                out[clientName] = tempAbout
    return out

#list the names of all the clients by game name
def listClientNames(gameName):
    out = []
    for client in games[gameName].about["clients"]:
        out.append(games[gameName].about["clients"][client].about["name"])
    return out

def listQuickPlayGames():
    joinableKeys = []
    for key in games.keys():
        if games[key].about["quickplay"]:
            joinableKeys.append(key)
    return joinableKeys

#join one or several clients to a lobby
def joinLobby(gameName="", clients=""):
    if gameName == "":
        gameName = random.choice(listQuickPlayGames())
        return {"gameName":gameName, "response":games[gameName].join(clients)}
    if games[gameName].about["status"][-1] == "lobby":
        return {"gameName":gameName, "response":games[gameName].join(clients)}

def leave(gameName, clients):
    if len(games[gameName].about["clients"]) == 1:
        deleteGame(gameName)
    return games[gameName].leave(clients)

def leaderboard(gameName):
    return games[gameName].leaderboard()

def turnHandle(gameName):
    #playerName = "Alex"
    #print("SORTED EVENTS FOR ALEX", sortEvents(gameName, "timestamp", filterEvents(gameName, {}, ['"' + playerName + '"' + ' in event["sourceNames"] or ' + '"' + playerName + '"' + ' in event["targetNames"]'])))
    return games[gameName].turnHandle()

def gameLoop(gameName):
    print("starting game loop")
    games[gameName].gameLoop()

def turnLoop(gameName):
    games[gameName].turnLoop()

def start(gameName):
    temp = games[gameName].start()
    return temp

def status(gameName):
    return games[gameName].status()

def setStatus(gameName, status):
    games[gameName].about["status"].append(status)
    return True

def playerCount(gameName):
    return len(games[gameName].about["clients"])

def returnEvents(gameName, about):
    return games[gameName].about["eventHandler"].about["log"]

def readyPerc(gameName):
    return len(games[gameName].filterClients({"ready":True}).keys()) / len(games[gameName].about["clients"].keys())

def readyUp(gameName, playerName):
    games[gameName].about["clients"][playerName].about["ready"] = True
    checkGameState(gameName)

def serialReadBoard(gameName, clientName, positions=True):
    return games[gameName].serialReadBoard(clientName, positions)

def serialWriteBoard(gameName, clientName, serial):
    try:
        games[gameName].serialWriteBoard(gameName, clientName, serial)
        return True
    except Exception as e:
        return e

def getRemainingQuestions(gameName):
    return games[gameName].getAllMyClientsQuestions()

def randomiseBoard(gameName, clientName):
    return games[gameName].about["clients"][clientName].buildRandomBoard()

def FRONTresponse(gameName, clientName, choice):
    games[gameName].about["clients"][clientName].FRONTresponse(choice)
    if games[gameName].about["status"][-1] != "paused":
        games[gameName].turnHandle()
    else:
        print("The response was recorded, but no turn processing was carried out due to the game being paused.")
    

def filterClients(gameName, requirements, clients=[]):
    return games[gameName].filterClients(requirements, clients)

def filterEvents(gameName, requirements={}, parses=[], returnNums=False, events=[]):
    if events == []:
        events = games[gameName].about["eventHandler"].about["log"]
    return games[gameName].about["eventHandler"].filterEvents(events, requirements, parses, returnNums)

def describeEvents(gameName, events):
    return games[gameName].about["eventHandler"].describe(events)

def sortEvents(gameName, key, events=None):
    if events == None:
        return games[gameName].about["eventHandler"].sortEvents(games[gameName].about["eventHandler"].about["log"], key)
    else:
        return games[gameName].about["eventHandler"].sortEvents(events, key)

def shownToClient(gameName, playerName, timestamps):
    eventNums = games[gameName].about["eventHandler"].filterEvents(games[gameName].about["eventHandler"].about["log"], {}, ['event["timestamp"] in ' + str(timestamps)], True)
    for eN in eventNums:
        games[gameName].about["eventHandler"].about["log"][eN]["whoToShow"].remove(playerName)
        #print(games[gameName].about["eventHandler"].about["log"][eN]["whoToShow"])

#Change the attributes of a client or several by game name
# eg: alterClients("game1", ["Jamie"], {"name":"Gemima"})
#this would change the name of Jamie to Gemima.
#nameUniqueFilter, nameNaughtyFilter, turnTime
def alterClients(gameName, clientNames, alterations):
    success = []
    for clientName in clientNames:
        if clientName in games[gameName].about["clients"]:
            for key,value in alterations.items():
                #if key in games[gameName].about["clients"][clientName].about:
                games[gameName].about["clients"][clientName].about[key] = value
                #else:
                    #success.append("Key: " + str(key) + " doesn't exist for value " + str(value) + " to be assigned to.")
        else:
            for a in alterations.items():
                success.append("Client" + clientName + "doesn't exist.")

#Change the attributes of a game or several, 
# eg: alterGames(["game1"], {"name":"game2"})
#this would change the name of game1 to game2.
def alterGames(gameNames, alterations):
    success = []
    for gameName in gameNames:
        if gameName in games:
            for key,value in alterations.items():
                #if key in games[gameName].about:
                games[gameName].about[key] = value
                success.append(True)
                #else:
                    #success.append("Key", key, "doesn't exist for value", value, "to be assigned to.")
        else:
            for a in alterations.items():
                success.append("Game", gameName, "doesn't exist.")
    return success

def getDataFromStoredGame(boardStorage):
    admins = boardStorage[0]["admins"]
    gridDim = boardStorage[0]["gridDim"]
    turnTime = boardStorage[0]["turnTime"]
    playerCap = boardStorage[0]["playerCap"]
    nameUniqueFilter = boardStorage[0]["nameUniqueFilter"]
    nameNaughtyFilter = boardStorage[0]["nameNaughtyFilter"]
    debug = boardStorage[0]["debug"]
    gameName = boardStorage[0]["name"]
    quickplay = boardStorage[0]["quickplay"]
    live = boardStorage[0]["live"]
    randomiseOnly = boardStorage[0]["randomiseOnly"]
    gameLoop = boardStorage[0]["gameLoop"]
    gameAbout = {"gameName":gameName, "gameLoop":gameLoop, "quickplay":quickplay, "live":live, "debug":debug, "admins":admins, "gridDim":gridDim, "turnTime":turnTime, "playerCap":playerCap, "nameUniqueFilter":nameUniqueFilter, "nameNaughtyFilter":nameNaughtyFilter, "randomiseOnly":randomiseOnly}
    return gameAbout

def loadGame(boardStorage):
    #try:
    gameAbout = getDataFromStoredGame(boardStorage)
    overwriteAbout = boardStorage[0]
    gameAbout["live"] = False
    overwriteAbout["live"] = False
    #overwriteAbout["sims"] = []
    makeGame(gameAbout, overwriteAbout)["gameName"]
    #except Exception as e:
        #print(boardStorage[0]["name"], "@@@@ FAILED GAME RECOVERY (it might be using a different .about format):", e)

def bootstrap(about):
    #Loading games that are "running", stored in boards.npy in case the backend crashes or something.
    def failLoad(exception):
        debugPrint("@@@@ No games were loaded because: " + str(exception))
        BOARDS = {}
        np.save("boards.npy", BOARDS)
    try:
        #f = open("boards.npy")
        if os.path.getsize("boards.npy") > 0:
            try:
                BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
                if len(BOARDS.keys()) == 0:
                    failLoad("there are no games in boards.npy")
                for gameName in BOARDS:
                    loadGame(BOARDS[gameName])
            except Exception as e:
                failLoad(e)
        else:
            failLoad("file is empty")
    except Exception as e:
        failLoad(e)
    
    #And then deleting all those recovered games, because they're not necessary to test one new game.
    if about["purge"]:
        if len(games.keys()) > 0:
            deleteGame([key for key in games])
        else:
            debugPrint("@@@@ Failed to load games, so boards.npy was nuked.")
            BOARDS = {}
            np.save("boards.npy", BOARDS)

########################################################################################################################################################################################################
# .___   .____  __   __   ___  
# /   `  /      |    |  .'   `.
# |    | |__.   |\  /|  |     |
# |    | |      | \/ |  |     |
# /---/  /----/ /    /   `.__.'
### Used for debugging and testing of the overall structure of how a game should operate in relation to the backend. ###
########################################################################################################################################################################################################

def demo():
    debug = True
    print("! TESTBENCH !")
    print("Note: this is not able to communicate with the live or local website!")
    print("An infinite testbench will be run, if there is a turn processing problem it should halt after the predefined 'handleCap'.")
    print("Commence? (hit enter)")
    shallIDemo = input()
    demo = True
    c = 0
    d = 0
    noCrash = True
    while demo and noCrash:
        #Let's set up a few variables about our new test game...
        gridDim = (15,15)
        gridSize = gridDim[0] * gridDim[1]
        turnCount = gridSize + 1 #maximum of gridSize + 1
        admins = [{"name":"Jamie", "type":"AI"}] #this person is auto added.
        gameName = "Test-Game " + str(time.time())[-6:]
        turnTime = 5
        playerCap = 5
        nameNaughtyFilter = None
        nameUniqueFilter = None
        randomiseOnly = False
        live = False #If true, the game loop is used, if false, the code below will trigger turns.
        gameLoop = True

        #Setting up a test game
        about = {"gameName":gameName, "quickplay":False, "live":live, "gameLoop":gameLoop, "admins":admins, "gridDim":gridDim, "turnTime":turnTime, "playerCap":playerCap, "nameUniqueFilter":nameUniqueFilter, "nameNaughtyFilter":nameNaughtyFilter, "debug":debug, "randomiseOnly":randomiseOnly}
        makeGame(about)

        #Adding each of the imaginary players to the lobby sequentially.
        clients = [{"name":"Tom", "type":"human"}, {"name":"Alex", "type":"human"}] #Player name, then info about them which currently consists of whether they're playing.
        joinLobby(gameName=gameName, clients=clients)
        #print("joining clients to the lobby", joinLobby(gameName=gameName, clients=clients)) #This will create all the new players listed above so they're part of the gameHandler instance as individual clientHandler instances.
        #In future, when a user decides they don't want to play but still want to be in a game, the frontend will have to communicate with the backend to tell it to replace the isPlaying attribute in self.game.about["clients"][client].about
        
        #clients = [{"name":"Jamie", "type":"human"}] #This is to verify that duplicate usernames aren't allowed.
        #print("joining a dupe client to the lobby", joinLobby(gameName=gameName, clients=clients))


        #Kicking one of the imaginary players. (regardless of whether the game is in lobby or cycling turns)
        #print("exiting client from the lobby", leave(gameName, ["Jamie"]))

        #Simulating the interaction with the vue server, pinging the processing of each successive turn like the Vue server will every time it's happy with client responses turn-by-turn.
        #print("Enter any key to iterate a turn...")
        #shallIContinue = input()

        c += 1
        print("=======")
        print("GAME NUMBER", c)
        print("TOTAL TURNS TESTED", d)
        print("=======")
        start(gameName)
        while status(gameName) != "dormant":

            for clientName, obj in gameInfo(gameName)["about"]["clients"].items():
                if len(obj.about["FRONTquestions"]) > 0:
                    choice = random.choice(obj.about["FRONTquestions"][0]["options"])
                    FRONTresponse(gameName, clientName, choice)

        #print("Enter any key to delete the game...")
        #shallIContinue = input()

        deleteGame([key for key in games])
        d += gridDim[0] * gridDim[1]
        for i in range(3):
            print("")

########################################################################################################################################################################################################
#███████╗██╗      █████╗ ███████╗██╗  ██╗
#██╔════╝██║     ██╔══██╗██╔════╝██║ ██╔╝
#█████╗  ██║     ███████║███████╗█████╔╝ 
#██╔══╝  ██║     ██╔══██║╚════██║██╔═██╗ 
#██║     ███████╗██║  ██║███████║██║  ██╗
#╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
########################################################################################################################################################################################################


def auth(playerName, gameName, code):
    try:
        secret = clientInfo({"gameName":gameName, "clientName":playerName})["about"]["authCode"]
    except Exception as e:
        print("FAIL AUTH. exception:", e)
        return False
    if code == secret:
        return True
    else:
        print("FAIL AUTH.", playerName, secret, code)
        return False

def isHost(gameName, playerName):
    hostName = gameInfo(gameName)["about"]["admins"][0]["name"]
    if playerName == hostName:
        return True
    else:
        return False

### SOCKET ROUTES...

@socketio.on('connect')
def Fconnect():
    CONNECTED_SOCKETS.inc()
    emit('response', {'data': 'Connected'})

@socketio.on('disconnect')
def FdisConnect():
    #remove from game
    CONNECTED_SOCKETS.dec()

##################################################################################################################

@socketio.on('looper')
def FLoop():
    print("Checking if games need nudging")
    print("current time: " + str(time.time()))
    print(schedule)
    for key, value in schedule.items():
        if value != None:
            if value < time.time():
                print("nudging game" + str(key))
                turnLoop(key)

###################################################################################################################

@socketio.on('createGame')
def FcreateGame(data):
    REQUEST.labels('/createGame').inc()

    gameName = data["gameName"]
    ownerName = data["ownerName"]
    Sizex = int(data["Sizex"])
    Sizey = int(data["Sizey"])
    isPlaying = data["isHostPlaying"]
    randomiseOnly = False
    playerCap = 12
    debug=True
    gridDim = (Sizex, Sizey)
    turnTime = 10
    nameUniqueFilter = True
    nameNaughtyFilter = True
    quickplay = False

    if gameName is None:
        gameName = ''
    if ownerName is None:
        ownerName = ''
    for char in gameName:
        if char not in string.ascii_letters:
            data = {"error": "Game name can only contain letters"}
            emit("createGameResponse", data)

    for char in ownerName:
        if char not in (string.ascii_letters + ' '):
            data = {"error": "Your name can only contain letters"}
            emit("createGameResponse", data)

    gameAbout = {"gameName":gameName, "admins":[{"name":ownerName, "type":"human"}], "gameLoop":True, "live":True, "quickplay":quickplay, "debug":debug, "gridDim":gridDim, "turnTime":turnTime, "playerCap":playerCap, "nameUniqueFilter":nameUniqueFilter, "nameNaughtyFilter":nameNaughtyFilter, "randomiseOnly": randomiseOnly}
    if not isPlaying:
        gameAbout["admins"] = [{"name":ownerName, "type":"spectator"}]
    out = makeGame(gameAbout) ###CREATING THE GAME.
    if not out:
        data = {"error": "could not create game"}
        emit("createGameResponse", data)
    else:
        gameName = out["gameName"]
        admins = out["admins"]

    join_room(gameName)
    alterClients(gameName, [ownerName], {"socket":request.sid})
    sendPlayerListToClients(gameName)

    authcode = clientInfo({"gameName":gameName, "clientName":admins[0]["name"]})["about"]["authCode"]
    
    data = {"error": False, "authcode": authcode, "playerName":admins[0]["name"], "gameName":gameName}
    emit("createGameResponse", data)

@socketio.on('joinGame')
def FjoinGame(data):
    REQUEST.labels('/joinGame').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]

    if len(gameName)<1:
        data = {"error": "Please enter a game name"}
        emit("joinGameResponse", data)
    if len(playerName)<1:
        data = {"error": "please enter a name"}
        emit("joinGameResponse", data)


    for char in gameName:
        if char not in string.ascii_letters:
            data = {"error": "Game name can only contain letters"}
            emit("joinGameResponse", data)

    for char in playerName:
        if char not in (string.ascii_letters + ' '):
            data = {"error": "Your name can only contain letters"}
            emit("joinGameResponse", data)


    if joinLobby(gameName, [{"name":playerName, "type":"human"}]):
        authcode = clientInfo({"gameName":gameName, "clientName":playerName})["about"]["authCode"]
        join_room(gameName)
        sendPlayerListToClients(gameName)
        alterClients(gameName, [playerName], {"socket":request.sid})
        data = {"error": False, "authcode": authcode}
        emit("joinGameResponse", data)
    else:
        data = {"error": "Something went wrong"}
        emit("joinGameResponse", data)

@socketio.on('getTiles')
def FgetTiles(data):
    REQUEST.labels('/getTiles').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    
    data = {"error": False, "tiles": serialReadBoard(gameName, playerName, positions=False)}

    emit("getTilesResponse", data)

@socketio.on('getGridDim')
def FgetGridDim(data):
    REQUEST.labels('/getGridDim').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]

    data = gameInfo(gameName)["about"]["gridDim"]
    out = {"error":False, "x": data[0], "y": data[1]}

    emit("getGridDimResponse", out)

@socketio.on('startGame')
def FstartGame(data):
    REQUEST.labels('/startGame').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            if start(gameName):
                data = ({"error":False})
                emit("startGameResponse", data)
            else:
                data = ({"error":"game not found"})
                emit("startGameResponse", data)
        else:
            data = ({"error":"You can't do this"})
            emit("startGameResponse", data)
    else:
        data = ({"error": "Authentication failed"})
        emit("startGameResponse", data)

@socketio.on('submitResponse')
def FsubmitResponse(data):
    REQUEST.labels('/submitResponse').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    choice = data["choice"]

    if auth(playerName, gameName, authCode):
        FRONTresponse(gameName, playerName, choice)

    data = {"error": False}
    emit("submitResponseResponse", data)

@socketio.on('modifyGame')
def FmodifyGame(data):
    REQUEST.labels('/modifyGame').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    naughty = data["naughty"]
    similar = data["similar"]
    turnTime = data["turnTime"]
    randomiseOnly = data["randomiseOnly"]
    playerCap = int(data["playerLimit"])

    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            alterGames([gameName], {"nameUniqueFilter":similar, "nameNaughtyFilter":naughty, "turnTime":turnTime, "playerCap": playerCap, "randomiseOnly": randomiseOnly})
            data = ({"error": False})
            emit("modifyGameResponse", data)
        else:
            data = ({"error": "You do not have permission to do this"})
            emit("modifyGameResponse", data)

    else:
        data = ({"error": "Authentication failed"})
        emit("modifyGameResponse", data)

@socketio.on('setTeam')
def FsetTeam(data):
    REQUEST.labels('/setTeam').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    
    print(playerName, gameName, authCode)
    Captain = data["Captain"]
    ship = ["A","B","C"][data["Ship"]]

    if auth(playerName, gameName, authCode):
        alterClients(gameName, [playerName], {"row": str(ship)}) #Ship
        alterClients(gameName, [playerName], {"column": str(Captain)}) #captain
        data = ({"error": False, "randomise":gameInfo(gameName)["about"]["randomiseOnly"]})
        emit("setTeamResponse", data)
    else:
        data = ({"error": "Authentication failed"})
        emit("setTeamResponse", data)
    return

@socketio.on('saveBoard')
def FsaveBoard(data):
    REQUEST.labels('/saveBoard').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    board = data["board"]

    if auth(playerName, gameName, authCode):
        if serialWriteBoard(gameName, playerName, board):
            readyUp(gameName, playerName)
            data = {"error": False}
            emit("saveBoardResponse", data)
        else:

            data = {"error": "board did not fit requirements"}
            emit("saveBoardResponse", data)
    else:
        data = ({"error": "Authentication failed"})
        emit("saveBoardResponse", data)

@socketio.on('randomiseBoard')
def FrandomiseBoard(data):
    REQUEST.labels('/randomiseBoard').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        randomiseBoard(gameName, playerName)

        board = serialReadBoard(gameName, playerName)
        emit("randomiseBoardResponse", {"error":False, "board":board})
    else:
        data = ({"error": "Authentication failed"})
        emit("randomiseBoardResponse", data)

@socketio.on('getBoard')
def FgetBoard(data):
    REQUEST.labels('/getBoard').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        data = {"error":False, "board":serialReadBoard(gameName, playerName)}
        emit("getBoardResponse", data)
    else:
        data = ({"error": "Authentication failed"})
        emit("getBoardResponse", data)
    
@socketio.on('amIHost')
def FamIHost(data):
    REQUEST.labels('/amIhost').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]

    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            data = ({"error": False})
            emit("amIHostResponse", data)
        else:
            data = ({"error": "You do not have permission to do this"})
            emit("amIHostResponse", data)

    else:
        data = ({"error": "Authentication failed"})
        emit("amIHostResponse", data)

@socketio.on('kickPlayer')
def FkickPlayer(data):
    REQUEST.labels('/kickPlayer').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    playerToKick = data["playerToKick"]
    
    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            if leave(gameName, [playerToKick]):
                sendPlayerListToClients(gameName)
                data = ({"error": False})
                emit("kickPlayerResponse", data)
            else:
                data = ({"error": "Player kick failed"})
                emit("kickPlayerResponse", data)
        else:
            data = ({"error": "You do not have permission to do this"})
            emit("kickPlayerResponse", data)

    else:
        data = ({"error": "Authentication failed"})
        emit("kickPlayerResponse", data)

@socketio.on('addAI')
def FaddAI(data):
    REQUEST.labels('/addAI').inc()

    gameName = data["gameName"]
    playerName = data["playerName"]
    authCode = data["authCode"]
    if auth(playerName, gameName, authCode):
        if isHost(gameName, playerName):
            if joinLobby(gameName=gameName, clients=[{"name":"", "type":"AI"}]):
                sendPlayerListToClients(gameName)
                data = ({"error": False})
                emit("addAIResponse", data)
            else:
                data = ({"error": "adding AI failed"})
                emit("addAIResponse", data)
        else:
            data = ({"error": "You do not have permission to do this"})
            emit("addAIResponse", data)

    else:
        data = ({"error": "Authentication failed"})
        emit("addAIResponse", data)

@socketio.on('requestGameState')
def FrequestGameState(data):
    REQUEST.labels('/requestGameState').inc()

    gameName = data["gameName"]
    checkGameState(gameName)

@socketio.on('requestPlayerList')
def FrequestPlayerList(data):
    REQUEST.labels('/requestPlayerList').inc()

    gameName = data["gameName"]
    sendPlayerListToClients(gameName)

@socketio.on('requestLeaderboard')
def FrequestLeaderboard(data):
    REQUEST.labels('/requestLeaderboard').inc()

    gameName = data["gameName"]
    LB = leaderboard(gameName)
    data = ({"error": False, "leaderboard": LB})
    emit("leaderboard", data)

@socketio.on('requestAllEvents')
def retrieveEventList(gameName, playerName):
    REQUEST.labels('/requestAllEvents').inc()

    events = games[gameName].about["eventLogs"][playerName]
    emit("requestAllEventsResponse", events)

@socketio.on_error()
def chat_error_handler(e):
    ERROR.inc()
    print('An error has occurred: ' + str(e))

#Functions that send the client data to update them.

def sendPlayerListToClients(gameName):
    print("sending player list to clients")
    session = gameInfo(gameName)
    if session == False:
        data = {"error": "game not found"}
        emit("playerList", data, room=gameName)
    
    clientList = listClients(gameName)
    print(clientList)
    toSend = []
    for clientName,about in clientList.items():
        text = str(about["type"]) + ": " + str(clientName)
        toSend.append(text)
    data = {"error": False, "names":toSend}
    emit("playerList", data, namespace='/', room=gameName)

def sendGameStatusToClient(gameName, data):
    emit("status", data, namespace='/', room=gameName)

def sendQuestionToClient(gameName, playerName, data):
    #data = {"labels":["this is the question", "this is the instrusctions"], "options":[]}
    emit("Question", data, namespace='/', room=clientInfo({"gameName":gameName, "clientName":playerName})["about"]["socket"])

def turnUpdate(gameName, playerName, descriptions):
    tiles = gameInfo(gameName)["about"]["chosenTiles"]
    width = gameInfo(gameName)["about"]["gridDim"][1]
    ids = []
    #print(tiles)
    for turn in tiles:
        ids.append((tiles[turn][1] * width) + tiles[turn][0])
    
    
    money = clientInfo({"gameName":gameName, "clientName": playerName})["about"]["money"]
    bank = clientInfo({"gameName":gameName, "clientName": playerName})["about"]["bank"]
    shield = clientInfo({"gameName":gameName, "clientName": playerName})["about"]["shield"]
    mirror = clientInfo({"gameName":gameName, "clientName": playerName})["about"]["mirror"]

    data = {"error": False, "events": descriptions, "ids":ids, "money": money, "bank": bank, "shield": shield, "mirror": mirror}
    emit("turn", data, namespace='/', room=clientInfo({"gameName":gameName, "clientName":playerName})["about"]["socket"])


def GotoLeaderboard(gameName):
    emit("End", namespace='/', room=gameName)

########################################################################################################################################################################################################
#███╗   ███╗ █████╗ ██╗███╗   ██╗    ████████╗██╗  ██╗██████╗ ███████╗ █████╗ ██████╗ 
#████╗ ████║██╔══██╗██║████╗  ██║    ╚══██╔══╝██║  ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗
#██╔████╔██║███████║██║██╔██╗ ██║       ██║   ███████║██████╔╝█████╗  ███████║██║  ██║
#██║╚██╔╝██║██╔══██║██║██║╚██╗██║       ██║   ██╔══██║██╔══██╗██╔══╝  ██╔══██║██║  ██║
#██║ ╚═╝ ██║██║  ██║██║██║ ╚████║       ██║   ██║  ██║██║  ██║███████╗██║  ██║██████╔╝
#╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ 
########################################################################################################################################################################################################

if __name__ == "__main__":
    print("-" * 50)
    print("Pirate Game 2.0 Early Development Branch")
    print("If the program crashes, check the known issues section on our Github. If the crash doesn't appear to be there, please add it!")
    print("-" * 50)

    bootstrap({"purge":True})
    subprocess.Popen(["python","./looper.py"])
    socketio.run(app, debug=False, host="0.0.0.0")