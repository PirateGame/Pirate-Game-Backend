import random
import numpy as np

def gridSizeToActionCount(gridSize):
    if gridSize < 25:
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
    howManyActions = gridSizeToActionCount(gridSize) * 11
    mD -= ((mA + mB + mC + mD + howManyActions) - gridSize)

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
    for c in range(11):
        c += len(mAc) + len(mBc) + len(mCc) + len(mDc)
        for ac in range(howManyEachAction):
            array[coords[(c*howManyEachAction)+ac][0]][coords[(c*howManyEachAction)+ac][1]] = chr(c+(65-(len(mAc) + len(mBc) + len(mCc) + len(mDc))))
    
    return array