import time

class gameEventHandler():
    def __init__(self, game):
        self.game = game
        self.about = {"log":[]}
    
    def sortEvents(self, key):
        return sorted(self.about["log"], key=lambda k: k[key])[-1]
    
    def filterEvents(self, requirements, parses=[]):
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
    
    def printNicely(self, event):
        pass
    
    def make(self, about): #{"event":whatHappened, "source":self, "targets":[self.game.about["clients"][choice]], "other":[]}
        self.about["log"].append({"timestamp":time.time(), "turnNum":self.game.about["turnNum"], "event":about["event"], "source":about["source"], "targets":about["targets"], "other":about["other"]})
        print("event:", self.about["log"][-1])
        return self.about["log"][-1]

class gameEstimateHandler():
    def __init__(self, client):
        self.client = client
        self.about = {"knownTiles":[]}
    
    def takeEvent(about):
        print(about[""])