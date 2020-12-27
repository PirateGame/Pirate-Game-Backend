import time

class gameEventHandler():
    def __init__(self, game):
        self.game = game
        self.about = {"privateLog":[], "publicLog":[]}
    
    def sortEvents(self, key):
        return sorted(self.about["log"], key=lambda k: k[key])[-1]
    
    def filterEvents(self, requirements, parses=[]): #eg: filterEvents({"timestamp":timestamp})
        out = {}
        for event in self.about["log"]:
            success = []
            for key,value in requirements:
                if value == requirement:
                    success.append(True)
                else:
                    success.append(False)
            for p in parses:
                try:
                    if eval(p):
                        success.append(True)
                    else:
                        success.append(False)
                except:
                    pass
            if False not in success:
                out[event] = self.about["log"][event]
        return out
    
    def describe(self, event):
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
                                "K":"banked their cash"}
        out = []
        for targetNum in range(len(event["targets"])):
            for sourceNum in range(len(event["sources"])):
                out.append(str(event["sources"][sourceNum].about["name"]) + " -> " + self.eventDescriptions[event["event"]] + " -> " + str(event["targets"][targetNum].about["name"]))
        return out
    
    def printNicely(self, event):
        desc = self.describe(event)
        for line in desc:
            print(line)
    
    def make(self, about): #{"event":whatHappened, "sources":[self], "targets":[self.game.about["clients"][choice]], "other":[]}
        if about["public"]:
            self.about["publicLog"].append({"timestamp":time.time(), "turnNum":self.game.about["turnNum"], "public":about["public"], "event":about["event"], "sources":about["sources"], "targets":about["targets"], "isMirrored":about["isMirrored"], "isShielded":about["isShielded"], "other":about["other"]})
            self.printNicely(self.about["publicLog"][-1])
            #self.game.processEvent
            return self.about["publicLog"][-1]
        else:
            self.about["privateLog"].append({"timestamp":time.time(), "turnNum":self.game.about["turnNum"], "public":about["public"], "event":about["event"], "sources":about["sources"], "targets":about["targets"], "isMirrored":about["isMirrored"], "isShielded":about["isShielded"], "other":about["other"]})
            return self.about["privateLog"][-1]

class clientEstimateHandler():
    def __init__(self, client):
        self.client = client
        self.about = {"knownTiles":[]}
    
    def estimate(self):
        filterEvents({"sources":[self.client.about["name"]]})