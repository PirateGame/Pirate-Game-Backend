import random

rOrC = random.choice(["row", "column"])#randint(0,1)
if rOrC == "column":
    columns = [str(i) for i in range(3)]
    columns.remove("1")
    choice = random.choice(columns)
else:
    rows = ["A", "B", "C"]
    del rows[int("2") - 1]
    choice = random.choice(rows)
print(choice)