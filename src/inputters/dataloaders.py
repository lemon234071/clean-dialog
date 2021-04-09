import os
import random
from src.inputters.data_utils import *


def simple_dataloader(dir_path, out_dir, batch_size):
    """Load jsonl data, each line should be a list of dialog: ["你好", "你也好", "哈哈"]"""
    cleaned_dir = os.path.join(out_dir, "cleaned_data")
    if not os.path.exists(cleaned_dir):
        os.mkdir(cleaned_dir)

    subdirs = [(subdir, os.path.join(dir_path, subdir)) for subdir in os.listdir(dir_path)]
    jsonl_path_list = [(file, subdir, os.path.join(subdir_path, file))
                       for subdir, subdir_path in subdirs
                       for file in os.listdir(subdir_path) if file.endswith(".jsonl")]
    # random.shuffle(jsonl_path_list)
    for file, subdir_name, path in jsonl_path_list:
        dataset = load_jsonl(path)
        for i in range(0, len(dataset), batch_size):
            fid = subdir_name + "_" + file.replace(".jsonl", "") + "_trunc" + str(i)
            # out
            out_subdir = os.path.join(cleaned_dir, subdir_name)
            if not os.path.exists(out_subdir):
                os.mkdir(out_subdir)
            out_path = os.path.join(out_subdir, fid + ".jsonl")
            yield fid, dataset[i: i + batch_size], out_path


def paths_dataloader(dir_path, out_dir, batch_size):
    """Load jsonl data, each line should be a list of dialog: ["你好", "你也好", "哈哈"]"""
    cleaned_dir = os.path.join(out_dir, "cleaned_data")
    if not os.path.exists(cleaned_dir):
        os.mkdir(cleaned_dir)

    subdirs = [(subdir, os.path.join(dir_path, subdir)) for subdir in os.listdir(dir_path)]
    jsonl_path_list = [(file, subdir, os.path.join(subdir_path, file))
                       for subdir, subdir_path in subdirs
                       for file in os.listdir(subdir_path) if file.endswith(".jsonl")]
    # random.shuffle(jsonl_path_list)
    for file, subdir_name, path in jsonl_path_list:
        # dataset = load_jsonl(path)
        file_len = wc_count(path)
        for i in range(0, file_len, batch_size):
            fid = subdir_name + "_" + file.replace(".jsonl", "") + "_trunc" + str(i)
            # out
            out_subdir = os.path.join(cleaned_dir, subdir_name)
            if not os.path.exists(out_subdir):
                os.mkdir(out_subdir)
            out_path = os.path.join(out_subdir, fid + ".jsonl")
            yield fid, path, i, i + batch_size, out_path
