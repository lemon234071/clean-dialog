import os
import time
import re
import random
import collections
import json
from multiprocessing import Pool


def load_jsonl(path):
    with open(path, 'r', encoding='UTF_8') as f:
        return [json.loads(line) for line in f.readlines() if len(line.strip()) > 0]


def load_txt(path):
    with open(path, encoding='UTF-8', errors='ignore') as f:
        data = [i.strip() for i in f.readlines() if len(i.strip()) > 0]
    return data


def save_txt(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(data)


def save_json(data, path, indent=0):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


no_emoji_regex = re.compile(
    "["
    "\u2E80-\u2FFF"
    "]+",
    flags=re.UNICODE,
)


def single_func(path):
    sta = collections.defaultdict(float)
    try:
        symbol_vocab = load_txt("../tool_data/data_symbols_remained_ascii.txt")
        symbol_vocab = set([x.split("\t\t")[0] for x in symbol_vocab])
        data = load_jsonl(path)
        print("start", path)
        for dialog in data:
            dialog = "\t\t".join(dialog)
            if no_emoji_regex.search(dialog):
                sta["no_emoji"] += 1
                continue
            dialog_set = list(dialog)
            for word in dialog_set:
                if word in symbol_vocab:
                    sta[word] += 1
                    break

        print("over {}".format(path))
        return sta
    except Exception as e:
        print("error!!!!!")
        print(e)
        return sta


def filter_symbols(indir):
    paths = [os.path.join(instance[0], file)
             for instance in list(os.walk(indir))
             for file in instance[-1] if file.endswith(".jsonl")]

    p = Pool(16)
    # single debug
    # path = paths[0]
    # returned = single_func(path)
    # print(returned.get())
    # exit()
    print("start")
    res = []
    for path in paths:
        res_set = p.apply_async(single_func, args=(path,))
        res.append(res_set.get())
        time.sleep(0.01)
    time.sleep(0.01)
    out = collections.defaultdict(float)
    for x in res:
        for k, v in x.items():
            out[k] += v
    print(out)
    p.close()
    p.join()
    print("over")
    return


if __name__ == '__main__':
    # print("test")
    # text = "asd12s12`🐹1"
    # print(PAT.sub("", text))
    import sys

    filter_symbols(sys.argv[1])
