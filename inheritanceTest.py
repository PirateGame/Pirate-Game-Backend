class game():
    def __init__(self, gameName):
        self.gameName = gameName
class client(game):
    def __init__(self, clientName, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clientName = clientName
    def printGame(self):
        print(self.gameName)
g = game("Game1")
c = client("Jamie")
c.printGame()