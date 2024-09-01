import json
import tkinter as tk
from tkinter import ttk

dict_path = "dict/konomeno-v5.json"
dict_save_path = "dict/konomeno-v5-save.json"
dict_zpdic_path = "dict/konomeno-v5-zpdic.json"
# JSONデータの読み込み
with open(dict_save_path) as f:
    data = json.load(f)

new_data = {}
for id, w in data.items():
    def plus(id):
        if id >= 4:
            return id + 2
        elif id == 0:
            return 0
        elif id == 1:
            return 1
        elif id == 2:
            return 3
        else:
            return 4
    if "parent" in w:
        w["parent"] = plus(w["parent"])
    if "children" in w:
        w["children"] = list(map(plus, w["children"]))
    if "arguments" in w:
        w["arguments"] = list(map(plus, w["arguments"]))
    new_data[str(plus(int(id)))] = w

with open(dict_path, 'w') as f:
    json.dump(new_data, f, indent=2, ensure_ascii=False)