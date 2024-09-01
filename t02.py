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
    if "arguments" in w:
        w["function"] = 0
    new_data[id] = w

with open(dict_path, 'w') as f:
    json.dump(new_data, f, indent=2, ensure_ascii=False)