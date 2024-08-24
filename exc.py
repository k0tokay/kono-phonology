import json
from word import *
import numpy as np

with open("dict/saimeno-v4.json") as f:
    data = json.load(f)

not_syl_res = []
for i, w in enumerate(data["words"]):
    w = Word(w["entry"]["form"])
    not_syl_res.append(not w.syl_res)

print(np.sum(not_syl_res))

samples = ["asfah", "coitav", "moftalto", "sss"]
w1 = Word(samples[0])
suf = Word("ikas")
print(w1.plus(suf).text)