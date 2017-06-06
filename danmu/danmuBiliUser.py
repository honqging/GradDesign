# encoding: utf-8

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.cElementTree as ET
import time
import jieba
import math
import numpy as np
import matplotlib.pyplot as plt
import sys

import sentimentAnalysis
import util
import xmlDL
import lda

# def numberDistribution(scoreList):
#     continue

# get users whose barrage less than num(eg: 3)
def getUserList(num):
    userList = []
    bList = xmlDL.migrateBD(xmlDL.vCid)
    uniBContentList, uniBContentList2, uniBContentListString, bNumPerUser = lda.getUserAndBarrageList(bList)
    for i in range(len(bNumPerUser)):
        # if bNumPerUser[i][1] == 1:
        #     numOfUsersList[0] += 1
        # elif bNumPerUser[i][1] == 2:
        #     numOfUsersList[1] += 1
        # elif bNumPerUser[i][1] == 3:
        #     numOfUsersList[2] += 1
        if bNumPerUser[i][1] >= num:
            userList.append(bNumPerUser[i][0])
    return userList

# print getUserList(3)
# sys.exit()

# only calculate barrages num/per larger than 3
def getScoreListFromVCid(newUniBContentListString):
    scoreList2 = []

    # userList whose barrage is larger than 3
    bList = newUniBContentListString
    for b in bList:
        word_list = jieba.lcut(b[1], cut_all=False)
        a = sentimentAnalysis.getScore(word_list)
        a = (b[0], b[1]) + a
        scoreList2.append(a)
    return scoreList2

scoreList = []
posScoreList = []
negScoreList = []


if __name__ == '__main__':
    bList = xmlDL.migrateBD(xmlDL.vCid)

    # eg: uniBContentListString: ['22ccd704', '\xe7\x88\xb7\xe7\x88\xb7QAQ']
    uniBContentList, uniBContentList2, uniBContentListString, bNumPerUser = lda.getUserAndBarrageList(bList)
    print 'uni', len(uniBContentListString)
    newUniBContentListString = lda.removeBLessNum(uniBContentListString, bNumPerUser, 3)
    print 'new', len(newUniBContentListString)

    scoreList2 = getScoreListFromVCid(newUniBContentListString)
    # for i in scoreList2:
    #     for j in i:
    #         print j,
    #     print

    a = 0
    b = 0
    c = 0
    d = 0
    for score in scoreList2:
        # print type(score[2])
        if score[2]+score[3]<0:
            a += 1
            posScoreList.append(score[2])
            negScoreList.append(score[3])
            print score[2]+score[3], score[2], score[1]
        elif score[2]>3*abs(score[3]):
            b += 1
        elif score[2]>abs(score[3]) & score[2]<3*abs(score[3]):
            c += 1
        elif score[2]+score[3]==0:
            d += 1
    print a, b, c, d


    print "-----字幕解析完毕-----"

    plt.figure(2)
    # plt.subplot(211)
    # plt.title(u"时间－弹幕数量分布")
    plt.xlabel(u"用户id")
    plt.ylabel(u"积极情感值")
    plt.bar(range(len(posScoreList)), posScoreList, fc='c', ec='c')

    # data = [5, 20, 15, 25, 10]
    # plt.bar(range(len(data)), data, fc='g', ec='r')


    # plot the second(matching) curve
    # func1 = util.matchedCurve(aveBarrageNum)
    # xAxis1 = np.arange(0, aveBarrageNum.size, 1)
    # plt.plot(xAxis1, func1(xAxis1), 'r')

    # plt.subplot(212)
    # plt.xlabel(u"用户id")
    # plt.ylabel(u"消极情感值")
    plt.bar(range(len(negScoreList)), negScoreList, fc='m', ec='m')

    plt.show()
