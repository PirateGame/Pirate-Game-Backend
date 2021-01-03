import time

class gameEventHandler():
    def __init__(self, game):
        self.game = game
        self.about = {"log":[]}
    
    def sortEvents(self, events, key): # sortEvents(games[gameName].about["eventHandler"].about["log"], "timestamp")
        return sorted(events, key=lambda k: k[key])
    
    def filterEvents(self, events, requirements, parses=[], returnNums=False): #eg: filterEvents(games[gameName].about["eventHandler"].about["log"], {"timestamp":timestamp})
        out = []
        outNums = []
        outNum = -1
        for event in events:
            outNum += 1
            success = []
            for key,value in requirements.items():
                if value == event[key]:
                    success.append(True)
                else:
                    success.append(False)
            for p in parses:
                try:
                    if eval(p):
                        success.append(True)
                    else:
                        success.append(False)
                except Exception as e:
                    print(e)
                    pass
            if False not in success:
                out.append(event)
                outNums.append(outNum)
        if returnNums:
            return outNums
        else:
            return out
    
    def describe(self, events):
        self.eventDescriptions = {"A":"robbed",
                                "B":"killed",
                                "C":"gave a present to",
                                "D":"skulled and crossboned",
                                "E":"swapped with",
                                "F":"chose the next square",
                                "G":"gained a shield",
                                "H":"gained a mirror",
                                "I":"got bombed",
                                "J":"doubled their cash",
                                "K":"banked their cash",
                                "5000":"gave £5000 to",
                                "3000":"gave £3000 to",
                                "1000":"gave £1000 to",
                                "200":"gave £200 to"}
        out = []
        for event in events:
            for targetNum in range(len(event["targetNames"])):
                for sourceNum in range(len(event["sourceNames"])):
                    if event["isMirrored"]:
                        out.append(str(event["sourceNames"][sourceNum]) + " -> " + self.eventDescriptions[str(event["event"])] + " -> " + str(event["targetNames"][targetNum]) + " (mirror)")
                    elif event["isShielded"]:
                        out.append(str(event["sourceNames"][sourceNum]) + " -> " + self.eventDescriptions[str(event["event"])] + " -> " + str(event["targetNames"][targetNum]) + " (shield)")
                    else:
                        out.append(str(event["sourceNames"][sourceNum]) + " -> " + self.eventDescriptions[str(event["event"])] + " -> " + str(event["targetNames"][targetNum]))
        return out
    
    def updateEvents(eventNums, updates):
        for eventNum in eventNums:
            for key,value in updates.items():
                self.about["log"][eventNum][key] = value
    
    def printNicely(self, event):
        if event["public"]:
            desc = self.describe([event])
            for line in desc:
                print(line)
        else:
            print("EVENT:", event)
    
    def make(self, about): #{"event":whatHappened, "sources":[self], "targets":[self.game.about["clients"][choice]], "other":[]}
        self.about["log"].append({"shownToClient":False, "timestamp":time.time(), "turnNum":self.game.about["turnNum"], "public":about["public"], "event":about["event"], "sources":about["sources"], "sourceNames":[source.about["name"] for source in about["sources"]], "targets":about["targets"], "targetNames":[target.about["name"] for target in about["targets"]], "isMirrored":about["isMirrored"], "isShielded":about["isShielded"], "other":about["other"]})
        #self.printNicely(self.about["log"][-1])
        #self.game.processEvent
        return self.about["log"][-1]

class clientEstimateHandler():
    def __init__(self, client):
        self.client = client
        self.about = {"knownTiles":[]}
    
    def estimate(self):
        pass