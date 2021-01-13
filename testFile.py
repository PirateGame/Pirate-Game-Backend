import random

options = []
for key,value in {"none":True, "mirror":True, "shield":True}.items():
    if value:
        options.append(key)
if "AI" == "AI":
    print(random.choice(options))