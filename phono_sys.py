import itertools

def prod(s1, s2):
    return list(map(list, itertools.product(s1, s2)))

def flatten(tree):
    result = {}
    for i, node in tree.items():
        if isinstance(node, list):
            result[i] = node
        else:
            result |= flatten(node)
            result[i] = [x for j in node for x in result[j]]
    return result

class PhonoSys:
    def __init__(self, ph_tree, res, res_sub):
        self.ph_tree = ph_tree
        self.ph = flatten(ph_tree)
        self.res = res
        self.res_sub = res_sub


ph_tree = {
    "X": {
        "C": {
            "S": ["f", "s", "z", "c", "zc", "kh", "h"],
            "Q": ["ts", "tc"],
            "T": ["p", "b", "t", "d", "k", "g"],
            "N": ["m", "n"],
            "L": ["l"],
            "J": ["w", "j"],
        },
        "V": ["a", "o", "e", "i", "u", "y", "v"],
    },
}

_globals = globals()
_globals |= flatten(ph_tree)

res_c1 = prod(S, T + N + L + J) + prod(T, L) + prod(T + N + L, J)
res_c2 = prod(S + T + N + L, T) + prod(L, N) + prod(N, S)
res_v = list(map(list, zip(V, V))) + prod("aoe", V) + [list("ui"), list("uy")]
res_v = list(filter(lambda x : x not in map(list, ["ao", "eo", "eu", "ev"]), res_v))

res = {"C1" : res_c1, "C2": res_c2, "V": res_v}

def res_sub(pattern, text):
    ans = text
    for key in pattern.keys():
        ans = ans.replace(key, pattern[key])
    return ans

pattern = {"sj": "c", "cj": "c", "tsj": "tc", "tcj": "tc", "khj": "kh", "si": "ci", "ti": "tci", "hi": "khi"}

std_sys = PhonoSys(ph_tree, res, lambda x: res_sub(pattern, x))