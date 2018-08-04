# -*- coding: utf-8 -*-
import json

def combination(idx, item, lst, keywords, keys):
    if idx == len(keys):
        lst.append(item)
        return False
    if len(item) == 3:
        lst.append(item)
        return True
    for k in keywords[keys[idx]]:
        new_item = item[:]
        if k != "":
            new_item.append(k)
        if combination(idx+1, new_item, lst, keywords, keys):
            break

def get_keywords():
    data = json.load(open("label/label.json", "r"))
    keys = data["keys"]
    keywords = data["labels"]
    lst = []
    combination(0, [], lst, keywords, keys)
    for item in lst:
        item = map(lambda x: x.encode('utf-8'), item)
        yield " ".join(item)

