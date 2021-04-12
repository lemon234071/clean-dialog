import os
import json
import tqdm
import sys
import time
import re
from multiprocessing import Pool


def load_txt(path):
    with open(path, encoding='UTF-8', errors='ignore') as f:
        data = [i.strip() for i in f.readlines() if len(i.strip()) > 0]
    return data


def save_txt(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(data)


def load_jsonl(path):
    with open(path, 'r', encoding='UTF_8') as f:
        return [json.loads(line) for line in f.readlines() if len(line.strip()) > 0]


def save_jsonl(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write("\n".join(json.dumps(line, ensure_ascii=False) for line in data))


def no_at(seq, tail_length=30):
    temp_pat = re.compile(r"(@+)\S{,30} ")
    seq = temp_pat.sub("", seq)
    r_at_idx = seq.rfind("@")
    if len(seq[r_at_idx:]) < tail_length:
        seq = seq[:r_at_idx]
    return seq


def is_chinese_char(cp):
    """Checks whether CP is the codepoint of a CJK character."""
    # This defines a "chinese character" as anything in the CJK Unicode block:
    #   https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)
    #
    # Note that the CJK Unicode block is NOT all Japanese and Korean characters,
    # despite its name. The modern Korean Hangul alphabet is a different block,
    # as is Japanese Hiragana and Katakana. Those alphabets are used to write
    # space-separated words, so they are not treated specially and handled
    # like the all of the other languages.
    if (
            (cp >= 0x4E00 and cp <= 0x9FFF)
            or (cp >= 0x3400 and cp <= 0x4DBF)  #
            or (cp >= 0x20000 and cp <= 0x2A6DF)  #
            or (cp >= 0x2A700 and cp <= 0x2B73F)  #
            or (cp >= 0x2B740 and cp <= 0x2B81F)  #
            or (cp >= 0x2B820 and cp <= 0x2CEAF)  #
            or (cp >= 0xF900 and cp <= 0xFAFF)
            or (cp >= 0x2F800 and cp <= 0x2FA1F)  #
    ):  #
        return True

    return False


def contains_Chinese(seq):
    for char in seq:
        cp = ord(char)
        if is_chinese_char(cp):
            return True
    return False

def contain_at(seq, tail_length=30):
    flag = re.search(r"(@+)\S{,30} ", seq)
    if flag is not None:
        return True
    r_at_idx = seq.rfind("@")
    if r_at_idx > -1 and len(seq[r_at_idx:]) < tail_length:
        return True
    return False


def seq_clean(seq, data_type="none"):
    if data_type == "zhihu":
        pat = re.compile(r"…* *显示全部\s*")
        seq = pat.sub("", seq)
    elif data_type == "weibo_tang":
        pat = re.compile(r"\[.*?\] *")
        pat1 = re.compile(r"［.*?］ *")
        seq = pat.sub("", seq)
        seq = pat1.sub("", seq)
    if contain_at(seq):
        seq = ""
    if "尼玛" in seq:
        seq = ""
    seq = seq.replace("[图片]", "")
    seq = seq.replace("［图片］", "")
    return seq


def single_func(path, outpath, extra_func=False, min_length=2, max_length=256):
    try:
        new_data = []
        print("loading", path)
        print("outpath", outpath)
        # data = load_jsonl(path)
        data = load_txt(path)
        data = [x.split("\t\t") for x in data]
        for dialog in tqdm.tqdm(data):
            new_dialog = []
            for seq in dialog:

                if extra_func:
                    if "zhihu" in path:
                        data_type = "zhihu"
                    elif "weibo_tang" in path:
                        data_type = "weibo_tang"
                    else:
                        data_type = "none"
                    seq = seq_clean(seq, data_type)

                seq = seq.replace(" ", "")
                length = len(seq)
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
        # save_jsonl(new_data, outpath)
        new_data = ["\t\t".join(x[:j]) for x in new_data for j in range(1, len(x))]
        save_txt("\n".join(new_data), outpath)
        print("over", path)
    except Exception as e:
        print("error!!!!", e)
    return


def main(indir, outdir, extra_func=False):
    paths = [os.path.join(instance[0], file)
             for instance in list(os.walk(indir))
             for file in instance[-1] if file.endswith(".txt")]

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
        time.sleep(0.01)
    time.sleep(0.01)
    p.close()
    p.join()
    print("over")


if __name__ == '__main__':
    # filter_dist("./toy_data/raw/", "./toy_data/output/", True)
    main(sys.argv[1], sys.argv[2], True)
