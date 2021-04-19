import os
import time
import json
import tqdm
from multiprocessing import Pool


def load_txt(path):
    with open(path, encoding='UTF-8', errors='ignore') as f:
        data = [i.strip() for i in f.readlines() if len(i.strip()) > 0]
    return data


def save_txt(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(data)


def save_jsonl(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write("\n".join(json.dumps(line, ensure_ascii=False) for line in data))


def load_jsonl(path):
    with open(path, 'r', encoding='UTF_8') as f:
        return [json.loads(line) for line in f.readlines() if len(line.strip()) > 0]


def single_func(path, outpath):
    data = load_jsonl(path)
    data = [[x.split("</title>", 1)[0] for x in dialog] for dialog in data]
    save_jsonl(data, outpath)
    print("over {}".format(path))
    return


def filter_symbols(indir, ourdir, n_p):
    paths = [os.path.join(instance[0], file)
             for instance in list(os.walk(indir))
             for file in instance[-1] if file.endswith(".jsonl")]

    p = Pool(int(n_p))
    # single debug
    # path = paths[0]
    # outpath = path.replace(indir, ourdir)
    # if not os.path.exists(os.path.dirname(outpath)):
    #     os.makedirs(os.path.dirname(outpath))
    # single_func(path, outpath)
    # exit()
    print("start")
    for path in paths:
        outpath = path.replace(indir, ourdir)
        if not os.path.exists(os.path.dirname(outpath)):
            os.makedirs(os.path.dirname(outpath))
        p.apply_async(single_func, args=(path, outpath))
        time.sleep(0.01)
    time.sleep(0.01)
    p.close()
    p.join()
    print("over")
    return


if __name__ == '__main__':
    import sys
    filter_symbols(sys.argv[1], sys.argv[2], sys.argv[3])
