# encoding: utf-8

import pickle
import jieba
import xlrd
import time
import jieba.posseg as pseg
import sys

sentence1 = ["我", "好", "喜欢", "这个", "电影啊", "讨厌"]
sentence2 = "我非常喜欢这个电影啊, 但是我讨厌主角"
sentence3 = "你名---------新海诚-----------秒五------------言叶走起"
sentence4 = "椿去湫来，海棠花开"

posDic = open("../../GradDesignDoc/sentimentDictionary/hownet/正面情感词语（中文）.txt").read().decode('gbk').encode('utf-8')
negDic = open("../../GradDesignDoc/sentimentDictionary/hownet/负面情感词语（中文）.txt").read().decode('gbk').encode('utf-8')
posEvaDic = open("../../GradDesignDoc/sentimentDictionary/hownet/正面评价词语（中文）.txt").read().decode('gbk').encode('utf-8')
negEvaDic = open("../../GradDesignDoc/sentimentDictionary/hownet/负面评价词语（中文）.txt").read().decode('gbk').encode('utf-8')
degreeDic = open("../../GradDesignDoc/sentimentDictionary/hownet/程度级别词语（中文）.txt").read().decode('gbk').encode('utf-8')

data = xlrd.open_workbook("../../GradDesignDoc/sentimentDictionary/情感词汇本体/情感词汇本体.xlsx")
table = data.sheet_by_index(0)
nrows = table.nrows
col_list = table.col_values(0)

# print col_list, type(col_list)
# sys.exit()

# print type(sentence)
# return sentiment type of a word
def getWordType(wordd):
    if type(wordd) == str:
        # print wordd, type(wordd)
        wordd = unicode(wordd, 'utf-8')
    if wordd in col_list:
        num = col_list.index(wordd)
        cSenti = table.cell(num, 4).value.encode('utf-8')
        if cSenti == 'PA' or cSenti == 'PE':
            return 1
        elif cSenti == 'PD' or cSenti == 'PH' or cSenti == 'PG' or cSenti == 'PB' or cSenti == 'PK':
            # print cSenti, wordd
            return 2
        elif cSenti == 'NA':
            return 3
        elif cSenti == 'NB' or cSenti == 'NJ' or cSenti == 'NH' or cSenti == 'PF':
            return 4
        elif cSenti == 'NI' or cSenti == 'NC' or cSenti == 'NG':
            return 5
        elif cSenti == 'NE' or cSenti == 'ND' or cSenti == 'NN' or cSenti == 'NK' or cSenti == 'NL':
            return 6
        elif cSenti == 'PC':
            return 7
        else:
            return 0
    else:
        return 0

def getSentiType(wList):
    sentiTList = [0, 0, 0, 0, 0, 0, 0]
    for word in wList:
        wordScore = getWordType(word)
        if wordScore == 0:
            continue
        # not calculating very, not, no, much.....
        sentiTList[wordScore-1] += 1
    return sentiTList


def getScore(wList):
    posScore = 0
    negScore = 0
    swp = 0  # last sentiment word position
    wp = 0  # current word position

    # get the sentiment score of each sentence
    for word in wList:
        # word in danmuBili.py is coded in unicode.
        if type(word) is not str:
            word = word.encode("utf-8")

        # start = time.time()
        # wtype = getSentiType(word)
        # end = time.time()
        # print "time:", end - start

        if ' ' in word:
            continue
        elif word in posDic:
            wPosScore = 1  # positive score of a word
            # uWord = unicode(word, 'utf-8')
            # wp = wList.index(uWord)
            # for word2 in wList[swp:wp]:
            #     word2 = word2.encode("utf-8")
            #     if word2 in degreeDic:
            #         # print "degree: ", word2
            #         wPosScore *= 2
            # swp = wList.index(uWord)
            posScore += wPosScore
        elif word in negDic:
            wNegScore = 1
            # uWord = unicode(word, 'utf-8')
            # wp = wList.index(uWord)
            # for word2 in wList[swp:wp]:
            #     word2 = word2.encode("utf-8")
            #     if word2 in degreeDic:
            #         wNegScore *= 2
            # swp = wList.index(uWord)
            # # print wp, swp, word
            negScore -= wNegScore
        # elif wtype == 1 or wtype == 2 or wtype == 7:
        #     wPosScore = 1  # positive score of a word
        #     # uWord = unicode(word, 'utf-8')
        #     # wp = wList.index(uWord)
        #     # for word2 in wList[swp:wp]:
        #     #     word2 = word2.encode("utf-8")
        #     #     if word2 in degreeDic:
        #     #         # print "degree: ", word2
        #     #         wPosScore *= 2
        #     # swp = wList.index(uWord)
        #     posScore += wPosScore
        # elif wtype == 3 or wtype == 4 or wtype == 5 or wtype == 6:
        #     wNegScore = 1
        #     # uWord = unicode(word, 'utf-8')
        #     # wp = wList.index(uWord)
        #     # for word2 in wList[swp:wp]:
        #     #     word2 = word2.encode("utf-8")
        #     #     if word2 in degreeDic:
        #     #         wNegScore *= 2
        #     # swp = wList.index(uWord)
        #     # # print wp, swp, word
        #     negScore -= wNegScore
        else:
            continue
    if (posScore or negScore) > 100:
        print ">>>>>>>>100", posScore, negScore
        posScore = 0
        negScore = 0
    return posScore, negScore

def getScore2(sentence):
    wordList = jieba.lcut(sentence, cut_all=False)
    for i in wordList:
        print i
    return getScore(wordList)

# return two lists: wordTypeList & wordList
def getScore7(sentence):
    wordList = jieba.lcut(sentence, cut_all=False)
    return getSentiType(wordList)

def printScoreAndWord(result):
    wordTypeList, wordList = result
    for i in range(len(wordList)):
        print wordTypeList[i], wordList[i]
# print getScoreBySen(sentence3)

if __name__ == "__main__":
    t1 = time.time()
    for i in range(1):
        # print getWordType("讨厌")
        print getScore7(sentence2)
        # print getScore2(sentence4)
    t2 = time.time()
    print 'Spent time: ', t2 - t1


    oneBarrageList = pseg.cut(sentence2)
    for word, flag in oneBarrageList:
        if(flag == 'n' or flag == 'a'):
            print word, type(word)

    # printScoreAndWord(getScoreBySen(sentence4))
