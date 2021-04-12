import os
import json
import tqdm
import sys
import collections
import time
import re
from multiprocessing import Pool


def load_txt(path):
    with open(path, encoding='UTF-8', errors='ignore') as f:
        data = [i.strip() for i in f.readlines() if len(i.strip()) > 0]
    return data


def load_jsonl(path):
    with open(path, 'r', encoding='UTF_8') as f:
        return [json.loads(line) for line in f.readlines() if len(line.strip()) > 0]


def check_at(seq, tail_length=30):
    temp = re.search(r"(@+)\S{,30} ", seq)
    flag = temp is not None
    r_at_idx = seq.rfind("@")
    if len(seq[r_at_idx:]) < tail_length:
        flag = True
    return flag


def sta_jsonl(datadir, have_id=False):
    paths = [os.path.join(datadir, file) for file in os.listdir(datadir) if file.endswith(".jsonl")]
    if len(paths) == 0:
        paths = [file for file in os.listdir(datadir)]
        paths = [os.path.join(datadir, file) for file in paths]
        paths = [path for path in paths if os.path.isdir(path)]
        paths = [os.path.join(subdir, file) for subdir in paths for file in os.listdir(subdir) if
                 file.endswith(".jsonl")]

    sta = collections.defaultdict(float)
    for path in tqdm.tqdm(paths, initial=1):
        data = load_jsonl(path)
        sta["sessions"] += len(data)
        for line in data:
            if have_id:
                line_id = line[0]
                line = line[1]
            if len(line) > 2:
                sta["multi"] += 1
            sta["utterances"] += len(line)
            for seq in line:
                sta["chars"] += len(seq.replace(" ", ""))
    sta["avg word"] = sta["chars"] / sta["utterances"]
    sta["single"] = sta["sessions"] - sta["multi"]
    sta["avg multi utter"] = (sta["utterances"] - 2 * sta["single"]) / sta["multi"]
    print(sta)
    return


def single_func(path, data_type="jsonl"):
    if data_type == "jsonl":
        data = load_jsonl(path)
    elif data_type == "txt":
        data = load_txt(path)
        data = [x.split("\t\t") for x in data]
    else:
        raise Exception("Wrong data type")
    sta = collections.defaultdict(float)
    sta["sessions"] = len(data)
    for line in data:
        if len(line) > 2:
            sta["multi"] += 1
        sta["utterances"] += len(line)
        for seq in line:
            sta["chars"] += len(seq.replace(" ", ""))
        temp = " ".join(line)
        if check_at(temp):
            sta["have_at"] += 1
    print("over", path)
    return sta


def merge_sta(stas):
    res = collections.defaultdict(float)
    for sta in stas:
        for k, v in sta.items():
            res[k] += v
    if res.get("utterances", 0) > 0:
        res["avg word"] = res["chars"] / res["utterances"]
    res["single"] = res["sessions"] - res["multi"]
    if res.get("multi", 0) > 0:
        res["avg multi utter"] = (res["utterances"] - 2 * res["single"]) / res["multi"]
    return res


def sta_dist(indir, data_type):
    paths = [os.path.join(instance[0], file)
             for instance in list(os.walk(indir))
             for file in instance[-1] if file.endswith(data_type)]

    # single debug
    # path = paths[0]
    # returned = single_func(path)
    # print(merge_sta(returned.get()))
    # exit()

    p = Pool(16)
    print("start")
    res = []
    for path in paths:
        sta_dict = p.apply_async(single_func, args=(path, data_type))
        res.append(sta_dict.get())
        time.sleep(0.01)
    time.sleep(0.01)
    p.close()
    p.join()
    print(merge_sta(res))
    print("over")


if __name__ == '__main__':
    # sta_jsonl(sys.argv[1])
    # sta_dist("./toy_data/after_dist/cleaned_data/")
    sta_dist(sys.argv[1], sys.argv[2])
