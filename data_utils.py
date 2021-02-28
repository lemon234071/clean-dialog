import json
import gzip
import pickle


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
