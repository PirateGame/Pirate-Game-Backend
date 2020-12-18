import random
import numpy as np

def makeGrid(gridDim):
    #gridDim = (10,10) ##MINIMUM SIZE 4X4
    gridSize = gridDim[0] * gridDim[1]
    if gridSize < 13:
        print("@@@ TOO SMALL")

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
    mD -= ((mA + mB + mC + mD + 8) - gridSize)

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
    for c in range(len(mEc)):
        c += len(mAc) + len(mBc) + len(mCc) + len(mDc)
        array[coords[c][0]][coords[c][1]] = chr(c+(65 - (len(mAc) + len(mBc) + len(mCc) + len(mDc))))
    
    return array