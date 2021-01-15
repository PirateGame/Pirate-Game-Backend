import time

class gameEventHandler():
    def __init__(self, game):
        self.game = game
        self.about = {"log":[]}
        self.eventDescriptions = {"A":"Rob",
                                "B":"Kill",
                                "C":"Present",
                                "D":"Skull and Crossbones",
                                "E":"Swap",
                                "F":"Choose Next Square",
                                "G":"Shield",
                                "H":"Mirror",
                                "I":"Bomb",
                                "J":"Double Cash",
                                "K":"Bank",
                                "5000":"gave £5000 to",
                                "3000":"gave £3000 to",
                                "1000":"gave £1000 to",
                                "200":"gave £200 to"}
        self.eventDescriptionsForSource = {"A":"Rob (Steal someone's balance)",
                                "B":"Kill (Make someone's balance AND bank go to 0)",
                                "C":"Present (Give someone 1000 of YOUR OWN cash)",
                                "D":"Skull and Crossbones (make 3 people's stashes go to 0)",
                                "E":"Swap (Swap balances with one other player)",
                                "F":"Choose Next Square (Have a guess!)",
                                "G":"Shield (Gain a shield - stops an action happening to you)",
                                "H":"Mirror (Gain a mirror - reflects the action as if you are doing it to the person who did it to you)",
                                "I":"Bomb (Your balance goes to 0)",
                                "J":"Double Cash (Your balance is doubled)",
                                "K":"Bank (Your balance is added to your bank, and then goes to 0)",
                                "5000":"gave £5000 to",
                                "3000":"gave £3000 to",
                                "1000":"gave £1000 to",
                                "200":"gave £200 to"}
        self.eventSentenceFillers = {"A":"robbed",
                                "B":"killed",
                                "C":"gave a present to",
                                "D":"skulled and crossboned",
                                "E":"swapped with",
                                "F":"delegated the square choice to",
                                "G":"gave a shield to",
                                "H":"gave a mirror to",
                                "I":"bombed",
                                "J":"doubled the cash of",
                                "K":"banked the cash of",
                                "5000":"gave £5000 to",
                                "3000":"gave £3000 to",
                                "1000":"gave £1000 to",
                                "200":"gave £200 to"}
    
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
        out = []
        for event in events:
            for targetNum in range(len(event["targetNames"])):
                for sourceNum in range(len(event["sourceNames"])):
                    sourceClass = event["sources"][sourceNum].__class__.__name__
                    if sourceClass == "gameHandler":
                        sourceClass = "game"
                        sourceType = "Game"
                    else:
                        sourceClass = "client"
                        sourceType = event["sources"][sourceNum].about["type"]
                    if event["isMirrored"]:
                        out.append("(" + str(sourceType) + ")" + str(event["sourceNames"][sourceNum]) + " " + self.eventSentenceFillers[str(event["event"])] + " " + str(event["targetNames"][targetNum]) + " (mirror)")
                    elif event["isShielded"]:
                        out.append("(" + str(sourceType) + ")" + str(event["sourceNames"][sourceNum]) + " " + self.eventSentenceFillers[str(event["event"])] + " " + str(event["targetNames"][targetNum]) + " (shield)")
                    elif event["event"] == "E":
                        out.append("(" + str(sourceType) + ")" + str(event["sourceNames"][sourceNum]) + "swapped" + str(event["other"][0]) + str("with") + str(event["other"][1]) +str("from") + str(event["targetNames"][targetNum]))
                    else:
                        out.append("(" + str(sourceType) + ")" + str(event["sourceNames"][sourceNum]) + " " + self.eventSentenceFillers[str(event["event"])] + " " + str(event["targetNames"][targetNum]))
        return out
    
    def updateEvents(self, eventNums, updates):
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
    
    def whoToShow(self, event):
        if event["public"] == True:
            out = []
            for clientName,obj in self.game.filterClients({}, []).items():
                if obj.__class__.__name__== "clientHandler" and obj.about["type"] == "human":
                    out.append(clientName)
            return out
        else:
            out = []
            people = event["sources"] + event["targets"]
            pDict = {}
            for person in people:
                pDict[person.about["name"]] = person
            for clientName,obj in pDict.items():
                if obj.__class__.__name__== "clientHandler" and obj.about["type"] == "human":
                    out.append(clientName)
            return out

    def make(self, about): #{"event":whatHappened, "sources":[self], "targets":[self.game.about["clients"][choice]], "other":[]}
        time.sleep(0.00001)
        self.about["log"].append({"timestamp":time.time(), "turnNum":self.game.about["turnNum"], "public":about["public"], "event":about["event"], "sources":about["sources"], "sourceNames":[source.about["name"] for source in about["sources"]], "targets":about["targets"], "targetNames":[target.about["name"] for target in about["targets"]], "isMirrored":about["isMirrored"], "isShielded":about["isShielded"], "other":about["other"]})
        self.about["log"][-1]["whoToShow"] = self.whoToShow(self.about["log"][-1])
        #self.printNicely(self.about["log"][-1])
        #self.game.processEvent
        return self.about["log"][-1]

class clientEstimateHandler():
    def __init__(self, client):
        self.client = client
        self.about = {"knownTiles":[]}
    
    def estimate(self):
        pass