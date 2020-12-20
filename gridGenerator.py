import random
import numpy as np
from scipy import optimize

def gridSizeToActionCount(gridSize):
    if gridSize <= 25:
        return 1
    else:
        return round((gridSize + 12.5) / 25) - 1

def makeGrid(gridDim):
    #gridDim = (10,10)
    gridSize = gridDim[0] * gridDim[1]

    array = [[None for y in range(gridDim[1])] for y in range(gridDim[0])]

    coords = []
    for x in range(gridDim[0]):
        for y in range(gridDim[1]):
            coords.append((x,y))
    random.shuffle(coords)

    mA = int(np.ceil(gridSize * (1/49)))
    mB = int(np.ceil(gridSize * (2/49)))
    mC = int(np.ceil(gridSize * (10/49)))
    mD = int(np.ceil(gridSize * (25/49)))
    howManyEachAction = gridSizeToActionCount(gridSize)
    howManyActions = howManyEachAction * 11

    # Reference for later: maxGameLength = 55 + (5 * gridSize) + (90 * (howManyEachAction * clientCount))
    
    def toMinimize(mA, mB, mC, mD, mAs, mBs, mCs, mDs): #The difference between the average monetary value of what the board should have been, and what it is now that tiles are being removed. This needs to be minimized to maintain the economy regardless of board size.
        return np.abs((((5000*(mA-mAs))+(3000*(mB-mBs))+(1000*(mC-mCs))+(200*(mD-mDs))) / ((mA-mAs)+(mB-mBs)+(mC-mCs)+(mD-mDs))) - ((((mA)*5000)+((mB)*3000)+((mC)*1000)+((mD)*200)) / (mA+mB+mC+mD))) 

    total = (mA + mB + mC + mD + howManyActions) - gridSize
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

    mAc = coords[:mA]
    mBc = coords[mA:mB+mA]
    mCc = coords[mB+mA:mC+mB+mA]
    mDc = coords[mC+mB+mA:mD+mC+mB+mA]
    mEc = coords[mD+mC+mB+mA:]

    for c in range(len(mAc)):
        array[coords[c][0]][coords[c][1]] = 5000
    for c in range(len(mBc)):
        c += len(mAc) 
        array[coords[c][0]][coords[c][1]] = 3000
    for c in range(len(mCc)):
        c += len(mAc) + len(mBc)
        array[coords[c][0]][coords[c][1]] = 1000
    for c in range(len(mDc)):
        c += + len(mAc) + len(mBc) + len(mCc)
        array[coords[c][0]][coords[c][1]] = 200
    for c in range(0, 11*howManyEachAction, howManyEachAction):
        c += len(mAc) + len(mBc) + len(mCc) + len(mDc)
        for ac in range(howManyEachAction):
            array[coords[c+ac][0]][coords[c+ac][1]] = chr(65 + ((c - (len(mAc) + len(mBc) + len(mCc) + len(mDc)))//howManyEachAction))
    
    return [array, {"mA":mA, "mB":mB, "mC":mC, "mD":mD, "howManyActions":howManyActions, "gridSize":gridSize}] #Return a dictionary with all the important stuff.
