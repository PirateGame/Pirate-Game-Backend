import random
import numpy as np
from scipy import optimize

def gridSizeToActionCount(gridSize):
    if gridSize <= 25:
        return 1
    else:
        return round((gridSize + 12.5) / 25) - 1
    
class grid():
    def __init__(self, gridDim):
        self.eventDescriptions = {"A":"Rob",
                                "B":"Kill",
                                "C":"Present",
                                "D":"Skull and Crossbones",
                                "E":"Swap",
                                "F":"Choose Next Square",
                                "G":"Shield",
                                "H":"Mirror",
                                "I":"Bomb",
                                "J":"Double",
                                "K":"Chest"}

        ### Build an optimised blueprint for grid building
        gridSize = gridDim[0] * gridDim[1]
        mA = int(np.ceil(gridSize * (1/49)))
        mB = int(np.ceil(gridSize * (2/49)))
        mC = int(np.ceil(gridSize * (10/49)))
        mD = int(np.ceil(gridSize * (25/49)))
        actionCount = gridSizeToActionCount(gridSize)
        totalActionCount = actionCount * 11
        
        def toMinimize(mA, mB, mC, mD, mAs, mBs, mCs, mDs): #The difference between the average monetary value of what the board should have been, and what it is now that tiles are being removed. This needs to be minimized to maintain the economy regardless of board size.
            return np.abs((((5000*(mA-mAs))+(3000*(mB-mBs))+(1000*(mC-mCs))+(200*(mD-mDs))) / ((mA-mAs)+(mB-mBs)+(mC-mCs)+(mD-mDs))) - ((((mA)*5000)+((mB)*3000)+((mC)*1000)+((mD)*200)) / (mA+mB+mC+mD))) 

        total = (mA + mB + mC + mD + totalActionCount) - gridSize
        minimum = toMinimize(mA, mB, mC, mD, total, 0, 0, 0)
        minimumInputs = [total,0,0,0]
        for mAs in range(total): #This tests all the possible board tile removal combinations.
            mAs += 1
            for mBs in range(total-mAs):
                mBs += 1
                for mCs in range(total-mAs-mBs):
                    mCs += 1
                    for mDs in range(total-mAs-mBs-mCs):
                        mDs += 1
                        if mAs + mBs + mCs + mDs == total:
                            result = toMinimize(mA, mB, mC, mD, mAs, mBs, mCs, mDs)
                            if result < minimum:
                                minimum = result
                                minimumInputs = [mAs, mBs, mCs, mDs]
        mA -= minimumInputs[0] #Remove the optimal combination from each type of money tile.
        mB -= minimumInputs[1]
        mC -= minimumInputs[2]
        mD -= minimumInputs[3]

        tileNums = {}
        for letter in ["A","B","C","D","E","F","G","H","I","J","K"]:
            tileNums[letter] = actionCount
        tileNums["5000"] = mA
        tileNums["3000"] = mB
        tileNums["1000"] = mC
        tileNums["200"] = mD
        self.about = {"tileNums":tileNums, "actionCount":actionCount, "totalActionCount":totalActionCount, "gridDim":gridDim, "gridSize":gridSize}

    def build(self):
        gridDim = self.about["gridDim"][::-1]
        #gridDim = (10,10)

        array = [[None for y in range(gridDim[1])] for y in range(gridDim[0])]

        coords = []
        for x in range(gridDim[0]):
            for y in range(gridDim[1]):
                coords.append((x,y))
        random.shuffle(coords)

        mA = self.about["tileNums"]["5000"]
        mB = self.about["tileNums"]["3000"]
        mC = self.about["tileNums"]["1000"]
        mD = self.about["tileNums"]["200"]

        mAc = coords[:mA]
        mBc = coords[mA:mB+mA]
        mCc = coords[mB+mA:mC+mB+mA]
        mDc = coords[mC+mB+mA:mD+mC+mB+mA]
        mEc = coords[mD+mC+mB+mA:]

        for c in range(len(mAc)):
            array[coords[c][0]][coords[c][1]] = "5000"
        for c in range(len(mBc)):
            c += len(mAc) 
            array[coords[c][0]][coords[c][1]] = "3000"
        for c in range(len(mCc)):
            c += len(mAc) + len(mBc)
            array[coords[c][0]][coords[c][1]] = "1000"
        for c in range(len(mDc)):
            c += + len(mAc) + len(mBc) + len(mCc)
            array[coords[c][0]][coords[c][1]] = "200"
        for c in range(0, 11*self.about["actionCount"], self.about["actionCount"]):
            c += len(mAc) + len(mBc) + len(mCc) + len(mDc)
            for ac in range(self.about["actionCount"]):
                array[coords[c+ac][0]][coords[c+ac][1]] = chr(65 + ((c - (len(mAc) + len(mBc) + len(mCc) + len(mDc)))//self.about["actionCount"]))
        
        return array #Return a list with the array and then a dictionary with all the important stuff.
    
    def serialReadBoard(self, array, positions):
        serialFile = []

        for x in range(self.about["gridDim"][0]):
            for y in range(self.about["gridDim"][1]):
                id = (y * self.about["gridDim"][1]) + x
                tile = array[y][x]
                if not tile.isdigit():
                    content = self.eventDescriptions[tile] #"<br>"+self.eventDescriptions[tile]+"<br>"
                else:
                    content = str(tile) #"<br>"+str(tile)+"<br>"
                if positions:
                    serialFile.append({"x":x, "y":y, "w":1, "h":1, "id":id, "content":content, "noResize": True, "noMove":False})
                else:
                    serialFile.append({"id":id, "content":content, "noResize": True, "noMove":False})

        return serialFile
    
    def serialWriteBoard(self, array, serial):
        tileTally = {}
        toAdd = []
        for tile in serial:
            if not tile["content"].isdigit():
                for key,value in self.eventDescriptions.items():
                    if value == tile["content"]:
                        event = key
            else:
                event = tile["content"]
            if not event in tileTally.keys():
                tileTally[event] = 1
            else:
                tileTally[event] += 1
            toAdd.append(event)
        if tileTally == self.about["tileNums"]:
            tileNum = -1
            for tile in serial:
                tileNum += 1
                array[tile["y"]][tile["x"]] = toAdd[tileNum]
            return array
        else:
            raise ValueError("Format" + str(tileTally) + "does not abide by" + str(self.about["tileNums"])) #inauthentic board