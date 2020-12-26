### DEMO FOR GRID SERIALISATION ###

import grid
gridTemplate = grid.grid((5,5))
exampleGrid = gridTemplate.build()
serialFile = gridTemplate.buildJSON(exampleGrid)

print("Grid:")
print("".join([str(i) + "\n" for i in exampleGrid]))

print("SerialFile:")
print("".join([str(i) + "\n" for i in serialFile]))
