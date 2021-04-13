import os
import tqdm
import collections
import logging

from src.inputters.data_utils import *

logger = logging.getLogger(__file__)


def no_ad(data, dirty_data):
    """A Dataset for Research on Short-Text Conversation (Wang et al. 2013)"""
    resp_dict = collections.defaultdict(set)
    for dialog in data:
        for i in range(1, len(dialog)):
            resp_dict[dialog[i]].add(dialog[i - 1])
    ad_resp_dict = {}
    for k, v in resp_dict.items():
        if len(k.replace(" ", "")) > 20 and len(v) > 2:
            ad_resp_dict[k] = len(v)
    ad_resp = sorted(ad_resp_dict.items(), key=lambda x: x[1], reverse=True)
    if dirty_data:
        dirty_data["ad"] = ad_resp
    logger.info("Ad len: {}".format(len(ad_resp)))

    resp_set = set(ad_resp_dict.keys())
    new_data = []
    for dialog in data:
        start = 0
        for i in range(1, len(dialog)):
            if dialog[i] in resp_set:
                if i - start > 2:
                    new_data.append(dialog[start:i])
                    start = i + 1
        if (len(dialog) - start) > 1:
            new_data.append(dialog[start:])
    logger.info("Data len after de_de: {}".format(len(new_data)))
    return new_data


def de_generic(data, dirty_data, tri_path, num):
    """From dialogpt"""

    def ngrams(resp, n):
        ngram = list()
        if len(resp) >= n:
            for i in range(len(resp) - n + 1):
                ngram.append(resp[i: i + n])
        return ngram

    if os.path.exists(tri_path):
        generic = load_jsonl(tri_path)
        print("load from :", tri_path)
    else:
        print("len raw: ", len(data))
        generic = collections.Counter()
        # assert isinstance(dataset[0][0], str)
        for dialog in tqdm.tqdm(data, mininterval=1):
            for seq in dialog[1:]:
                tri_grams = ngrams(seq.replace(" ", ""), 3)
                generic.update(list(set(tri_grams)))

        generic = sorted(generic.items(), key=lambda x: x[1], reverse=True)
        save_jsonl(generic, tri_path)
    generic = set(x for x, cnt in generic if cnt > num)

    new_dataset = []
    for dialog in tqdm.tqdm(data, mininterval=1):
        start_idx = 0
        for i in range(len(dialog)):
            if not i > start_idx:
                continue
            resp = dialog[i].replace(" ", "")
            tri_grams = ngrams(resp, 3)
            cnt = collections.Counter(tri_grams)
            for word, num in cnt.items():
                if word in generic and 0.9 < (num * 3 / len(resp)):
                    if dirty_data:
                        dirty_data["generic"].append(resp)
                    if len(dialog[start_idx: i]) > 1:
                        new_dataset.append(dialog[start_idx: i])
                        start_idx = i + 1
                    break
        if len(dialog[start_idx:]) > 1:
            new_dataset.append(dialog[start_idx:])
    logger.info("Data len after de_generic: {}".format(len(new_dataset)))

    return new_dataset
