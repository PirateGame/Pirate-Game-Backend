### DEMO FOR GRID SERIALISATION ###

import grid
gridTemplate = grid.grid((5,5))
exampleGrid = gridTemplate.build()
serialFile = gridTemplate.buildJSON(exampleGrid)

print("Grid:")
print("".join([str(i) + "\n" for i in exampleGrid]))

print("SerialFile:")
print("".join([str(i) + "\n" for i in serialFile]))
print(serialFile)

###

import grid

message = [{'content': '200', 'h': 1, 'id': 0, 'noResize': True, 'w': 1, 'x': 0, 'y': 0}, {'content': '1000', 'h': 1, 'id': 1, 'noResize': True, 'w': 1, 'x': 1, 'y': 0}, {'content': '200', 'h': 1, 'id': 2, 'noResize': True, 'w': 1, 'x': 2, 'y': 0}, {'content': '200', 'h': 1, 'id': 3, 'noResize': True, 'w': 1, 'x': 3, 'y': 0}, {'content': '200', 'id': 4, 'noResize': True, 'x': 4, 'y': 0, 'w': 1, 'h': 1}, {'content': '200', 'h': 1, 'id': 5, 'noResize': True, 'w': 1, 'x': 5, 'y': 0}, {'content': '200', 'h': 1, 'id': 6, 'noResize': True, 'w': 1, 'x': 6, 'y': 0}, {'content': '200', 'h': 1, 'id': 7, 'noResize': True, 'w': 1, 'x': 0, 'y': 1}, {'content': '1000', 'h': 1, 'id': 33, 'noResize': True, 'w': 1, 'x': 1, 'y': 1}, {'content': '1000', 'h': 1, 'id': 9, 'noResize': True, 
'w': 1, 'x': 2, 'y': 1}, {'content': '200', 'id': 10, 'noResize': True, 'x': 3, 'y': 1, 'w': 1, 'h': 1}, {'content': 'Present', 'h': 1, 'id': 11, 'noResize': True, 'w': 1, 'x': 4, 'y': 1}, {'content': 'Choose Next Square', 'h': 1, 'id': 12, 'noResize': True, 'w': 1, 'x': 5, 'y': 1}, {'content': '200', 'id': 13, 'noResize': True, 'x': 6, 'y': 1, 'w': 1, 'h': 1}, {'content': '200', 'h': 1, 'id': 14, 'noResize': True, 'w': 1, 'x': 0, 'y': 2}, {'content': '200', 'h': 1, 'id': 8, 'noResize': True, 'w': 1, 'x': 1, 'y': 2}, {'content': '200', 'h': 1, 'id': 16, 'noResize': True, 'w': 1, 'x': 2, 'y': 2}, {'content': '1000', 'h': 1, 'id': 17, 'noResize': True, 'w': 1, 'x': 3, 'y': 2}, {'content': 'Swap', 'h': 1, 'id': 18, 'noResize': True, 'w': 1, 'x': 4, 'y': 2}, {'content': '3000', 'h': 1, 'id': 19, 'noResize': True, 'w': 1, 'x': 5, 'y': 2}, {'content': 'Double', 'h': 1, 'id': 20, 'noResize': True, 'w': 1, 'x': 6, 'y': 2}, {'content': '200', 'h': 1, 'id': 21, 'noResize': True, 'w': 1, 'x': 0, 'y': 3}, {'content': '1000', 'h': 1, 'id': 15, 'noResize': True, 'w': 1, 'x': 
1, 'y': 3}, {'content': '200', 'h': 1, 'id': 23, 'noResize': True, 'w': 1, 'x': 2, 'y': 3}, {'content': 'Mirror', 'h': 1, 'id': 24, 'noResize': True, 'w': 1, 'x': 3, 'y': 3}, {'content': 'Kill', 'h': 1, 'id': 25, 'noResize': True, 'w': 1, 'x': 4, 'y': 3}, {'content': '200', 'h': 1, 'id': 26, 'noResize': True, 'w': 1, 'x': 5, 'y': 3}, {'content': '200', 'h': 1, 'id': 27, 'noResize': True, 'w': 1, 'x': 6, 'y': 3}, {'content': '5000', 'h': 1, 'id': 28, 'noResize': True, 'w': 1, 'x': 0, 'y': 4}, {'content': 'Rob', 'h': 1, 'id': 22, 'noResize': True, 'w': 1, 'x': 1, 'y': 4}, {'content': '1000', 'h': 1, 'id': 30, 'noResize': True, 'w': 1, 'x': 2, 'y': 4}, {'content': '200', 'h': 1, 'id': 31, 'noResize': True, 'w': 1, 'x': 3, 'y': 4}, {'content': '200', 'h': 1, 'id': 32, 'noResize': True, 'w': 1, 'x': 4, 'y': 4}, {'content': '3000', 'h': 1, 'id': 29, 'noResize': True, 'w': 1, 'x': 5, 'y': 4}, {'content': 'Shield', 'h': 1, 'id': 34, 'noResize': True, 'w': 1, 'x': 6, 'y': 4}, {'content': 'Bomb', 'h': 1, 'id': 35, 'noResize': True, 'w': 1, 'x': 0, 'y': 5}, {'content': '1000', 'h': 1, 'id': 36, 'noResize': True, 'w': 1, 'x': 1, 'y': 5}, {'content': '200', 'h': 1, 'id': 37, 'noResize': True, 'w': 1, 'x': 2, 'y': 5}, {'content': '200', 'h': 1, 'id': 38, 'noResize': True, 'w': 1, 'x': 3, 'y': 5}, {'content': '200', 'h': 1, 'id': 39, 'noResize': True, 'w': 1, 'x': 4, 'y': 5}, {'content': '1000', 'h': 1, 'id': 40, 'noResize': True, 'w': 1, 'x': 5, 'y': 5}, {'content': '1000', 'h': 1, 'id': 41, 'noResize': True, 'w': 1, 'x': 6, 'y': 5}, {'content': '1000', 'h': 1, 'id': 42, 'noResize': True, 'w': 1, 'x': 0, 'y': 6}, {'content': '200', 'h': 1, 'id': 43, 'noResize': True, 'w': 1, 'x': 1, 'y': 6}, {'content': '200', 'h': 1, 'id': 44, 'noResize': True, 'w': 1, 'x': 2, 'y': 6}, {'content': '200', 'h': 1, 'id': 45, 'noResize': True, 'w': 1, 'x': 3, 'y': 6}, {'content': '200', 'h': 1, 'id': 46, 'noResize': True, 'w': 1, 'x': 4, 'y': 6}, {'content': 'Bank', 'h': 1, 'id': 47, 'noResize': True, 'w': 1, 'x': 5, 'y': 6}, {'content': 'Skull and Crossbones', 'h': 1, 'id': 48, 'noResize': True, 'w': 1, 'x': 6, 'y': 6}]

grid.serialWriteBoard(message)
