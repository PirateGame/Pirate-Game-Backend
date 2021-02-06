import app

def updateClientStatus(data):
    app.sendPlayerListToClients(data)

def updateClientEvent(data, group,gameName, playerName=None):
    app.sendUpdateToClient(gameName, playerName, group, data)

def sendTurn(gameName, playerName):
    app.turnUpdate(gameName, playerName)