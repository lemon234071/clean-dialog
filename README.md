本项目为一个清洗对话数据的多线程框架，目前还比较简陋，欢迎提bug和优化，比如句内重复短语降重函数的正则或者后缀算法。代码还在继续完善中，注释以及一些函数出处引用等待完善。

# 目录结构

    --clean: 清洗框架主目录  
      ---rules: 存放各级别的规则函数   
      ---tool_data: 存放黑名单词典，每行一个词  
      ---run_dist.py: 主运行文件，构造dataloader, 加载黑名单  
      ---single_filter.py: run_dist.py所调用的单个线程的主程序，加载处理单个数据，并保存过滤后的数据以及脏数据  
      ---run.sh: 使用我挑选的几个规则来运行run_dist.py   
      
# 运行

    bash run.sh

# Rules
规则包括目前大部分论文内的清洗规则：  

1 黑名单过滤，包括特殊字符和脏话  
2 emoji表情  
3 邮箱、电话号等隐私过滤, 人名 替换为NAME1、NAME2。。。  
4 URL过滤  
5 unicode 相关修复   
6 去重：包括重复词缩减、过滤掉上下文相同的句子、重复的对话   
7 、meena以及dialogpt中使用的广告、通用回复筛除   

以上识别出来的噪音，如可在句中抹去则抹去。  
如不可抹去则放弃该句子：即，若是单轮对话放弃该对话，若是多轮对话则以该句为分割，切分对话。  

NOTE THAT: 
1, 改动某规则的时候注意是否影响到其他规则
2, 黑名单如人名、特殊话题等可根据需要配置放置到 ./tool_data/下，文件命名可自行配置请参阅。/run_dist.py中dataloader。黑名单可到github上搜寻，如 https://github.com/fighting41love/funNLP 

# Auguments

        --n_p"  #  多线程使用的线程数
        --batch_size"  # 单个处理文件的session数
        --tool_dir  # 黑名单文件所在目录
        --out_dir  # 过滤后文件输出的目录
        --raw_dir  # 待处理文件所在的目录
        
        # 清洗规则
        # 基于原始字符串
        --split_multi_repost  # "一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？" 按 "//"分割为多句
        --utterance_dedup  # 如果 context == response 则去掉该对话
        --no_name  # 对话中的人名用 <NAME1>, <NAME2> ...代替
        --split_multi_repost  # 将如下单句子拆成多个回复，与context一起构成多个对话："一起来吗？@Cindy //@Bob: 算我一个//@Amy:今晚开派对吗？"
        --de_ad  # 去除可能是广告的对话（同样的回复对应多个context， 借鉴 https://www.aclweb.org/anthology/D13-1096.pdf）
        --de_generic_dialog  # 去除通用回复，借鉴 https://arxiv.org/abs/1911.00536
        --no_reply_tag  # 去除 "回复 @Devid: 我会准时到的" 中的 "回复 @Devid:"
        --no_hashtag  # 去除 "# 感恩节# 感谢给予自己生命，养育我们长大的父母" 中的 "# 感恩节#"
        --no_emotion # 去除 ": xxx: 感谢给予自己生命" 中的 ": xxx:"
        --no_mention  # 去除 "一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？" 中的 "@Cindy"， "@Bob:"， "@Amy:"
        --no_repost  # 去除"一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？" 中的 "//@Bob: 算我一个//@Amy: 今晚开派对吗？"
        --no_brackets  # 去除中括号中的内容: "[XXX] 今晚月色真美"
        --no_duplicated  # 降重 "老师，您好您好您好您好您好您好" 为 "老师， 您好您好您好"
        --no_emoji  # 去除emoji表情
        --no_short  # 去除过短的句子
        --no_long   # 去除过长的句子
        --no_special_topic  # 去除带有 特殊话题的句子，如医疗名词、金融名词
        --bert_clean  # 使用 BertTokenizer中文中的清理函数清理句子
        --use_cleantext_lib  # 使用clean-text库来去除掉句子中的电话号、邮箱、unicode错误等
        --no_str_blacklist   # 过滤掉句子中含有该黑名单中词的句子
    
        # 基于分词后的 word list
        --no_word_blacklist  # 过滤掉 分词后的句子中含有的词在 该黑名单中的句子
        --no_alpha_noise  # 过滤掉含有不成 英文单词的 字母组合 的句子
        --check_confuse_word  # 给定一个黑名单，看看包含这些词的句子是否是噪音
        --yda_dedupl   # 使用我设计的一个函数过滤该句子: 如果一个词语在句子中出现的比例 超过一个阈值则放弃该句子