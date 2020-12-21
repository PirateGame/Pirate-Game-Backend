class game():
    def __init__(self, gameName):
        self.gameName = gameName
        self.clients = {}
    def makeClient(self, clientName):
        self.clients[clientName] = (client(self, clientName))
        
class client():
    def __init__(self, game, clientName):
        self.game = game
        self.clientName = clientName
    def whoIsMyOwner(self):
        print(self.game.gameName)

g = game("Game1")
g.makeClient("Jamie")
g.clients["Jamie"].whoIsMyOwner()
