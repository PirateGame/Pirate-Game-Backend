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
                                "F":"chose the square for",
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
            ownerClass = event["owner"].__class__.__name__
            turnStr = str(event["turnNum"] + 1)
            if ownerClass == "gameHandler":
                if event["event"] == "newTurn":
                    out.append("~TURN" + turnStr + "~")
                if event["event"] == "start":
                    out.append("~THE GAME HAS STARTED~")
                if event["event"] == "pause":
                    out.append("~PAUSED~")
                if event["event"] == "resume":
                    out.append("~RESUMED~")
                if event["event"] == "end":
                    out.append("~THE GAME HAS ENDED~")
                if event["event"] == "leaderboard":
                    out.append("Leaderboard: " + str(event["other"]))
                if event["event"] == "delete":
                    out.append("~THE GAME HAS BEEN DELETED")
            elif ownerClass == "clientHandler":
                targetLst = []
                for targetNum in range(len(event["targetNames"])):
                    targetClass = event["targetNames"][targetNum].__class__.__name__
                    if targetClass == "gameHandler":
                        targetClass = "game"
                        targetType = "game"
                    else:
                        targetClass = "client"
                        targetType = event["targets"][targetNum].about["type"]
                    targetLst.append(targetType + ":" + event["targetNames"][targetNum])
                if len(targetLst) == 0:
                    targetLst.append("no one")
                sourceLst = []
                for sourceNum in range(len(event["sourceNames"])):
                    sourceClass = event["sources"][sourceNum].__class__.__name__
                    if sourceClass == "gameHandler":
                        sourceClass = "game"
                        sourceType = "game"
                    else:
                        sourceClass = "client"
                        sourceType = event["sources"][sourceNum].about["type"]
                    sourceLst.append(sourceType + ":" + event["sourceNames"][sourceNum])
                if len(sourceLst) == 0:
                    sourceLst.append("no one")
                
                targetStr = ",".join(targetLst)
                sourceStr = ",".join(sourceLst)
                mirrorStr = ""
                shieldStr = ""
                if event["isMirrored"]:
                    mirrorStr = "(MIRRORED)"
                elif event["isShielded"]:
                    shieldStr = "(SHIELDED)"
                elif event["event"] == "A":
                    if len(event["other"]) > 0:
                        out.append(sourceStr + " robbed " + str(event["other"][0]) + str(" from ") + targetStr + mirrorStr + shieldStr)
                    else:
                        out.append(sourceStr + " tried to rob " + targetStr + mirrorStr + shieldStr)
                elif event["event"] == "B":
                    if len(event["other"]) > 0:
                        out.append(sourceStr + " killed " + targetStr + mirrorStr + shieldStr)
                    else:
                        out.append(sourceStr + " tried to kill " + targetStr + mirrorStr + shieldStr)
                elif event["event"] == "C":
                    if len(event["other"]) > 0:
                        out.append(sourceStr + " gave a present of " + str(event["other"][0]) + str(" to ") + targetStr + mirrorStr + shieldStr)
                    else:
                        out.append(sourceStr + " tried to give a present to " + targetStr + mirrorStr + shieldStr)
                        #out.append(sourceStr + " tried to give a present of", event["other"], to " + targetStr + mirrorStr + shieldStr)
                elif event["event"] == "E":
                    out.append(sourceStr + " swapped " + str(event["other"][0]) + str(" with ") + str(event["other"][1]) +str(" from ") + targetStr + mirrorStr + shieldStr)
                elif event["event"] == "F":
                    out.append(sourceStr + " chose the next tile: " + str((event["other"][0][1] + 1, event["other"][0][0] + 1)))
                else:
                    out.append(sourceStr + " " + self.eventSentenceFillers[str(event["event"])] + " " + targetStr + mirrorStr + shieldStr)
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
        self.about["log"].append({"timestamp":time.time(), "owner":about["owner"], "turnNum":self.game.about["turnNum"], "public":about["public"], "event":about["event"], "sources":about["sources"], "sourceNames":[source.about["name"] for source in about["sources"]], "targets":about["targets"], "targetNames":[target.about["name"] for target in about["targets"]], "isMirrored":about["isMirrored"], "isShielded":about["isShielded"], "other":about["other"]})
        self.about["log"][-1]["whoToShow"] = self.whoToShow(self.about["log"][-1])
        #print("EVENT MADE.", self.about["log"][-1])
        #self.printNicely(self.about["log"][-1])
        #self.game.processEvent
        return self.about["log"][-1]

class clientEstimateHandler():
    def __init__(self, client):
        self.client = client
        self.about = {"knownTiles":[]}
    
    def estimate(self):
        pass