import os
import logging
from multiprocessing import Pool
from argparse import ArgumentParser

from single_filter import main_filter, add_filter_args
from data_utils import *

logger = logging.getLogger(__file__)


def dataloader(dir_path, batch_size):
    """Load jsonl data, each line should be a list of dialog: ["你好", "你也好", "哈哈"]"""
    subdirs = [(subdir, os.path.join(dir_path, subdir)) for subdir in os.listdir(dir_path)]
    jsonl_path_list = [(file, subdir_name, os.path.join(subdir, file))
                       for subdir_name, subdir in subdirs
                       for file in os.listdir(subdir)]
    for file, subdir_name, path in jsonl_path_list:
        dataset = load_jsonl(path)
        for i in range(0, len(dataset), batch_size):
            fid = subdir_name + "_" + file.replace(".jsonl", "") + "_trunc" + str(i)
            yield fid, dataset[i: i + batch_size]


def get_filter_set(tool_dir):
    black_str_set = set(load_txt(os.path.join(tool_dir, "black_str_vocab.txt")))
    black_list_set = set(load_txt(os.path.join(tool_dir, "black_list_vocab.txt")))
    special_topic_str_set = set(load_txt(os.path.join(tool_dir, "special_topic.txt")))
    person_name_set = set(load_txt(os.path.join(tool_dir, "person_name.txt")))
    en_set = {'l', '.', 'W', 't', 'o', 'z', 'k', 'C', 'B', 'y', '/', 'w', 'a', 's', 'h', 'x', '_', 'n', 'g', 'i',
              'd', 'e'}
    confuse_set = set()
    blacklist = {"name": person_name_set, "str_blacklist": black_str_set, "word_blacklist": black_list_set,
                 "confuse": confuse_set, "english": en_set, "special_topic": special_topic_str_set}
    return blacklist


def main():
    parser = ArgumentParser()
    parser.add_argument("--n_p", type=int, default=32, help="Number of subprocess")
    parser.add_argument("--batch_size", type=int, default=500000)
    parser.add_argument("--tool_dir", type=str, default="./tool_data/",
                        help="Path of the tool data.")

    parser.add_argument("--out_dir", type=str, default="./data/", help="Main data dir.")
    parser.add_argument("--raw_dir", type=str, default="./data/raw/", help="Dir of the raw dataset.")
    add_filter_args(parser)
    args = parser.parse_args()

    logger.info("Preparing")
    after_dist_dir = os.path.join(args.out_dir, "after_dist")
    if not os.path.isdir(after_dist_dir):
        os.mkdir(after_dist_dir)

    simple_loader = dataloader(args.raw_dir, args.batch_size)
    blacklists = get_filter_set(args.tool_dir)

    # single process debug
    # file_id, data = next(simple_loader)
    # file_id, data = next(simple_loader)
    # main_filter(args, file_id, data, blacklists, after_dist_dir)
    # exit()

    # multi processing
    logger.info("Cleaning start!")
    p = Pool(args.n_p)
    for file_id, data in simple_loader:
        p.apply_async(main_filter, args=(args, file_id, data, blacklists, after_dist_dir))
    p.close()
    p.join()
    logger.info("Cleaning over!")
    return


if __name__ == '__main__':
    main()
