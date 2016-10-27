# encoding: utf-8

import pickle
sentence = ["我", "好", "喜欢", "这个", "电影啊", "讨厌"]

posDic = open("../../GradDesignDocs/hownet/正面情感词语（中文）.txt").read().decode('gbk').encode('utf-8')
negDic = open("../../GradDesignDocs/hownet/负面情感词语（中文）.txt").read().decode('gbk').encode('utf-8')
posEvaDic = open("../../GradDesignDocs/hownet/正面评价词语（中文）.txt").read().decode('gbk').encode('utf-8')
negEvaDic = open("../../GradDesignDocs/hownet/负面评价词语（中文）.txt").read().decode('gbk').encode('utf-8')
degreeDic = open("../../GradDesignDocs/hownet/程度级别词语（中文）.txt").read().decode('gbk').encode('utf-8')

print type(posDic), type(sentence)

for word in sentence:
    if word in (posDic or posEvaDic):
        print "pos"
    elif word in (negDic or negEvaDic):
        print "neg"
    else:
        print "opo"
