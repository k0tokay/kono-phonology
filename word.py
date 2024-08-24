from phono_sys import *
import re
import functools

class Word:
    def __init__(self, text, sys=std_sys):
        self.text = text
        self.sys = sys
        self.ph = re.findall("|".join(sys.ph["X"]), text)
        self.cal_group()

    def cal_group(self):
        # 母音列と子音列に分ける
        C_str = "|".join(self.sys.ph["C"])
        V_str = "|".join(self.sys.ph["V"])
        ans = re.findall(f'(?:{C_str})+|(?:{V_str})+', self.text)
        ans = [re.findall("|".join(self.sys.ph["X"]), x) for x in ans]
        self.cv_group = ans

        # 音節に分ける
        def res_str(label):
            return "|".join([x+y for x,y in self.sys.res[label]])
        ans = []
        def rec(text):
            for c1, v, c2 in itertools.product([res_str("c1"), C_str], [res_str("v"), V_str], [C_str, res_str("c2")]):
                syl = re.match(f'({c1})?({v})({c2})?', text)
                if syl:
                    ans.append(syl.group())
                    rec(text[syl.span()[1]:])
                    return True
            return False
        self.syl_res = rec(self.text)
        self.syl_group = [re.findall("|".join(self.sys.ph["X"]), x) for x in ans]
        if not self.syl_res:
            print(f"{self.text} : 制約違反 - 音節")

    # 母音結合
    def plus(self, word):
        if word.text == "":
            return self
        if self.text == "":
            return word
        cv1 = self.cv_group
        cv2 = word.cv_group
        V1, C1 = ([], cv1) if cv1[-1][0] not in self.sys.ph["V"] else (cv1[-1], cv1[:-1])
        V2, C2 = ([], cv2) if cv2[0][0] not in self.sys.ph["V"] else (cv2[0], cv2[1:])
        if len(V1) == 0 or len(V2) == 0:
            tmp = V1 + ["a"][:(1-len(V1))*(1-len(V2))] + V2
        elif len(V1) == 1 and len(V2) == 1:
            if (V1[0], V2[0]) in self.sys.res["v"]:
                tmp = [V1[0], V2[0]]
            elif (V2[0], V1[0]) in self.sys.res["v"]:
                tmp = [V2[0], V1[0]]
            else:
                tmp = ["y" if len({"o", "y", "v"} & set(V1 + V2)) != 0 else "i"]
        elif len(V1) == 1 and len(V2) >= 2:
            tmp = [V1[0], "j", V2[0]]
        elif len(V1) >= 2 and len(V2) == 1:
            tmp = Word("".join(V1[:-1])).plus(Word(V1[-1]).plus(Word(V2[0]))).ph
        else:
            tmp = [V1[0], "j"] + V2
        ans = "".join(["".join(x) for x in C1 + [tmp] + C2])
        ans = self.sys.res_sub(ans)
        return Word(ans)
    
    # 子音結合
    def dotplus(self, word):
        if word.text == "":
            return self
        if self.text == "":
            return word
        cv1 = self.cv_group
        cv2 = word.cv_group
        C1, V1 = ([], cv1) if cv1[-1][0] not in self.sys.ph["C"] else (cv1[-1], cv1[:-1])
        C2, V2 = ([], cv2) if cv2[0][0] not in self.sys.ph["C"] else (cv2[0], cv2[1:])
        if len(V1) == 0 or len(V2) == 0:
            tmp = C1 + ["n"][:(1-len(C1))*(1-len(C2))] + C2
        elif len(C1) == 1 and len(C2) == 1:
            tmp = [C1[0], C2[0]]
            if C1[0] in self.sys.ph["Q"]:
                tmp[0] = tmp[0][1]
            if C2[0] in self.sys.ph["Q"]:
                tmp[1] = tmp[1][1]
        elif len(C1) == 1 and len(C2) >= 2:
            tmp = C1 + ["a"] + C2  
        else:
            tmp = Word("".join(C1[:-1])).dotplus(Word(C1[-1]).dotplus(Word("".join(C2)))).ph
        ans = "".join(["".join(x) for x in V1 + [tmp] + V2])
        ans = self.sys.res_sub(ans)
        return Word(ans)