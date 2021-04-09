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

ANGLE_REGEX = re.compile(r"<[^\u4e00-\u9fa5]*?>")

# TODO ???
# 当小猫用他特殊的方式安慰你的时候，再坚硬的心也会被融化。[happy][happy] ˆ_ˆ ˆ_ˆ
WEIBO_EMOJI_REGEX = re.compile(r"[?(?:. ?){1,10} ?]")


# r"\[?(?:. ?){1,10} ?\]"

# TODO replace the @somebody to NAME1, NAME2 ....???
# 一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？
# COMMON_MENTION_REGEX = re.compile(r"(@+)\S+")
# COMMON_MENTION_REGEX = re.compile(r"(@+)(.*?):")
# COMMON_MENTION_REGEX = re.compile(r"(@+)(\S*?\s*?): *")
def no_at(seq, tail_length=30):
    temp_pat = re.compile(r"(@+)\S{,30} ")
    seq = temp_pat.sub("", seq)
    r_at_idx = seq.rfind("@")
    if len(seq[r_at_idx:]) < tail_length:
        seq = seq[:r_at_idx]
    return seq


def contain_at(seq, tail_length=30):
    flag = re.search(r"(@+)\S{,30} ", seq)
    if flag is not None:
        return True
    r_at_idx = seq.rfind("@")
    if r_at_idx > -1 and len(seq[r_at_idx:]) < tail_length:
        return True
    return False


SINGLE_REPPOST_MENTION_REGEX = re.compile(r"(@+)(\S*?\s*?): *")

# TODO ???
# 一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？
REPPOST_MENTION_REGEX = re.compile(r"/ ?/? ?@ ?(?:[\w \-] ?){,30}? ?:.+")

# 回复 @Devid: 我会准时到的
REPLY_MENTION_REGEX = re.compile(r"回复 *@.*?: *")

ZHIHU_SHOW_ALL_REGEX = re.compile(r"…* *显示全部\s*")

URL_REGEX = re.compile(
    r"(?:^|(?<![A-Za-z0-9\/\.]))"
    # protocol identifier
    # r"(?:(?:https?|ftp)://)"  <-- alt?
    r"(?:(?:https?:?\/\/|ftp:\/\/|www\d{0,3}\.))"
    # user:pass authentication
    r"(?:\S+(?::\S*)?@)?" r"(?:"
    # IP address exclusion
    # private & local networks
    r"(?!(?:10|127)(?:\.\d{1,3}){3})"
    r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
    r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
    r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
    r"|"
    # host name
    r"(?:(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)"
    # domain name
    # r"(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*"
    r"(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*"
    # TLD identifier
    r"(?:\.(?:[a-z\\u00a1-\\uffff]{2,}))"
    r"|"
    r"(?:(localhost))"
    r")"
    # port number
    r"(?::\d{2,5})?"
    # resource path
    r"(?:\/[^\)\]\}\s\u4e00-\u9fa5]*)?",
    # r"(?:$|(?![\w?!+&\/\)]))",
    # @jfilter: I removed the line above from the regex because I don't understand what it is used for, maybe it was useful?
    # But I made sure that it does not include ), ] and } in the URL.
    flags=re.UNICODE | re.IGNORECASE,
)

WEIBO_URL_REGEX = re.compile(r"(?:(?:https?:?\/\/|ftp:\/\/|www\d{0,3}\.)t\.cn?(\/[a-zA-Z0-9]{0,8})?)")


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


def is_chinese_char(cp):
    """Checks whether CP is the codepoint of a CJK character."""
    # This defines a "chinese character" as anything in the CJK Unicode block:
    #   https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)
    #
    # Note that the CJK Unicode block is NOT all Japanese and Korean characters,
    # despite its name. The modern Korean Hangul alphabet is a different block,
    # as is Japanese Hiragana and Katakana. Those alphabets are used to write
    # space-separated words, so they are not treated specially and handled
    # like the all of the other languages.
    if (
            (cp >= 0x4E00 and cp <= 0x9FFF)
            or (cp >= 0x3400 and cp <= 0x4DBF)  #
            or (cp >= 0x20000 and cp <= 0x2A6DF)  #
            or (cp >= 0x2A700 and cp <= 0x2B73F)  #
            or (cp >= 0x2B740 and cp <= 0x2B81F)  #
            or (cp >= 0x2B820 and cp <= 0x2CEAF)  #
            or (cp >= 0xF900 and cp <= 0xFAFF)
            or (cp >= 0x2F800 and cp <= 0x2FA1F)  #
    ):  #
        return True

    return False


def contains_Chinese(seq):
    for char in seq:
        cp = ord(char)
        if is_chinese_char(cp):
            return True
    return False


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
    print("Testing the RegEx")

    test_text = '< ( ̄ ˇ ̄ ) > < ( ## ) > < 97 | | 97 > < 176 > < u > < ( ° ー ° 〃 ) > < 5 > < / h1 > < 23 > < t > < img src = " < url > < a tnk " href = " < url > < ) ( 〃 > < ) ~ ★ ~ ☆ ~ ★ ~ ☆ ~ ★ gakkiiloveyou ! ~ ★ ~ ☆ ~ ★ ~ ☆ ~ ★ ~ ( > < ( > < html > < ( ̄ 3 ̄ ) > < / p > < img pic _ type = " 1 " src = " < url > < --- > < 2015.11 . 03 > < ( / ▽ \\ = ) > < i , robot > < s > < 16 > < ) < url > < h1 > < ๑ ) ( ๑ > < / s > < 22 > < 007 > < イ グ ジ ス ト > < 144xxx > < img src = < url > < girlsaward 2016 a / w > < 3.0 > < ? b > < ( ̄ ) ̄ ) > < < awaydays > < healer > < cxs > < mama > < ___ ● > < before > < email > < %% > < 9 > < ( = ̄ _ ̄ | | | ) > < dune > < p > < 18 > < 0f $ > < 12 > < 2015.11 . 05 > < < う わ き な シ ン プ ル ス マ イ ル > < women > < ~ ~ ~ > < colors > < / iframe > < ( ̄ ▽ ̄ ) > < * ) ) > < desperado > < title > < phone > < / br > < cosplay > < ( ^ - ^ ) > < ○ > < ) ~ ~ ~ ~ ~ ~ ( > < ( * φ ω φ * ) > < < shark > < 20 > < ) ( > < ( ` ▽ ′ ) > < ( ï ¿ £ 3 ï ¿ £ ) > < 4 > < 13 > < wow > < piece > < mbmd > < champions > < ( · ω · ` ) > < ~ < < 117274117 > < = = > < 2012.1 . 09.02 : 21 > < 1 > < 7 > < doctors > < 49 > < < > < always there > < ( - ^ - ) > < ( " " " o " " " > < 50 > < someday > < 53 > < 8 > < br / > < fairy tale > < ● > < if > < / html > < = 1 ) , rnd ( 0 , a * b ) ( a * b > < ) } } { { ( > < < doctors > < 3 > < chapter.05 > < ) ~ ( > < 。 < url > < m q > < ‖ ‖ < url > < ~ > < / sup > < * * > < < phone > < 14 > < ` \' - , _ ) \' ._ ) , ___ .- ; \' ` " -. ` \\ _..._ / ` . ` , \\ / .- \' \' , / ( ) ( ) \\ ` \' ._ \\ / ( ) . ( | > < gosick > < \' ) ) ) > < 。 > < < br > < ( - ︿ - ) > < anaesthesia > < / u > < ) — — ( > < ( = ~ = ) > < < semini > < ) o ~ ~ o ( > < ) ~ ~ ( > < 52l > < | ; , __. ; \' -. \' -. | , \\ , \\ ` > < bleach > < ( 。 _ 。 ) > < < < > < ( __ __ ) > < br > < \' . < ` \' - , _ ) \' ._ ) , ___ .- ; \' ` " -. ` \\ _..._ / ` . ` , \\ / .- \' \' , / ( ) ( ) \\ ` \' ._ \\ / ( ) . ( | > < 。 = ) > < < url > < a href = " < url > < 2015.11 . 02 > < 19 > < 2 > < 17 > < 12 / 2 > < = 0.5 ) , 0.5 ( a > < 2012.1 . 09.01 : 46 > < / title > < ๑ ) < url > < % % > < ( _ _ ) > < op > < / a > < ( / \\ ) _ ( ) _ ( _ > < ) ☆ < url > < ) < ) ( 〃 > < < 1030 > < b > < gb12142 - 2007 > < 〜 > < 2015.11 . 04 > < \\ x \\ / > < v5.0 . 201401 > < 。 ) ( > < ( ̄ ︶ ̄ ) > < ( __ ) > < falling slowly > < 21 > < / span > < ) o ゜ < url > < ~ ~ > < … … … > < い ら な い > < circus > < sup > < < monster > < _ > < w . k . > < / body > < 11 > < url > < 3 < > < < < < < < < < < æ ° ´ æ ° ´ æ ° ´ > < t2 b . t1 > < 6 > < / b > < \\ x / > < bandage > < > < img >'

    pat2 = re.compile(u"<[^\\u4e00-\\u9fa5]*?>")
    print(pat2.sub("XXX", test_text))
    # '去成为你想成为的人，@花篇篇 皮肤管理培训什么时候都可以开始；去做你想做的事，任何方向都值得努力。祛斑吝惜汗水和能量，哪一条路都是弯路>；朝着目标努力前进，整个世界都会为你让路。未来和梦想，不是想出来的，是拼出来的。'
    # expected: 郭麒麟打卡,且听他分享防疫小知识XXX哈哈XXX哈哈哈哈XXX
