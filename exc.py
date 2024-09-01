import json
from word import *
import numpy as np

with open("dict/saimeno-v4.json") as f:
    data = json.load(f)

not_valid = []
for i, w in enumerate(data["words"]):
    w = Word(w["entry"]["form"], alert_flag=True)
    not_valid.append(not w.is_valid)

print(f"総数 : {np.sum(not_valid)}")

print(Word("stoit").dotplus(Word("lis")).text)