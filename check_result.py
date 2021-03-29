import os
import sys
from run_dist import dataloader


def check_files_successed(raw_dir, out_dir, batch_size=500000):
    simple_loader = dataloader(raw_dir, batch_size)
    out_dir = os.path.join(out_dir, "after_dist")

    failed_files = []
    for file_id, data in simple_loader:
        out_path = os.path.join(out_dir, file_id + ".jsonl")
        if not os.path.exists(out_path):
            failed_files.append(out_path)
    print(failed_files)
    print(len(failed_files))
    return


if __name__ == '__main__':
    check_files_successed(sys.argv[1], sys.argv[2])
