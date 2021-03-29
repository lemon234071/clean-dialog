import os
import sys


def dataloader(dir_path, batch_size):
    """Load jsonl data, each line should be a list of dialog: ["你好", "你也好", "哈哈"]"""
    subdirs = [(subdir, os.path.join(dir_path, subdir)) for subdir in os.listdir(dir_path)]
    jsonl_path_list = [(file, subdir_name, os.path.join(subdir, file))
                       for subdir_name, subdir in subdirs
                       for file in os.listdir(subdir) if file.endswith(".jsonl")]
    for file, subdir_name, path in jsonl_path_list:
        count = 0
        for line in open(path):
            count += 1
        for i in range(0, count, batch_size):
            fid = subdir_name + "_" + file.replace(".jsonl", "") + "_trunc" + str(i)
            yield fid


def check_files_successed(raw_dir, out_dir, batch_size=500000):
    simple_loader = dataloader(raw_dir, batch_size)
    out_dir = os.path.join(out_dir, "after_dist")

    in_raw = []
    in_res = [os.path.join(out_dir, x) for x in os.listdir(out_dir)]

    for file_id in simple_loader:
        out_path = os.path.join(out_dir, file_id + ".jsonl")
        in_raw.append(out_path)

    not_in_raw = set(in_res) - set(in_raw)
    print(not_in_raw)
    print("not in raw", len(not_in_raw))

    not_in_res = set(in_raw) - set(in_res)
    print(not_in_res)
    print("not in res", len(not_in_res))
    return


if __name__ == '__main__':
    check_files_successed(sys.argv[1], sys.argv[2])
