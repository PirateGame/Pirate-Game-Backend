import grid
gridTemplate = grid.grid((5,5))
exampleGrid = gridTemplate.build()

JSON = []

gridHeight = len(exampleGrid)
gridWidth = len(exampleGrid[0])
for y in range(gridHeight):
    for x in range(gridWidth):
        JSON.append({"x":x, "y":y, "w":1, "h":1, "id":(y * gridWidth) + x, "content":""})

print(JSON)
