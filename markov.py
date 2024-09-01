import json
import numpy as np
from word import *

# N-gramマルコフモデル
# N >= 2
N = 3

with open("dict/saimeno-v4.json") as f:
    data = json.load(f)

words = [["BOS"] * (N-1) + Word(w["entry"]["form"]).ph + ["EOS"] * (N-1) for w in data["words"]]

X = std_sys.ph["X"] + ["BOS", "EOS"]
inv = lambda X : {x : X.index(x) for x in X}
# X^nの場合
inv_n = lambda X, n, x : np.sum([inv(X)[x[i]] * len(X) ** i for i in range(n)])
L = len(X)
invX = inv(X)
invXN = lambda x: inv_n(X, N-1, x)
to_N_gram = lambda w : [w[i:i+N] for i in range(len(w)-N+1)]
N_grams = list(map(to_N_gram, words))

A = np.zeros((L ** (N-1), L))
# Nが大きすぎるとAが死ぬ

for w in N_grams:
    for wi in w:
        A[invXN(wi[:-1])][invX[wi[-1]]] += 1

A_sum = np.sum(A, axis=1, keepdims=True)
A /= np.where(A_sum != 0, A_sum, 1) # 0除算よけ

# with open("markov.json", "w") as f:
#     json.dump(A.tolist(), f, indent=2)

generated = []
for _ in range(500):
    w = ["BOS"] * (N-1)
    next = "BOS"
    while next != "EOS":
        tail = invXN(w[1-N:])
        next = np.random.choice(X, p=A[tail])
        w.append(next)
    w = Word("".join(w[N-1:-1]))
    if w.is_valid and len(w.ph) >= 4 and w.text not in data["words"]["entry"]["form"]:
        generated.append(w.text)

generated = list(set(generated)) # 一意化

with open("generated/markov01.txt", "w") as f:
    f.write("\n".join(generated))