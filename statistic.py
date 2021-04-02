import os
import json
import tqdm
import sys
import collections


def load_jsonl(path):
    with open(path, 'r', encoding='UTF_8') as f:
        return [json.loads(line) for line in f.readlines() if len(line.strip()) > 0]


def sta_jsonl(datadir, have_id=False):
    paths = [os.path.join(datadir, file) for file in os.listdir(datadir) if file.endswith(".jsonl")]
    if len(paths) == 0:
        paths = [file for file in os.listdir(datadir)]
        paths = [os.path.join(datadir, file) for file in paths]
        paths = [path for path in paths if os.path.isdir(path)]
        paths = [os.path.join(subdir, file) for subdir in paths for file in os.listdir(subdir) if file.endswith(".jsonl")]

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


if __name__ == '__main__':
    sta_jsonl(sys.argv[1])
