import os
import logging
import time
import random
from multiprocessing import Pool
from argparse import ArgumentParser

from src.single_filter import main_filter, add_filter_args
from src.inputters.dataloaders import paths_dataloader
from src.inputters.data_utils import *

random.seed(42)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  # - %(name)s
logger = logging.getLogger(__file__)


def get_filter_set(tool_dir):
    blacklist = {}

    if os.path.exists(os.path.join(tool_dir, "black_str_vocab.txt")):
        black_str_set = set(load_txt(os.path.join(tool_dir, "black_str_vocab.txt")))
        blacklist["str_blacklist"] = black_str_set

    if os.path.exists(os.path.join(tool_dir, "black_list_vocab.txt")):
        black_list_set = set(load_txt(os.path.join(tool_dir, "black_list_vocab.txt")))
        blacklist["word_blacklist"] = black_list_set

    if os.path.exists(os.path.join(tool_dir, "special_topic.txt")):
        special_topic_str_set = set(load_txt(os.path.join(tool_dir, "special_topic.txt")))
        blacklist["special_topic"] = special_topic_str_set

    if os.path.exists(os.path.join(tool_dir, "person_name.txt")):
        person_name_set = set(load_txt(os.path.join(tool_dir, "person_name.txt")))
        blacklist["name"] = person_name_set

    en_set = {'l', '.', 'W', 't', 'o', 'z', 'k', 'C', 'B', 'y', '/', 'w', 'a', 's', 'h', 'x', '_', 'n', 'g', 'i',
              'd', 'e'}
    blacklist["english"] = en_set

    confuse_set = set()
    blacklist["confuse"] = confuse_set

    return blacklist


def main():
    parser = ArgumentParser()
    parser.add_argument("--n_p", type=int, default=32, help="Number of subprocess")
    parser.add_argument("--batch_size", type=int, default=500000)
    parser.add_argument("--tool_dir", type=str, default="./tool_data/",
                        help="Path of the tool data.")

    parser.add_argument("--out_dir", type=str, default="./data/", help="Main data dir.")
    parser.add_argument("--dirty_dir", type=str, default="", help="Dir to save dirty cases.")
    parser.add_argument("--raw_dir", type=str, default="./data/raw/", help="Dir of the raw dataset.")
    add_filter_args(parser)
    args = parser.parse_args()
    logger.info(args)
    p = Pool(args.n_p)

    logger.info("Preparing")
    dataloader = paths_dataloader(args.raw_dir, args.out_dir, args.batch_size)
    blacklists = get_filter_set(args.tool_dir)

    # single process debug
    # file_id, data = next(simple_loader)
    # file_id, data, outpath = next(simple_loader)
    # main_filter(args, file_id, data, blacklists, outpath, args.out_dir)
    # exit()

    # multi processing
    logger.info("Cleaning start!")
    for file_id, path, start, end, outpath in dataloader:
        data = (path, start, end)
        p.apply_async(main_filter, args=(args, file_id, data, blacklists, outpath, args.dirty_dir))
        time.sleep(0.01)
    time.sleep(0.01)
    p.close()
    p.join()
    logger.info("Cleaning over!")
    return


if __name__ == '__main__':
    main()
