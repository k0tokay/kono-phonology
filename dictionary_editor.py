import json
import tkinter as tk
from tkinter import ttk

dict_path = "dict/konomeno-v5.json"
dict_save_path = "dict/konomeno-v5-save.json"
dict_zpdic_path = "dict/konomeno-v5-zpdic.json"
# JSONデータの読み込み
with open(dict_path) as f:
    data = json.load(f)

with open(dict_save_path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

words = data["words"]

# メインウィンドウの作成
root = tk.Tk()
root.title("Dictionary Editor")
window_size = [1000, 700]
root.geometry(f"{window_size[0]}x{window_size[1]}")

window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=15)
window.pack(fill=tk.BOTH, expand=True)

# ツリービューの作成
tree = ttk.Treeview(window)
tree["columns"] = ("id", "translations")
tree.heading("#0", text="単語", anchor="w")
tree.heading("id", text="ID", anchor="w")
tree.heading("translations", text="翻訳", anchor="w")

tree.column("id", width=30, stretch=True)

inv = lambda L: {x: i for i, x in enumerate(L)}
inv_map = lambda L: lambda S: [i for i, x in enumerate(L) if x in S]
categories = {
    "name": [
        "catetgory",
        "concept",
        "relation",
        "HO_relation",
        "parametric_operator",
        "syllable",
        "idiom"
    ],
    "title": [
        "カテゴリ",
        "概念",
        "関係",
        "高階関係",
        "パラメータ演算子",
        "音節",
        "慣用表現"
    ]
}
cat2i = inv(categories["title"])
cat2i_map = inv_map(categories["title"])
attrs = {
    "name": [
        "entry",
        "id",
        "translations",
        "parent",
        "children",
        "tags",
        "arguments",
        "is_function",
        "is_instance"
    ],
    "title": [
        "単語",
        "ID",
        "翻訳",
        "上位語",
        "下位語",
        "タグ",
        "項",
        "関数",
        "実例"
    ], 
    "is_valid": [
        [True, True, True, True, True, True, True],
        [True, True, True, True, True, True, True],
        [False, True, True, True, True, True, True],
        [False, True, True, True, True, True, True],
        [True, True, True, False, False, False, False],
        [True, True, True, True, True, True, True],
        [False, False, True, True, False, False, False],
        [False, False, True, True, False, False, False],
        [False, True, False, False, False, False, False]
    ], 
    "display": [
        lambda id: words[id]["entry"],
        lambda id: id,
        lambda id: "，".join(words[id]["translations"]),
        lambda id: words[id]["parent"] if words[id]["parent"] != None else "",
        lambda id: "，".join(map(str, words[id]["children"])),
        lambda id: "，".join(words[id]["tags"]),
        lambda id: "，".join(map(str, words[id]["arguments"])),
        lambda id: words[id]["is_function"],
        lambda id: words[id]["is_instance"]
    ],
    "parse": [
        lambda text: text,
        lambda text: None if text == "" else int(text),
        lambda text: [] if text == "" else text.split("，"),
        lambda text: None if text == "" else int(text),
        lambda text: [] if text == "" else list(map(int, text.split("，"))),
        lambda text: [] if text == "" else text.split("，"),
        lambda text: [] if text == "" else list(map(int, text.split("，"))),
        lambda text: 0 if text == "" else int(text),
        lambda text: 0 if text == "" else int(text)
    ], 
    "editable": [
        True,
        False,
        True,
        True,
        False,
        True,
        True,
        True,
        True
    ]
}
attr2i = inv(attrs["name"])
attr2i_map = inv_map(attrs["name"])

def insert_items(parent, id):
    idxs = attr2i_map(["id", "entry", "translations"])
    f = lambda i: attrs["display"][idxs[i]](id)
    node = tree.insert(parent, 'end', text=f(0), values=(f(1), f(2)))
    if "children" in words[id]:
        for id in words[id]['children']:
            insert_items(node, id)

cat2wi = {w["entry"]: w["id"] for w in words if w != None and w["category"] == "カテゴリ"}
cat2wi["カテゴリ"] = None
cat2wi_map = lambda S: {w: i for w, i in cat2wi.items() if w in S}
for cat, i in cat2wi.items():
    if i == None:
        continue
    insert_items("", i)

window.add(tree, stretch="always")

# 要素の選択
def select_item(item):
    tree.selection_set(item)
    tree.focus(item)
    tree.see(item)
# 要素 → ID
def getid(item_id):
    return int(list(tree.item(item_id, 'values'))[0])
# ID → 要素
def getitem(id):
    todo = list(tree.get_children())
    while todo:
        node = todo.pop(0)
        if getid(node) == id:
            return node
        todo += tree.get_children(node)

# フレーム
main_frame = tk.Frame(window)
window.add(main_frame, stretch="always")

# 検索画面
def search_window(frame, result_frame=None):
    for widget in frame.winfo_children():
        widget.destroy()
    
    frame_1 = tk.Frame(frame)
    frame_1.pack()
    entries = []
    for i in attr2i_map(["id","entry","translations"]):
        tk.Label(frame_1, text=attrs["title"][i]).grid(row=i, column=0, padx=10, pady=10, sticky="w")
        entries.append(tk.Entry(frame_1))
        entries[i].grid(row=i, column=1, padx=10, pady=10, sticky="ew")
    search_button = tk.Button(frame, text="検索", command=lambda: search_element(entries, result_frame))
    search_button.pack()

# 検索
def search_element(entries, frame):
    id = entries[attr2i["id"]].get()
    if id == "":
        result = words.copy()
    elif id in words:
        result = [words[id]]
    else:
        result = []
    for i in attr2i_map(["entry", "translations"]):
        text = entries[i].get()
        if text == "":
            continue
        result = [result[id] for id, w in enumerate(result) if w != None and attrs["display"][i](id).find(text) != -1]
    search_result_window(frame, result)

# 検索結果画面
def search_result_window(frame, result):
    if frame == None:
        frame = tk.Toplevel(root)
        frame.title("検索結果")
        frame.geometry("300x300")
    else:
        for widget in frame.winfo_children():
            widget.destroy()
    
    for r in result:
        text = f'{r["entry"]}, {r["id"]}, {r["translations"][0]}'
        button = tk.Button(frame, text=text, command=lambda: select_item(getitem(r["id"])))
        button.pack(fill=tk.X)

search_window(main_frame)

# 単語の詳細画面
def detail_window(frame, id):
    for widget in frame.winfo_children():
        widget.destroy()
    
    frame_1 = tk.Frame(frame)
    frame_1.pack()
    entries = {}
    for i in range(len(attrs["name"])):
        if not attrs["is_valid"][i][cat2i[words[id]["category"]]]:
            continue
        j = len(entries)
        tk.Label(frame_1, text=attrs["title"][i]).grid(row=j, column=0, padx=10, pady=10, sticky="w")
        var = tk.StringVar(value=attrs["display"][i](id))
        entries[i] = tk.Entry(frame_1, textvariable=var)
        entries[i].grid(row=j, column=1, padx=10, pady=10, sticky="ew")

        if not attrs["editable"][i]: # 編集不能にする属性
            entries[i].config(state='readonly')
    content_frame = tk.Frame(frame)
    content_frame.pack()

    edit_button = tk.Button(main_frame, text="変更を保存", command=lambda: edit_element(entries))
    edit_button.pack()

    frame.update_idletasks()

# 追加
def add_element(parent):
    id = len(words)
    pid = getid(parent)
    wordTemplate = {
      "id": None,
      "entry": "",
      "category": "",
      "translations": [],
      "simple_translations": [],
      "parent": None,
      "children": [],
      "arguments": [],
      "tags": [],
      "contents": [],
      "variations": [],
      "is_function": None,
      "is_instance": None
    }
    new_element = wordTemplate
    new_element["id"] = id
    c = cat2wi[words[id]["caterogy"]]
    c = pid if c == -1 else c
    # for i in range(len(attrs["name"])):
    #     if attrs["is_valid"][i][c+1] and i != 1:
    #         new_element[attrs["name"][i]] = attrs["parse"][i]("")
    new_element["parent"] = pid
    def cat_rec(id):
        pid = words[id]["parent"]
        if pid ==  None:
            return words[pid]["category"]
        else:
            return cat_rec(pid)
    new_element["category"] = cat_rec(pid)
    # ポップアップを出す
    popup = tk.Toplevel(root)
    popup.title("要素の追加")
    entries = {}
    for i in attr2i_map(["entry", "translations", "tags", "arguements"]):
        if attrs["is_valid"][i][c+1]:
            j = len(entries)
            tk.Label(popup, text=attrs["title"][i]).grid(row=j, column=0, padx=10, pady=10, sticky="e")
            entries[i] = tk.Entry(popup)
            entries[i].grid(row=j, column=1, padx=10, pady=10)
    
    def save_words():
        for i in attr2i_map(["entry", "translations", "tags", "arguements"]):
            if attrs["is_valid"][i][c+1]:
                new_element[attrs["name"][i]] = attrs["parse"][i](entries[i].get())

        words.append(new_element.copy())
        words[pid]["children"].append(id)
        insert_items(parent, id)

        popup.destroy()
    
    tk.Button(popup, text="OK", command=save_words).grid(row=len(entries), columnspan=2, pady=10)
    popup.geometry("300x300")

# 削除
def delete_element(node):
    id = getid(node)
    pid = words[id]["parent"]
    words[pid]["children"].remove(id)
    if "children" not in words[id]:
        tree.delete(node)
        words.pop(id)
        return
    # ポップアップを出す
    popup = tk.Toplevel(root)
    popup.title("要素の削除")
    tk.Label(popup, text="子の新しい親").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry = tk.Entry(popup)
    entry.grid(row=0, column=1, padx=10, pady=10)
    def save_words():
        new_pid = entry.get()
        if new_pid != "" and new_pid in words:
            new_pid = int(new_pid)
            for cid in words[id]["children"]:
                words[cid]["parent"] = new_pid
                words[new_pid]["children"].append(cid)
                insert_items(getitem(pid), cid)
        tree.delete(*tree.get_children(node))
        tree.delete(node)
        words.pop(id)
        popup.destroy()
    tk.Button(popup, text="OK", command=save_words).grid(row=3, columnspan=2, pady=10)


def on_tree_select(event):
    if tree.selection(): # deleteすると()になるっぽい(?)
        selected_item = tree.selection()[0]
        detail_window(main_frame, getid(selected_item))

tree.bind('<<TreeviewSelect>>', on_tree_select)

# 編集
def edit_element(entries):
    id = int(entries[attr2i["id"]].get())
    item = getitem(id)
    for i in entries:
        text = entries[i].get()
        if i == 3:
            pid = words[id]["parent"]
            new_pid = int(text)
            words[pid]["children"].remove(id)
            words[new_pid]["children"].append(id)
        if i != "1":
            words[id][attrs["name"][int(i)]] = attrs["parse"][int(i)](text)
    tree.delete(*tree.get_children(item))
    tree.delete(item)
    insert_items(getitem(new_pid), id)

# ダブルクリックで編集
# def edit_on_click(event):

# 追加・削除のコンテキストメニュー
def create_context_menu(event):
    item_id = tree.identify_row(event.y)
    if item_id:
        context_menu = tk.Menu(root, tearoff=0)
        context_menu.add_command(label="追加", command=lambda: add_element(item_id))
        if int(getid(item_id)) >= c_num: # 0..c_numは削除できない
            context_menu.add_command(label="削除", command=lambda: delete_element(item_id))
        context_menu.post(event.x_root, event.y_root)
    
tree.bind("<Button-2>", create_context_menu)
tree.bind("<Button-3>", create_context_menu)

# 保存
def save_words(event=None):
    with open(dict_path, 'w') as f:
        data["words"] = words
        json.dump(data, f, indent=2, ensure_ascii=False)

# 保存ショートカット
root.bind("<Command-s>", save_words)
root.bind("<Control-s>", save_words)

# 検索ショートカット
root.bind("<Command-f>", lambda event: search_window(main_frame))
root.bind("<Control-f>", lambda event: search_window(main_frame))

# メインループの実行
root.mainloop()

# zpdicへの変換
def to_zpdic():
    # JSON ファイルの仕様
    # https://zpdic.ziphil.com/document/other/json-spec
    zpdic = {
        "words" : [],
        "examples": data["examples"],
        "zpdic" : {
            "punctuations" : [",","、","，"],
            "pronunciationTitle" : "Pronunciation"},
            "zpdicOnline":{"enableMarkdown" : False
        },
        "version" : 2
    }
    zpdic_words = []
    id_form = lambda id: {
        "id": id,
        "form": words[id]["entry"]
    }
    for id, w in enumerate(words):
        if id in cat2wi_map(categories["title"]):
            continue
        if w == None:
            continue
        zpdic_w = {}
        zpdic_w["entry"] = id_form(id)
        c = cat2wi[words[id]["category"]]
        if c == 0 and w["is_instance"] == 1:
            title = "実例" 
        elif c == 1 and w["is_function"] == 1:
            title = "関数"
        elif c == None:
            title = "カテゴリ"
        else:
            title = words[c]["entry"]
        zpdic_w["translations"] = [{ 
            "title" : title,
            "forms": w["translations"]
        }]
        zpdic_w["tags"] = w["tags"]
        zpdic_w["contents"] = w["contents"]
        zpdic_w["variations"] = w["variations"]
        zpdic_w["relations"] = []
        pid = w["parent"]
        if pid != None and pid not in cat2wi_map(categories["title"]):
            r = {
                "title": "上位語",
                "entry": id_form(pid)
            }
            zpdic_w["relations"].append(r)
        if "children" in w:
            for cid in w["children"]:
                r = {
                    "title": "下位語",
                    "entry": id_form(cid)
                }
                zpdic_w["relations"].append(r)
        if "arguments" in w:
            if w["is_function"] == 1:
                w_arg = w["arguments"][:-1]
            else:
                w_arg = w["arguments"]
            for i, aid in enumerate(w_arg):
                r = {
                    "title": f"第{i+1}項",
                    "entry": id_form(aid)
                }
                zpdic_w["relations"].append(r)
            if w["is_function"] == 1:
                r = {
                    "title": "出力",
                    "entry": id_form(w["arguments"][-1])
                }
                zpdic_w["relations"].append(r)
        zpdic_words.append(zpdic_w)
    zpdic["words"] = zpdic_words
    return zpdic

with open(dict_zpdic_path, "w") as f:
    json.dump(to_zpdic(), f, ensure_ascii=False, indent=2)