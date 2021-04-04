import re
import emoji
import time
import unicodedata

from nltk.corpus import wordnet

SPECIFIC = {"repost", "转发", "repostweibo"}

# 感恩节# 感谢给予自己生命，养育我们长大的父母，他们教会了我们爱、善良和尊严。
HASHTAG_REGEX = re.compile(r"#.*?# *")

EMOTION_REGEX = re.compile(r":.*?: *")

BRACKETS_REGEX = re.compile(r"\[.*?\] *")

# TODO ???
# 当小猫用他特殊的方式安慰你的时候，再坚硬的心也会被融化。[happy][happy] ˆ_ˆ ˆ_ˆ
WEIBO_EMOJI_REGEX = re.compile(r"[?(?:. ?){1,10} ?]")
# r"\[?(?:. ?){1,10} ?\]"

# TODO replace the @somebody to NAME1, NAME2 ....???
# 一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？
# COMMON_MENTION_REGEX = re.compile(r"(@+)\S+")
# COMMON_MENTION_REGEX = re.compile(r"(@+)(.*?):")
COMMON_MENTION_REGEX = re.compile(r"(@+)(\S+?\s*?): *")

# TODO ???
# 一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？
REPPOST_MENTION_REGEX = re.compile(r"/ ?/? ?@ ?(?:[\w \-] ?){,30}? ?:.+")

# 回复 @Devid: 我会准时到的
REPLY_MENTION_REGEX = re.compile(r"回复 *@.*?: *")

WEIBO_URL_REGEX = re.compile(r"(?:(?:https?:?\/\/|ftp:\/\/|www\d{0,3}\.)t\.cn\/[a-zA-Z0-9]{0,8})")

ZHIHU_SHOW_ALL_REGEX = re.compile(r"...显示全部\s*")


def too_short(utter, length=2):
    temp = utter.replace(" ", "")
    return True if len(temp) < length else False


def too_long(utter, length=1000):
    temp = utter.replace(" ", "")
    return True if length < len(temp) else False


def remove_emoji(text):
    for x in emoji.UNICODE_EMOJI:
        if x in text:
            text = text.replace(x, "")
    return text.strip()


MAX_LEN_EMOJI = max(len(x) for x in emoji.UNICODE_EMOJI.keys()) + 2


def remove_emoji2(utter):
    blacklist = set(emoji.UNICODE_EMOJI.keys())
    # max_len = max(len(x) for x in blacklist)
    all_gram = set([utter[i:j + 1] for i in range(len(utter)) for j in range(i, min(len(utter), i + MAX_LEN_EMOJI))])
    overlap = blacklist & all_gram
    if len(overlap) > 0:
        return overlap.pop()
    return None


def no_toupiao(utter):
    temp = utter.replace(" ", "")
    if "我投给了" in temp and "你也快来表态吧" in temp:
        return True
    return False


def no_fenxiang(utter):
    if utter == "分享图片":
        return True
    return False


def no_specific_utter(utter):
    if utter in SPECIFIC:
        return True
    return False


# TODO speed up
def de_str_blacklist(utter, blacklist):
    for word in blacklist:
        if word in utter:
            return word
    return None


def de_str_blacklist2(utter, blacklist, max_len=110):
    # max_len = max(len(x) for x in blacklist)
    all_gram = set([utter[i:j + 1] for i in range(len(utter)) for j in range(i, min(len(utter), i + max_len))])
    overlap = blacklist & all_gram
    if len(overlap) > 0:
        return overlap.pop()
    return None


def check_confuse(word_list, confuse_set):
    for word in word_list:
        for confuse in confuse_set:
            if confuse in word:
                return word
    return None


def de_word_blacklist(word_list, blacklist):
    for word in word_list:
        if word in blacklist:
            return word
    return False


def not_en(word_list, en_set):
    for word in word_list:
        if word.encode('UTF-8').isalpha():
            if not wordnet.synsets(word):
                if word not in en_set:
                    return word
    return None


def bert_clean(text):
    """From transformers.BertTokenizer"""
    """Performs invalid character removal and whitespace cleanup on text."""

    def _is_control(char):
        """Checks whether `chars` is a control character."""
        # These are technically control characters but we count them as whitespace
        # characters.
        if char == "\t" or char == "\n" or char == "\r":
            return False
        cat = unicodedata.category(char)
        if cat.startswith("C"):
            return True
        return False

    def _is_whitespace(char):
        """Checks whether `chars` is a whitespace character."""
        # \t, \n, and \r are technically contorl characters but we treat them
        # as whitespace since they are generally considered as such.
        if char == " " or char == "\t" or char == "\n" or char == "\r":
            return True
        cat = unicodedata.category(char)
        if cat == "Zs":
            return True
        return False

    output = []
    for char in text:
        cp = ord(char)
        if cp == 0 or cp == 0xfffd or _is_control(char):
            continue
        if _is_whitespace(char):
            output.append(" ")
        else:
            output.append(char)
    return "".join(output)


def split_multi_repost(utter):
    # 一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？
    if utter.find("//@") > -1:
        utters = [x.strip() for x in utter.split("//@")]
        for i in range(1, len(utters)):
            if utters[i]:
                utters[i] = "@" + utters[i]
        return utters
    return [utter]


# TODO shorter the phrase instead of removing whole utterance
def judge_duplicated_phrase(seq_str, times, length=2):
    """
    :type seq_str: str
    :rtype: bool
    """
    count = 0
    n = len(seq_str)
    for k in range(n - (times + 1) * (length + 1)):
        for i in range(times - 1, (n - k) // times + 1):
            a = seq_str[k: k + i]
            j = k + i
            while j < n and i > length and seq_str[j:j + i] == a:
                j += i
                count += 1
                if count > (times - 2):
                    return True
    return False


def reduce_duplicated_phrase(seq_str, times=3, length=1):
    while length * (times + 1) < len(seq_str):
        # 0 1 2 3 4, 5 6 7 8 9 10 11
        # l = 2,  t = 3
        i = 0
        while i + length * (times + 1) <= len(seq_str):
            substr = seq_str[i:i + length]
            j = i + length
            while (j + length) <= len(seq_str) and seq_str[j:j + length] == substr:
                j += length
            if (i + length * times) < j:
                seq_str = seq_str[:i + length * times] + seq_str[j:]
            i += 1
        length += 1
    return seq_str


def judge_yda_dupl(seq_list):
    word_dict = {}
    for word in seq_list:
        if word in word_dict:
            word_dict[word] += 1
        else:
            word_dict[word] = 1
            # fitler duplicate
    num_list = list(word_dict.values())
    num_list.sort(reverse=True)

    if len(num_list) <= 1 / 3 * len(seq_list):
        return True

    return 3 < len(num_list) < len(seq_list) and sum(
        num_list[:3]
    ) > 0.75 * len(seq_list)


def deduplicate_chars(seq_str, no_single=False):
    """truncate char duplication more than a number"""
    char_set = set(seq_str)
    n = 0
    last_char = None
    seven_i = 0
    new_list = []
    last_i = 0
    for i, char in enumerate(seq_str):
        if char == last_char:
            n += 1
            if n == 6:
                seven_i = i
        else:
            if n > 5:
                new_list.append(seq_str[last_i:seven_i])
                last_i = i
            n = 0
        last_char = char

    end = seven_i if n > 5 else len(seq_str)
    new_list.append(seq_str[last_i:end].strip())
    if no_single and len(char_set) < 2 and 4 < len(seq_str):
        return ""
    return "".join(new_list) if new_list else seq_str


# TODO Regex and words
# DUPLICATE_WORDS_REGEX = re.compile(r"(?P(?P\S-(\S.*\S))  (?:\s*(?P=item)) {1})   (?:\s*(?P=item)) {2,}")
# DUPLICATE_WORDS_REGEX = re.compile(r"(.+?(?P<item>\S)(?:\s*(?P=item)))(?:\s*(?P=item)){2,}")

if __name__ == '__main__':
    # print("Testing the RegEx")
    # test_text = "一起来吗？@Cindy //@Bob: 算我一个//@Amy:今晚开派对吗？"
    # pat = re.compile(r"/ ?/? ?@ ?(?:[\w \-] ?){,30}? ?:.+")
    # print(pat.sub("XXX", test_text))
    #
    # test_text = "🤔 🙈 me, se 😌 ds 💕👭👙 hello 👩🏾‍🎓 emoji hello 👨‍👩‍👦‍👦 how are 😊 you today🙅🏽🙅🏽"
    # s_t = time.time()
    # for i in range(100000):
    #     remove_emoji2(test_text)
    # print(time.time() - s_t)
    # test_text = "哈哈哈哈哈 你好啊 你好啊你好啊你好啊你好啊你好啊 今晚开派对吗？哈哈哈哈 今晚开派对吗？今晚开派对吗？今晚开派对吗？今晚开派对吗？hhhhhhhhh"
    # print(reduce_duplicated_phrase(test_text))
    #
    # URL_REGEX = re.compile(
    #     r"(?:^|(?<![\w\/\.]))"
    #     # protocol identifier
    #     # r"(?:(?:https?|ftp)://)"  <-- alt?
    #     r"(?:(?:https?:\/\/|ftp:\/\/|www\d{0,3}\.))"
    #     # user:pass authentication
    #     r"(?:\S+(?::\S*)?@)?" r"(?:"
    #     # IP address exclusion
    #     # private & local networks
    #     r"(?!(?:10|127)(?:\.\d{1,3}){3})"
    #     r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
    #     r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
    #     # IP address dotted notation octets
    #     # excludes loopback network 0.0.0.0
    #     # excludes reserved space >= 224.0.0.0
    #     # excludes network & broadcast addresses
    #     # (first & last IP address of each class)
    #     r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    #     r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
    #     r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
    #     r"|"
    #     # host name
    #     r"(?:(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)"
    #     # domain name
    #     r"(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*"
    #     # TLD identifier
    #     r"(?:\.(?:[a-z\\u00a1-\\uffff]{2,}))" r"|" r"(?:(localhost))" r")"
    #     # port number
    #     r"(?::\d{2,5})?"
    #     # resource path
    #     r"(?:\/[^\)\]\}\s]*)?",
    #     # r"(?:$|(?![\w?!+&\/\)]))",
    #     # @jfilter: I removed the line above from the regex because I don't understand what it is used for, maybe it was useful?
    #     # But I made sure that it does not include ), ] and } in the URL.
    #     flags=re.UNICODE | re.IGNORECASE,
    # )
    # test_text = "郭麒麟打卡,且听他分享防疫小知识。 http//t.cn/a67ov8bt"
    # pat = re.compile(r"(?:(?:https?:?\/\/|ftp:\/\/|www\d{0,3}\.)t\.cn\/[a-zA-Z0-9]{0,8})")
    # print(pat.sub("XXX", test_text))
    # pat2 = URL_REGEX
    # print(pat2.sub("XXX", test_text))
    # test_text = '@优优教程网 :连做法都告诉大家了[偷笑]@优优教程网:hahahhah[偷笑]@优优教程网 :嘻嘻嘻[偷笑]@:asdsada哈哈[偷笑]'
    # pat = re.compile(r"(@+)(.+?):")
    # print(pat.sub("XXX", test_text))
    #
    # pats = [HASHTAG_REGEX, EMOTION_REGEX, BRACKETS_REGEX, WEIBO_EMOJI_REGEX, COMMON_MENTION_REGEX,
    #         REPPOST_MENTION_REGEX, REPLY_MENTION_REGEX, WEIBO_URL_REGEX]
    # for pat in pats:
    #     # print(pat)
    #     print(pat.sub("XXX", test_text))

    test_text = "一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？@优优教程网 :连做法都告诉大家了[偷笑]@优优教程网:hahahhah[偷笑]@优优教程网 :嘻嘻嘻[偷笑]@:asdsada哈哈[偷笑]"
    pat = re.compile(r"(@+)(\S+?\s*?): *")
    print(pat.sub("XXX", test_text))
