import os
import json
import tqdm
import sys
import re
from multiprocessing import Pool


def load_jsonl(path):
    with open(path, 'r', encoding='UTF_8') as f:
        return [json.loads(line) for line in f.readlines() if len(line.strip()) > 0]


def save_jsonl(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write("\n".join(json.dumps(line, ensure_ascii=False) for line in data))


def seq_clean(seq, zhihu=False):
    seq = seq.replace("</title>", " ")
    seq = seq.replace("</tle>", " ")
    if zhihu:
        pat = re.compile(r"…* *显示全部\s*")
        seq = pat.sub("", seq)
    # seq = seq.replace("...显示全部", "")
    seq = seq.replace("<URL>", "")
    seq = seq.replace("<url>", "")
    return seq


def single_func(path, outpath, extra_func=False, min_length=2, max_length=256):
    try:
        new_data = []
        print("loading", path)
        print("outpath", outpath)
        data = load_jsonl(path)
        for dialog in tqdm.tqdm(data):
            new_dialog = []
            for seq in dialog:
                if extra_func:
                    seq = seq_clean(seq, ("zhihu" in path))
                length = len(seq.replace(" ", ""))
                if length > max_length or length < 1:
                    if len(new_dialog) > 1:
                        # flag = len(new_dialog) == 2 and len(new_dialog[1].replace(" ", "")) < min_length
                        # if not flag:
                        new_data.append(new_dialog)
                    new_dialog = []
                else:
                    new_dialog.append(seq)
            if len(new_dialog) > 1:
                # flag = len(new_dialog) == 2 and len(new_dialog[1].replace(" ", "")) < min_length
                # if not flag:
                new_data.append(new_dialog)
        save_jsonl(new_data, outpath)
        print("over", path)
    except Exception as e:
        print("error!!!!", e)
    return


def main(indir, outdir, extra_func=False):
    paths = [os.path.join(instance[0], file)
             for instance in list(os.walk(indir))
             for file in instance[-1] if file.endswith(".jsonl")]

    outpaths = [path.replace(indir, outdir) for path in paths]

    # debug single
    # path, outpath = next(zip(paths, outpaths))
    # outsubdir = os.path.dirname(outpath)
    # if not os.path.exists(outsubdir):
    #     os.makedirs(outsubdir)
    # single_func(path, outpath, extra_func)
    # exit()

    p = Pool(16)
    print("start")
    for path, outpath in zip(paths, outpaths):
        outsubdir = os.path.dirname(outpath)
        if not os.path.exists(outsubdir):
            os.makedirs(outsubdir)
        p.apply_async(single_func, args=(path, outpath, extra_func))
    p.close()
    p.join()
    print("over")


if __name__ == '__main__':
    # filter_dist("./toy_data/raw/", "./toy_data/output/", True)
    main(sys.argv[1], sys.argv[2], True)
