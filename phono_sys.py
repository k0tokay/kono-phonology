import itertools

def prod(s1, s2):
    return set(itertools.product(s1, s2))

def flatten(tree):
    ans = dict([])
    for i in tree.keys():
        if type(tree[i]) == set:
            ans[i] = tree[i]
        else:
            ans[i] = []
            for j in tree[i].keys():
                ans |= flatten(tree[i])
                ans[i] += ans[j]
    return ans

class PhonoSys:
    def __init__(self, ph_tree, res, res_sub):
        self.ph_tree = ph_tree
        self.ph = flatten(ph_tree)
        self.res = res
        self.res_sub = res_sub


ph_tree = {"X": {
    "C": {
        "S": {"f", "s", "z", "c", "zc", "kh", "h"},
        "Q": {"ts", "tc"},
        "T": {"p", "b", "t", "d", "k", "g"},
        "N": {"m", "n"},
        "L": {"l"},
        "J": {"w", "j"}},
    "V": {"a", "o", "e", "i", "u", "y", "v"}
    }
}

ph = flatten(ph_tree)

X, C, V, S, Q, T, N, L, J = ph["X"], ph["C"], ph["V"], ph["S"], ph["Q"], ph["T"], ph["N"], ph["L"], ph["J"]

res_c1 = prod(S, T | N | L | J) | prod(T, L) | prod(T | N | L, J)
res_c2 = prod(S | T | N | L, T) | prod(L, N) | prod(N, S)
res_v = set(zip(V, V)) | prod(set("aoe"), V) | set(map(tuple, {"ui", "uy"})) - set(map(tuple, {"ao", "eo", "eu", "ev"}))

res = {"c1" : res_c1, "c2": res_c2, "v": res_v}

def res_sub(pattern, text):
    ans = text
    for key in pattern.keys():
        ans = ans.replace(key, pattern[key])
    return ans

pattern = {"sj": "c", "cj": "c", "tsj": "tc", "tcj": "tc", "khj": "kh", "si": "ci", "ti": "tci", "hi": "khi"}

std_sys = PhonoSys(ph_tree, res, lambda x: res_sub(pattern, x))