from phono_sys import *

class Word:
    def __init__(self, text, sys=std_sys, alert_flag=False):
        self.text = text
        self.sys = sys
        self.alert_flag = alert_flag
        self.is_valid = True
        self.cal_ph()
        self.cal_group()
    
    def alert(self, content):
        self.is_valid = False
        if self.alert_flag:
            print(content)
    # 音素列にする
    def cal_ph(self):
        X = self.sys.ph["X"]
        X = sorted(X, key=len, reverse=True)
        i = 0
        ans = []
        while i < len(self.text):
            j = 0
            while j < len(X) and X[j] != self.text[i:i + len(X[j])]: j += 1
            if j < len(X):
                ans.append(X[j])
                i += len(X[j])
            else:
                self.alert(f"{self.text} : 制約違反 - 音素")
                self.ph = ans
                break
        self.ph = ans

    def cal_group(self):
        # 母音列と子音列に分ける
        i = 0
        ans = []
        while i < len(self.ph):
            Pc = lambda i : self.ph[i] in self.sys.ph["C"]
            j = 0
            while i + j < len(self.ph) and Pc(i) == Pc(i+j): j += 1
            if i + j != len(self.ph):
                ans.append(self.ph[i:i+j])
            else:
                ans.append(self.ph[i:])
            i += j
        self.cv_group = ans

        # 音節に分ける
        ans = []
        singleton = lambda x : [x]
        CC1 = self.sys.res["C1"] + list(map(singleton, self.sys.ph["C"])) + [[]]
        VV = self.sys.res["V"] + list(map(singleton, self.sys.ph["V"]))
        CC2_list = [[[]], list(map(singleton, self.sys.ph["C"])), list(self.sys.res["C2"])] # これだけ順番要る
        def rec(group):
            if len(group) <= 2:
                return False
            P1 = group[0] in CC1 and group[1] in VV
            i = 1 if len(group[2]) >= 2 else 0
            CC2 = CC2_list[i] + CC2_list[1-i] + CC2_list[2]
            for c in CC2: # CC2をどこで切るか
                Prec = False
                if group[2][:len(c)] == c:
                    tmp1 = group[2][:len(c)] if len(c) != 0 else []
                    tmp2 = group[2][len(c):] if len(c) != len(group[2]) else []
                    Prec = False
                    if len(group) > 3:
                        Prec = rec([tmp2] + group[3:])
                    Prec |= len(group) == 3 and tmp2 == []
                    if P1 and Prec:
                        ans.append(group[:2] + [tmp1])
                        return True
            return False
        group = self.cv_group.copy()
        if self.cv_group[0][0] in self.sys.ph["V"]:
            group = [[]] + group
        if self.cv_group[-1][0] in self.sys.ph["V"]:
            group = group + [[]]
        flag = rec(group)
        self.syl_group = ans[::-1]
        if not flag:
            self.alert(f"{self.text} : 制約違反 - 音節")

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
            if (V1[0], V2[0]) in self.sys.res["V"]:
                tmp = [V1[0], V2[0]]
            elif (V2[0], V1[0]) in self.sys.res["V"]:
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