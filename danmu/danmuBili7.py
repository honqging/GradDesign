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
def getUserList(num, barrageList):
    userList = []
    bList = barrageList
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

# barrage num/per larger than 3
def getScoreListFromVCid(vCid):
    scoreList2 = []

    # userList whose barrage is larger than 3
    userList = getUserList(3)
    bList = xmlDL.migrateBD(vCid)
    for b in bList:
        if b[6] in userList:
            word_list = jieba.lcut(b[8], cut_all=False)
            a = sentimentAnalysis.getScore(word_list)
            a = (float(b[0]), b[6]) + a + (b[8], 0)
            scoreList2.append(a)
        else:
            continue
    return scoreList2
# scoreList2 = getScoreListFromVCid(xmlDL.vCid)

# barrage num/per no limit
def getScoreListFromVCid3(vCid):
    scoreList3 = []

    # userList whose barrage is larger than 3
    bList = xmlDL.migrateBD(vCid)
    userList = getUserList(3, bList)
    for b in bList:
        word_list = jieba.lcut(b[8], cut_all=False)
        a = sentimentAnalysis.getSentiType(word_list)
        a = (float(b[0]), b[6]) + tuple(a) + (b[8], 0)
        scoreList3.append(a)
    return scoreList3
# scoreList3 = getScoreListFromVCid3(xmlDL.vCid)

if __name__ == '__main__':
    # eg: 2341.10009766 0 3 0 这里一个bug，左边是墙哪里来的风？ 0
    scoreList = getScoreListFromVCid3(xmlDL.vCid)
    scoreList.sort()

    interval = 30
    sentiType = 7
    # total barrage number in every 'interval' seconds
    totalLen = int(scoreList[-1][0]/interval) + 1
    print totalLen

    aveBarrageNum = np.linspace(0, 0, totalLen)

    totalBarrageScore7 = []
    aveBarrageScore7 = []
    scoreNum7 = []

    for i in range(sentiType):
        totalBarrageScore = np.zeros(totalLen)
        scoreNum = np.zeros(totalLen)
        aveBarrageScore = np.zeros(totalLen)

        totalBarrageScore7.append(totalBarrageScore)
        aveBarrageScore7.append(scoreNum)
        scoreNum7.append(aveBarrageScore)

    # total positive and negative score in 10s
    # eg: score: 0.0 a74ad57b 0 0 0 0 0 0 0 哈哈哈哈 0
    for score in scoreList:
        # print score[0], score[4] # output time & text
        # total barrage number in every 10s
        intScore0 = int(score[0]/interval)
        aveBarrageNum[intScore0] += 1

        # eg: 0 0 0 0 0 0 0
        score7 = list(score[2:8])
        if score7[-2] > 0:
            print score[-2]
        for i in range(len(score7)):
            if score7[i] > 1:
                totalBarrageScore7[i][intScore0] += score7[i]
                scoreNum7[i][intScore0] += 1
            # if totalBarrageScore[i][intScore0] > 60000:
            #     print "more than 6000", score[0]
    for i in totalBarrageScore7:
        print i
    for i in scoreNum7:
        print 'scoreNum7:', i

    print "-----字幕解析完毕-----"
    print len(scoreNum7), len(scoreNum7[0])
    for index in range(len(scoreNum7[0])):
        for i2 in range(len(scoreNum7)):
            if scoreNum7[i2][index] == 0:
                aveBarrageScore7[i2][index] = 0
            else:
                aveBarrageScore7[i2][index] = totalBarrageScore7[i2][index]/scoreNum7[i2][index]
                # print 'i2 index', i2, index, aveBarrageScore7[i2][index]

    plt.figure(2)
    # plt.title(u"时间－弹幕数量分布")
    plt.xlabel(u"弹幕出现时间(" + str(interval) + "s)")
    plt.ylabel(u"7维情感值")

    # plot the first curve
    plt.plot(aveBarrageNum)
    print '------------------print aveBarrageNum', aveBarrageNum

    # plot the second(matching) curve
    func1 = util.matchedCurve(aveBarrageNum)
    xAxis1 = np.arange(0, aveBarrageNum.size, 1)
    plt.plot(xAxis1, func1(xAxis1), 'r')


    plt.figure(3)
    plt.title("Time-Positive/Negtive Sentiment")

    for i in range(len(scoreNum7)):
        # 711
        # print i, aveBarrageScore7[i]
        subIndex = int(str(len(scoreNum7))+str(1)+str(i+1))
        plt.subplot(subIndex)
        plt.xlabel(u"弹幕出现时间(" + str(interval) + "s)")
        ee = "第" + str(i+1) + "种情感"
        ee = unicode(ee, 'utf-8')
        plt.ylabel(ee)
        # plt.bar(range(len(aveBarrageNum)), aveBarrageScore7[i])
        plt.plot(aveBarrageScore7[i], 'c')
        func311 = util.matchedCurve(aveBarrageScore7[i])
        xAxis311 = np.arange(0, aveBarrageScore7[i].size, 1)
        plt.plot(xAxis311, func311(xAxis311), 'r')

    plt.show()
