# encoding: utf-8

import jieba

text = ["他来到了网易杭研大厦",
"小明硕士毕业于中国科学院计算所",
"后在日本京都大学深造"]

lists = []
l2 = []
for single in text:
    seg_list = jieba.lcut(single, cut_all=False)
    lists.append(seg_list)

    # list.append()
    print lists[0][0]
print lists[1][1]



print "-----字幕解析完毕-----"
