import json
from pathlib import Path
from word import *
import numpy as np

path = Path(__file__).parent.parent / "dict" / "saimeno-v4.json"
with open(path) as f:
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