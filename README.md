本项目为一个清洗对话数据的多线程框架，目前还比较简陋，欢迎提bug和优化，比如句内重复短语降重函数的正则或者后缀算法。代码还在继续完善中，注释以及一些函数出处引用等待完善。

# 目录结构
    
    --scripts: 存放运行脚本
      ---run.sh: 使用我挑选的几个规则来运行run_dist.py  
    --src: 清洗框架功能主目录  
      ---inputters: 存放dataloader 和 存取数据工具函数
      ---rules: 存放各级别的规则函数
      ---single_filter.py: run_dist.py所调用的单个线程的主程序，加载处理单个数据，并保存过滤后的数据以及脏   
    ---tool_data: 存放黑名单词典，每行一个词  
    ---run_dist.py: 主运行文件，加载dataloader，加载黑名单，简历线程池 
    ---utils: 数据统计，结果检测
      
# 运行并保存日志

    bash ./scripts/run.sh 2>&1 | tee -a cleaning.log

# Rules
规则包括目前大部分论文内的清洗规则：  

1 黑名单过滤，包括特殊字符和脏话  
2 emoji表情  
3 邮箱、电话号等隐私过滤, 人名 替换为NAME1、NAME2。。。  
4 URL过滤  
5 unicode 相关修复   
6 去重：包括重复词缩减、过滤掉上下文相同的句子、重复的对话   
7 meena以及dialogpt中使用的广告、通用回复筛除   

以上识别出来的噪音，如可在句中抹去则抹去。  
如不可抹去则放弃该句子：即，若是单轮对话放弃该对话，若是多轮对话则以该句为分割，切分对话。  

NOTE THAT: 
1, 改动某规则的时候注意是否影响到其他规则, 规则清洗顺序有要求
2, 黑名单如人名、特殊话题等可根据需要配置放置到 ./tool_data/下，文件命名可自行配置请参阅。/run_dist.py中dataloader。黑名单可到github上搜寻，如 https://github.com/fighting41love/funNLP 
3, 将在每个函数上方给定测试样例，下方给定期待样例
4, 目前run.sh中使用的参数为本人正在使用的功能

# Auguments
        
| 参数               | 描述                 |
| :---------------  | :------------------- |
| n_p               | 多进程数 |
| batch_size        | 单个进程最大处理session数 |
| tool_dir          | 工具数据所在目录（如黑名单）|
| out_dir           | 清洗后的文件输出目录 |
| raw_dir           | 待处理文件所在mull  |
| dirty_dir         | 存储清洗出来的脏数据，如为空则不存  |
| :---------------  | :------------------- |
| split_multi_repost| 将微博转发数据按"//@aaa XXXX //@bbb XXX"撕开成多句  |
| no_utter_dup   | 如果 context == response 则去掉该对话  |
| re_name           | 人名用 <NAME1>, <NAME2> ...替换 |
| no_ad             | 去除可能是广告的对话（同样的回复对应多个context）借鉴[论文](https://www.aclweb.org/anthology/D13-1096.pdf) |
| de_generic_dialog | 去通用回复 借鉴[论文](https://arxiv.org/abs/1911.00536)|
| no_short_response | 去掉对话尾部所有过短回复 |
| :---------------  | :------------------- |
| bert_clean        | 使用BertTokenizer 中函数清理句子 |
| cleantext_clean | 使用[clean-text]() 清理 （电话号、邮箱、unicode错误等） |
| :---------------  | :------------------- |
| no_short          | 去除过短的句子 |
| no_long           | 去除过长的句子 |
| de_reply_tag      | 去除微博中 "回复 @XXX:" |
| de_hashtag        | 去除句中 "# XXX#" |
| de_emotion        | 去除句中 ": XXX:" |
| de_mention        | 去除句子中 "@Cindy"， "@Bob:"， "@Amy:" 等|
| no_mention       | 去除包含 @XXX 的句子 |
| de_repost         | 去除句中 "//XXX" |
| de_duplicated     | 句中短语降重 （待用后缀算法优化） |
| no_emoji          | 去除emoji （代补全） |
| no_special_topic  | 过滤包含特定名单词的对话对话 |
| no_str_blacklist  | 过滤包含黑名单词的对话 |
| no_toupiao        | 判断是否是微博投票 |
| no_specific_utter | 删除一些特定句子 |
| contain_zh        | 删掉不包含中文的句子 |
| de_single_repost_mention| 去掉 "@XXX:" |
| de_weibo_url      | 去除 http:\\t.c |
| de_url            | 去除 url |
| de_angle          | 去除 <XXX> 其中XX为非中文 |
| de_alpha_num      | 去除长串无意义的数字字母组合 |
| de_specific       | 去除句中固定pattern    |
| :---------------  | :------------------- |
| de_showall        | 去除某些特定文件中的 "...显示全部" |
| de_brackets       | 去除某些特定文件中的 "\[XXX\]" |
| :---------------  | :------------------- |
| no_word_blacklist | 过滤分此后的黑名单词的对话 |
| no_alpha_noise    | 过滤掉含有不成 英文单词的 字母组合 的句子 |
| check_confuse_word| 保存包含混淆名单词的对话进行recall |
| yda_dedupl        | 如果一个词语在句子中出现的比例 超过一个阈值则放弃该句子 |