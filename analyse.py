gridSize = 7*7
for i in range(1000):
    a = ''.join(random.choice(string.ascii_letters) for x in range(gridSize))
    b = ''.join(random.randint(0,20000) for x in range(gridSize))

def forecast(self, iterations=0):
    BOARDS = np.load("boards.npy", allow_pickle=True).tolist()
    boardStorage = BOARDS[self.about["name"]]
    startTime = time.time()
    gameAbout = getDataFromStoredGame(boardStorage)
    overwriteAbout = boardStorage[0]
    overwriteAbout["debug"] = False
    overwriteAbout["isSim"] = True
    overwriteAbout["debug"] = False
    for clientName in overwriteAbout["clients"]:
        overwriteAbout["clients"][clientName].about["type"] = "AI"
        overwriteAbout["clients"][clientName].about["FRONTquestions"] = []
    for i in range(iterations):
        self.about["sims"].append(gameHandler(gameAbout, overwriteAbout))
        print("New sim made.")
        while self.about["sims"][-1].about["status"][-1] != "dormant":
            print("ITERATION", i, "TURN", self.about["sims"][-1].about["turnNum"], "HANDLE", self.about["sims"][-1].about["handleNum"])
            self.about["sims"][-1].turnHandle() 
    #print("FORECAST TIMED TO:", time.time() - startTime)