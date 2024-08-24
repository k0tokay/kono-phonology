import json
from word import *
import markovify

with open("dict/saimeno-v4.json") as f:
    data = json.load(f)

words = [Word(w["entry"]["form"]) for w in data["words"]]
text = "\n".join([" ".join(w.ph) + " .."[i%3] for i, w in enumerate(words)])
#text = "\n".join([" ".join(["".join(v) for v in w.syl_group]) + " ." for w in words])

text_model = markovify.Text(text, state_size=2)

generated = []
for _ in range(3):
    ans = text_model.make_sentence() # なぜかくそ長い．なにこれ．
    if ans != None:
        ans = ans.replace(" ", "").split(".")
        generated += ans

generated = filter(lambda x: len(x) >= 4, generated)
generated = list(set(generated) - set(words))
generated = filter(lambda x: Word(x).syl_res, generated)

with open("generated/samples01.txt", "w") as f:
    f.write("\n".join(generated))