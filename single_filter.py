import os
import gc
import tqdm
import jieba
import time
import collections
import logging

from cleantext import clean

from data_utils import *
from rules import str_level, session_level, data_level

logger = logging.getLogger(__file__)

MAX_LEN_STR_BLACKWORD = 110


def main_filter(opt, file_id, data, blacklist, out_dir, cut=True):
    out_path = os.path.join(out_dir, file_id + ".jsonl")
    try:
        logger.info("The saved path of data is {}".format(out_path))

        if not os.path.exists(os.path.dirname(out_path)):
            logger.error("{} dost not exist!!!!!!".format(os.path.dirname(out_path)))
            return

        logger.info("{} start".format(file_id))
        # data = loader(path)
        logger.info("Size of this batch : {}, log in {}".format(len(data), file_id))

        dirty_data = {k: collections.defaultdict(set) for k in
                      ["other", "name", "str_blacklist", "word_blacklist", "not_en", "confused", "generic", "emoji",
                       "duplicated", "confuse"]}

        logger.info("Batch sample: {}, log in {}".format(data[0][0], file_id))

        time_dict = collections.defaultdict(float)

        global MAX_LEN_STR_BLACKWORD
        MAX_LEN_STR_BLACKWORD = max(len(x) for x in blacklist["str_blacklist"]) + 2

        res = []
        for dialog in tqdm.tqdm(data, mininterval=1):
            # session level
            # dialog = session_check(opt, dialog)
            if opt.utterance_dedup:
                if len(set(dialog)) < 2:
                    if len(set(dialog)) > 0:
                        dirty_data["duplicated"]["utterance_level"].add(dialog[0])
                    continue

            new_dialog = []
            for i in range(len(dialog)):
                if opt.split_multi_repost:
                    utters = str_level.split_multi_repost(dialog[i])
                else:
                    utters = [dialog[i]]

                for j, utter in enumerate(utters):
                    if opt.no_toupiao and (j + 1) < len(utters):
                        toupiao = str_level.no_toupiao(utters[j + 1])
                        if toupiao:
                            continue
                    utter = utterance_clean(opt, utter, blacklist, dirty_data, time_dict, cut)
                    new_dialog.append(utter)

            if opt.no_name:
                new_dialog = session_level.de_name(new_dialog, blacklist["name"])

            start_idx = 0 if new_dialog[0] else 1
            for i in range(1, len(new_dialog) + 1):
                if i == len(new_dialog) or not new_dialog[i]:
                    if opt.no_short_response:
                        part_dialog = new_dialog[start_idx: i][:]
                        part_dialog = session_level.no_short_response(part_dialog)
                        if len(part_dialog) > 1:
                            res.append(part_dialog)
                    else:
                        if len(new_dialog[start_idx: i]) > 1:
                            res.append(new_dialog[start_idx: i])
                    start_idx = i + 1
            # for i in range(1, len(new_dialog)):
            #     if not new_dialog[i]:
            #         if len(new_dialog[start_idx: i]) > 1:
            #             res.append(new_dialog[start_idx: i])
            #         start_idx = i + 1
            #     elif i == len(new_dialog) - 1:
            #         if len(new_dialog[start_idx:]) > 1:
            #             res.append(new_dialog[start_idx:])

        del data
        gc.collect()

        # data level
        if opt.de_ad:
            res = data_level.de_ad(res, dirty_data)

        if opt.de_generic_dialog:
            res = data_level.de_generic(res, dirty_data, out_path.replace(".jsonl", "_trigram.jsonl"), 1000)

        if len(res) > 0:
            save_jsonl(res, out_path)

        # save dirty data
        dirty_dir = os.path.join(out_dir, "dirty_data")
        if not os.path.isdir(dirty_dir):
            os.mkdir(dirty_dir)
        for k, v in dirty_data.items():
            k_path = os.path.join(dirty_dir, k)
            if sum(len(subv) for subv in v.values()):
                if not os.path.isdir(k_path):
                    os.mkdir(k_path)
                if "blacklist" in k and len(v) > 0:
                    temp_bl = {bk: len(bv) for bk, bv in v.items()}
                    temp_bl = sorted(temp_bl.items(), key=lambda x: x[1], reverse=True)
                    save_json(temp_bl, os.path.join(k_path, "sta_{}.json".format(file_id)))
                    save_json({bk: list(bv) for bk, bv in v.items()}, os.path.join(k_path, "{}.json".format(file_id)))
                else:
                    for sub_k, sub_v in v.items():
                        if len(sub_v) > 0:
                            save_jsonl(sub_v, os.path.join(k_path, "{}_{}.jsonl".format(sub_k, file_id)))
        logger.info("{}  over, resulting {} dialogs".format(file_id, len(res)))
    except Exception as e:
        logger.error("Error !!!! : {}, log in {}".format(e, out_path))
    return file_id


def add_filter_args(argparser):
    opt = argparser.add_argument_group('Filter Arguments')

    opt.add_argument('--utterance_dedup', action="store_true")
    opt.add_argument('--no_name', action="store_true")
    opt.add_argument('--split_multi_repost', action="store_true")
    opt.add_argument('--de_ad', action="store_true")
    opt.add_argument('--de_generic_dialog', action="store_true")
    opt.add_argument('--no_reply_tag', action="store_true")
    opt.add_argument('--no_hashtag', action="store_true")
    opt.add_argument('--no_emotion', action="store_true")
    opt.add_argument('--no_mention', action="store_true")
    opt.add_argument('--no_repost', action="store_true")
    opt.add_argument('--no_brackets', action="store_true")
    opt.add_argument('--no_duplicated', action="store_true")
    opt.add_argument('--no_emoji', action="store_true")
    opt.add_argument('--no_short', action="store_true")
    opt.add_argument('--no_long', action="store_true")
    opt.add_argument('--no_special_topic', action="store_true")
    opt.add_argument('--bert_clean', action="store_true")
    opt.add_argument('--use_cleantext_lib', action="store_true")
    opt.add_argument('--no_str_blacklist', action="store_true")
    opt.add_argument('--no_toupiao', action="store_true")
    opt.add_argument('--no_short_response', action="store_true")

    # words list level
    opt.add_argument('--no_word_blacklist', action="store_true")
    opt.add_argument('--no_alpha_noise', action="store_true")
    opt.add_argument('--check_confuse_word', action="store_true")
    opt.add_argument('--yda_dedupl', action="store_true")


def utterance_clean(opt, utterance, blacklist, dirty_data, time_dict, cut, return_segmented=True) -> str:
    orig_utter = utterance
    utterance = utterance.strip()

    utterance = utterance.replace("alink", "")
    # TODO check
    utterance = utterance.replace("{\\1c&H4080FF&}", "")
    if not utterance:
        dirty_data["other"]["{\\1c&H4080FF&}"].add(orig_utter)

    # TODO check
    if "¡ 评论" in utterance:
        utterance = utterance[:utterance.index("¡ 评论")]
        if not utterance:
            dirty_data["other"]["¡ 评论"].add(orig_utter)

    if utterance and opt.no_toupiao:
        toupiao = str_level.no_toupiao(utterance)
        if toupiao:
            dirty_data["other"]["toupiao"].add(orig_utter)
            utterance = ""

    if utterance and opt.no_special_topic:
        special_topic_word = str_level.de_str_blacklist(utterance, blacklist["special_topic"])
        if special_topic_word:
            dirty_data["special_topic"][special_topic_word].add(orig_utter)
            utterance = ""

    if utterance and opt.no_str_blacklist:
        global MAX_LEN_STR_BLACKWORD
        black_word = str_level.de_str_blacklist2(utterance, blacklist["str_blacklist"], MAX_LEN_STR_BLACKWORD)
        if black_word:
            dirty_data["str_blacklist"][black_word].add(orig_utter)
            utterance = ""

    if utterance and opt.no_reply_tag:
        utterance = str_level.REPLY_MENTION_REGEX.sub("", utterance).strip()
        if not utterance:
            dirty_data["other"]["no_reply_tag"].add(orig_utter)

    if utterance and opt.no_hashtag:
        utterance = str_level.HASHTAG_REGEX.sub("", utterance).strip()

    if utterance and opt.no_emotion:
        utterance = str_level.EMOTION_REGEX.sub("", utterance).strip()

    if utterance and opt.no_mention:
        utterance = str_level.COMMON_MENTION_REGEX.sub("", utterance).strip()

    if utterance and opt.no_repost:
        utterance = str_level.REPPOST_MENTION_REGEX.sub("", utterance).strip()

    if utterance and opt.no_brackets:
        utterance = str_level.BRACKETS_REGEX.sub("", utterance).strip()
        if not utterance:
            dirty_data["emoji"]["weibo_emoji"].add(orig_utter)

    if utterance and opt.no_duplicated:
        utterance = str_level.reduce_duplicated_phrase(utterance)

    if utterance and opt.no_emoji:
        utterance = str_level.remove_emoji(utterance)
        if not utterance:
            dirty_data["emoji"]["emoji"].add(orig_utter)

    # clean-text lib
    if utterance and opt.use_cleantext_lib:
        utterance = clean(
            utterance,
            fix_unicode=True,
            to_ascii=False,
            normalize_whitespace=True,
            no_line_breaks=True,
            no_urls=True,
            no_emails=True,
            no_phone_numbers=True,
            replace_with_url="<URL>",
            replace_with_email="<EMAIL>",
            replace_with_phone_number="<PHONE>")
        if not utterance:
            dirty_data["other"]["cleantext"].add(orig_utter)

    if utterance and opt.no_short:
        len_flag = str_level.too_short(utterance)
        if len_flag:
            dirty_data["other"]["short"].add(orig_utter)
            utterance = ""

    if utterance and opt.no_long:
        len_flag = str_level.too_long(utterance)
        if len_flag:
            dirty_data["other"]["long"].add(orig_utter)
            utterance = ""

    if utterance and opt.bert_clean:
        utterance = str_level.bert_clean(utterance)

    ### word level
    if cut:
        word_list = list(jieba.cut(utterance))
    else:
        word_list = utterance.strip().split()

    if word_list and opt.no_alpha_noise:
        alpha_word = str_level.not_en(word_list, blacklist["english"])
        if alpha_word:
            dirty_data["not_en"][alpha_word].add(orig_utter)
            word_list = []
            utterance = ""

    if word_list and opt.check_confuse_word:
        confuse_word = str_level.check_confuse(word_list, blacklist["confuse"])
        if confuse_word:
            dirty_data["confuse"][confuse_word].add(orig_utter)

    if word_list and opt.no_word_blacklist:
        dirty_word = str_level.de_word_blacklist(word_list, blacklist["word_blacklist"])
        if dirty_word:
            dirty_data["word_blacklist"][dirty_word].add(orig_utter)
            word_list = []
            utterance = ""

    if word_list and opt.yda_dedupl:
        yda_dupl_flag = str_level.judge_yda_dupl(word_list)
        if yda_dupl_flag:
            dirty_data["duplicated"]["yda"].add(orig_utter)
            word_list = []
            utterance = ""

    return " ".join(word_list).strip() if return_segmented else utterance.strip()
