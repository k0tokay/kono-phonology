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

fields = [
    [
        "entry",
        "id",
        "translations",
        "parent",
        "children",
        "tags",
        "arguments"
    ], [
        "単語",
        "ID",
        "翻訳",
        "上位語",
        "下位語",
        "タグ",
        "項"
    ], [
        [True, True, True, True, True],
        [True, True, True, True, True],
        [False, True, True, True, True],
        [False, True, True, False, False],
        [True, True, True, False, False],
        [True, True, True, True, True],
        [False, False, True, False, False]
    ], [
        lambda id: data[str(id)]["entry"],
        lambda id: str(id),
        lambda id: "，".join(data[str(id)]["translations"]) if "translations" in data[str(id)] else "",
        lambda id: data[str(id)]["parent"] if "parent" in data[str(id)] else "",
        lambda id: "，".join(map(str, data[str(id)]["children"])) if "children" in data[str(id)] else "",
        lambda id: "，".join(data[str(id)]["tags"]) if "tags" in data[str(id)] else "",
        lambda id: "，".join(map(str, data[str(id)]["arguments"])) if "arguments" in data[str(id)] else ""
    ], [
        lambda text: text,
        lambda text: -1 if text == "" else int(text),
        lambda text: [] if text == "" else text.split("，"),
        lambda text: -1 if text == "" else int(text),
        lambda text: [] if text == "" else list(map(int, text.split("，"))),
        lambda text: [] if text == "" else text.split("，"),
        lambda text: [] if text == "" else list(map(int, text.split("，")))
    ], [
        True,
        False,
        True,
        False,
        False,
        True,
        True
    ]
]

def insert_items(parent, id):
    node = tree.insert(parent, 'end', text=fields[3][0](id), values=(fields[3][1](id), fields[3][2](id)))
    if "children" in data[str(id)]:
        for id in data[str(id)]['children']:
            insert_items(node, id)

c_num = 4
for id in range(c_num):
    insert_items("", id)

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

def category(id):
    if id < c_num:
        return -1
    else:
        pid = data[str(id)]["parent"]
        if pid < c_num:
            return pid
        else:
            return category(pid)

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
    for i in [0, 1, 2]:
        tk.Label(frame_1, text=fields[1][i]).grid(row=i, column=0, padx=10, pady=10, sticky="w")
        entries.append(tk.Entry(frame_1))
        entries[i].grid(row=i, column=1, padx=10, pady=10, sticky="ew")
    search_button = tk.Button(frame, text="検索", command=lambda: search_element(entries, result_frame))
    search_button.pack()

# 検索
def search_element(entries, frame):
    id = entries[1].get()
    if id == "":
        result = data.copy()
    elif id in data:
        result = {id : data[id]}
    else:
        result = {}
    for i in [0, 2]:
        text = entries[i].get()
        if text == "":
            continue
        result = {id: result[id] for id in result if fields[3][i](id).find(text) != -1}
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
    
    for id, r in result.items():
        text = f'{r["entry"]}, {id}, {r["translations"][0]}'
        button = tk.Button(frame, text=text, command=lambda: select_item(getitem(int(id))))
        button.pack(fill=tk.X)

search_window(main_frame)

# 単語の詳細画面
def detail_window(frame, id):
    for widget in frame.winfo_children():
        widget.destroy()
    
    frame_1 = tk.Frame(frame)
    frame_1.pack()
    entries = {}
    for i in range(len(fields[0])):
        if not fields[2][i][category(id)+1]:
            continue
        j = len(entries)
        tk.Label(frame_1, text=fields[1][i]).grid(row=j, column=0, padx=10, pady=10, sticky="w")
        var = tk.StringVar(value=fields[3][i](id))
        entries[str(i)] = tk.Entry(frame_1, textvariable=var)
        entries[str(i)].grid(row=j, column=1, padx=10, pady=10, sticky="ew")

        if not fields[5][i]: # 編集不能にする属性
            entries[str(i)].config(state='readonly')
    content_frame = tk.Frame(frame)
    content_frame.pack()

    edit_button = tk.Button(main_frame, text="変更を保存", command=lambda: edit_element(entries))
    edit_button.pack()

    frame.update_idletasks()

# 追加
def add_element(parent):
    id = max([int(id) for id in data]) + 1
    pid = getid(parent)
    new_element = {}
    c = category(pid)
    c = pid if c == -1 else c
    for i in range(len(fields[0])):
        if fields[2][i][c+1] and i != 1:
            new_element[fields[0][i]] = fields[4][i]("")
    new_element["parent"] = pid
    new_element["contents"] = []
    new_element["variations"] = []
    # ポップアップを出す
    popup = tk.Toplevel(root)
    popup.title("要素の追加")
    entries = {}
    for i in [0, 2, 5, 6]:
        if fields[2][i][c+1]:
            j = len(entries)
            tk.Label(popup, text=fields[1][i]).grid(row=j, column=0, padx=10, pady=10, sticky="e")
            entries[str(i)] = tk.Entry(popup)
            entries[str(i)].grid(row=j, column=1, padx=10, pady=10)
    
    def save_data():
        for i in [0, 2, 5, 6]:
            if fields[2][i][c+1]:
                new_element[fields[0][i]] = fields[4][i](entries[str(i)].get())

        data[str(id)] = new_element
        data[str(pid)]["children"].append(id)
        insert_items(parent, id)

        popup.destroy()
    
    tk.Button(popup, text="OK", command=save_data).grid(row=len(entries), columnspan=2, pady=10)
    popup.geometry("300x300")

# 削除
def delete_element(node):
    id = getid(node)
    pid = data[str(id)]["parent"]
    data[str(pid)]["children"].remove(id)
    if "children" not in data[str(id)]:
        tree.delete(node)
        data.pop(str(id))
        return
    # ポップアップを出す
    popup = tk.Toplevel(root)
    popup.title("要素の削除")
    tk.Label(popup, text="子の新しい親").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry = tk.Entry(popup)
    entry.grid(row=0, column=1, padx=10, pady=10)
    def save_data():
        new_pid = int(entry.get())
        if str(new_pid) in data:
            for cid in data[str(id)]["children"]:
                data[str(cid)]["parent"] = new_pid
                data[str(new_pid)]["children"].append(cid)
                tree.insert(getitem(pid), "end", text=data[str(cid)]["entry"], values=(cid, "，".join(data[str(cid)]["translations"])))
        tree.delete(node)
        data.pop(str(id))
        popup.destroy()
    tk.Button(popup, text="OK", command=save_data).grid(row=3, columnspan=2, pady=10)


def on_tree_select(event):
    if tree.selection(): # deleteすると()になるっぽい(?)
        selected_item = tree.selection()[0]
        detail_window(main_frame, getid(selected_item))

tree.bind('<<TreeviewSelect>>', on_tree_select)

# 編集
def edit_element(entries):
    id = int(entries["1"].get())
    item = getitem(id)
    for i in entries:
        if i != "1":
            text = entries[i].get()
            data[str(id)][fields[0][int(i)]] = fields[4][int(i)](text)
    tree.item(item, text=entries["0"].get(), values=(entries["1"].get(), entries["2"].get() if "2" in entries else ""))

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
def save_data(event=None):
    with open(dict_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 保存ショートカット
root.bind("<Command-s>", save_data)
root.bind("<Control-s>", save_data)

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
        "zpdic" : {
            "punctuations" : [",","、","，"],
            "pronunciationTitle" : "Pronunciation"},
            "zpdicOnline":{"enableMarkdown" : False
        },
        "version" : 2
    }
    words = []
    id_form = lambda id: {
        "id": id,
        "form": data[str(id)]["entry"]
    }
    for id, w in data.items():
        id = int(id)
        if id < c_num:
            continue
        word = {}
        word["entry"] = id_form(id)
        word["translations"] = [{ 
            "title" : data[str(category(id))]["entry"][1:-1],
            "forms": w["translations"]
        }]
        word["tags"] = w["tags"]
        word["contents"] = w["contents"]
        word["variations"] = w["variations"]
        word["relations"] = []
        pid = w["parent"]
        if pid >= c_num:
            r = {
                "title": "上位語",
                "entry": id_form(pid)
            }
            word["relations"].append(r)
        if "children" in w:
            for cid in w["children"]:
                r = {
                    "title": "下位語",
                    "entry": id_form(cid)
                }
                word["relations"].append(r)
        if "arguments" in w:
            for i, aid in enumerate(w["arguments"]):
                r = {
                    "title": f"第{i}項",
                    "entry": id_form(aid)
                }
                word["relations"].append(r)
        words.append(word)
    zpdic["words"] = words
    return zpdic

with open(dict_zpdic_path, "w") as f:
    json.dump(to_zpdic(), f, ensure_ascii=False, indent=2)