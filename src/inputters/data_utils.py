import json
import gzip
import pickle
import os
import time
import subprocess


def load_pkl(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


def load_txt(path):
    with open(path, encoding='UTF-8', errors='ignore') as f:
        data = [i.strip() for i in f.readlines() if len(i.strip()) > 0]
    return data


def save_txt(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(data)


def load_json(path):
    with open(path, 'r', encoding='UTF_8') as f:
        return json.load(f)


def save_json(data, path, indent=0):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_jsonl(path):
    with open(path, 'r', encoding='UTF_8') as f:
        return [json.loads(line) for line in f.readlines() if len(line.strip()) > 0]


def save_jsonl(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write("\n".join(json.dumps(line, ensure_ascii=False) for line in data))


def load_gz_jsonl(path):
    with gzip.open(path, "rb") as f:
        return [json.loads(line) for line in f.readlines() if len(line.strip()) > 0]


def load_lines(path, start, end):
    data = []
    with open(path, encoding="utf-8") as f:
        i = -1
        for line in f:
            i += 1
            if i > end - 1:
                break
            if i > start - 1:
                if len(line.strip()) > 0:
                    data.append(json.loads(line))
    return data


def dist_prepare_file_offset(path):
    """Fill the file index and offsets of each line in files_list in offset_list
    Args:
        path: string of file path, support single file or file dir
    return:
        files_list: the list contains file names
        offset_list: the list contains the tuple of file name index and offset
    """
    files_list, offset_list = [], []
    if os.path.isdir(path):  # for multi-file, its input is a dir
        files_list.extend([os.path.join(path, f) for f in os.listdir(path)])
    elif os.path.isfile(path):  # for single file, its input is a file
        files_list.append(path)
    else:
        raise RuntimeError(path + " is not a normal file.")
    for i, f in enumerate(files_list):
        offset = 0
        with open(f, "r", encoding="utf-8") as single_file:
            for line in single_file:
                tup = (i, offset)
                offset_list.append(tup)
                offset += len(bytes(line, encoding='utf-8'))
    return files_list, offset_list


def dist_get_line(index, data_files, data_files_offset):
    tup = data_files_offset[index]
    target_file = data_files[tup[0]]
    with open(target_file, "r", encoding="utf-8") as f:
        f.seek(tup[1])
        line = f.readline()
    return line


def dist_get_lines(start, end, data_files, data_files_offset):
    tup = data_files_offset[start]
    target_file = data_files[tup[0]]
    data = []
    with open(target_file, "r", encoding="utf-8") as f:
        f.seek(tup[1])
        i = -1
        for line in f:
            i += 1
            if i > end - 1:
                break
            if len(line.strip()) > 0:
                data.append(json.loads(line))
    return data


def wc_count(file_name):
    out = subprocess.getoutput("wc -l %s" % file_name)
    return int(out.split()[0]) + 1


if __name__ == '__main__':
    print("testing")
    path = "weibo_tang300/2020030911.jsonl"
    files_list, offset_list = dist_prepare_file_offset(path)
    s_t = time.time()
    # data = load_lines(path, 500000, 1000000)
    data = dist_get_lines(500000, 1000000, files_list, offset_list)
    print(time.time() - s_t)
    print(data[0], data[-1], len(data))
