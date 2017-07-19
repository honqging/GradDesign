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

from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import random

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

# def getUserDistance(u1, u2):

def getIniCentroid(k, maximum):
    iniCentroid = []
    for i in range(k):
        index = random.randint(0, maximum-1)
        if index not in iniCentroid:
            iniCentroid.append(user2Score[index])
    return iniCentroid

# if centroid stopped
def isEnded(cent1, cent2):
    totDist = 0
    for i in range(len(cent1)):
        # print len(cent1[i]), cent1[i][1]
        # print len(cent2[i]), cent2[i]
        dista, path = fastdtw(cent1[i], cent2[i], dist=euclidean)
        totDist += dista
    # if totDist < 1:
    #     return True
    # return False
    return totDist

def getInnerDist(data, centroid, label, k):
    inner = np.zeros(k)
    # indexList[0]: all indice in label whose type is 0
    # indexList[0]: [1, 3, 4, 5, 88, 89, 102...]
    indexList = []
    for index in range(k):
        indexList.append([i for i, v in enumerate(label) if v==index])
    for i in range(k):
        print 'len:', len(indexList[i])
        if len(indexList[i]) == 0:
            return 0
    for i in range(k):
        # iLen: the number of users whose type is i
        iLen = len(indexList[i])
        for m in indexList[i]:
            # temp method to calculate innerDist
            dista, path = fastdtw(data[m], centroid[i], dist=euclidean)
            inner[i] += dista

            # true method to calculate innerDist
            # for n in range(m, iLen):
            #     dista, path = fastdtw(data[m], data[n], dist=euclidean)
            #     print 'dista: ', dista, m, n
            #     inner[i] += dista
        print 'inner[i]: ', inner[i], iLen, i
        inner[i] = inner[i]/(iLen*(iLen-1)/2)
    return sum(inner)/k

def getOutDist(centroids, k):
    outDist = 0
    for m in range(k):
        for n in range(m, k):
            dista, path = fastdtw(centroids[m], centroids[n], dist=euclidean)
            outDist += dista
    return outDist/(k*(k-1)/2)

def kmeans(k, data, dataLength):
    ended = False
    centroid = getIniCentroid(k, dataLength)
    label = np.zeros(dataLength)

    # the min dist list of every data to its centroid
    assessment = np.zeros(dataLength)
    while not ended:
        oldCentroid = np.copy(centroid)
        # centroid = []
        for i in range(dataLength):
            minDist = np.inf
            minIndex = -1
            for j in range(k):
                # get dtw distance
                # print 'len(centroid[j]), centroid[1]',len(data[i]), len(centroid[j]), data[i][1], centroid[j][1]
                dista, path = fastdtw(data[i], centroid[j], dist=euclidean)
                if dista < minDist:
                    minDist, minIndex = dista, j
                    label[i] = j
            assessment[i] = minDist
        # update centroid
        for j in range(k):
            cen = []
            for n in range(len(data[0])):
                y = np.zeros(7)
                for m in range(dataLength):
                    # users whose type is j
                    if label[m] == j:
                        x = data[m][n]
                        y = [a+b for a, b in zip(x, y)]
                cen.append(y)
            centroid[j] = cen
        # print 'before ended: ', len(oldCentroid)
        # ended = isEnded(oldCentroid, centroid)
        ended = True
        print '2 centroid distance:', isEnded(oldCentroid, centroid)
    return centroid, label, assessment

if __name__ == '__main__':
    # eg: 2341.10009766 0 3 0 这里一个bug，左边是墙哪里来的风？ 0
    scoreList = getScoreListFromVCid3(xmlDL.vCid)
    scoreList.sort()

    interval = 30
    sentiType = 7
    # total barrage number in every 'interval' seconds
    totalLen = int(scoreList[-1][0]/interval) + 1
    print 'totalLen', totalLen

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




    print 'start new coding for essay.....'
    # calculate single user number
    userList = []
    for score in scoreList:
        # print score
        userList.append(score[1])
    singleUserList = list(set(userList))
    singleUserNum = len(singleUserList)

    print 'singleUserNum', singleUserNum

    # [0, 0, 0, 0, 0, 0, 0]
    # singleScore = np.zeros(sentiType)
    # [[7 zeros], [7 zeros], ......] totalLen
    # barrageScore = []
    # for i in range(totalLen):
    #     barrageScore.append(np.zeros(sentiType))

    # 3 dimensions
    user2Score = []
    for i in range(singleUserNum):
        barrageScore = []
        for i in range(totalLen):
            barrageScore.append(np.zeros(sentiType))
        user2Score.append(barrageScore)

    for i in range(singleUserNum):
        scoresOfUserI = [j for j, v in enumerate(userList) if v==singleUserList[i]]
        # print scoresOfUserI
        for k in scoresOfUserI:
            intScore0 = int(scoreList[k][0]/interval)
            user2Score[i][intScore0] += scoreList[k][2:9]
            # print intScore0, user2Score[i][intScore0], scoreList[k][2:9]

    # print user2Score[0]
    # print user2Score[1]

    # distance2d = np.zeros((singleUserNum, singleUserNum))
    # for i in range(singleUserNum):
    #     for j in range(singleUserNum):
    #         distance, path = fastdtw(user2Score[0], user2Score[1], dist=euclidean)
    #         # print 'distance', distance
    #         distance2d[i][j] = distance
    # print distance2d

    start = time.time()
    k = 7

   

    while 1:
        print 'k=', k
        centroid, label, assessment = kmeans(k, user2Score, singleUserNum)

        indexList = []
        for index in range(k):
            indexList.append([i for i, v in enumerate(label) if v==index])
        for i in range(k):
            print 'len:', len(indexList[i])
            if len(indexList[i]) == 0:
                print 'some indeList is 0'
                continue
                
        # for i in label:
        #     print i,
        print 'label'
        for i in range(len(label)):
            if label[i] == 1:
                print 'user:', singleUserList[i]
                for score in scoreList:
                    if score[1] == singleUserList[i]:
                        for ss in score:
                            print ss,
                        print
        print 'the end'
        break
 
        # innerDist = getInnerDist(user2Score, centroid, label, k)
        # if innerDist != 0:
        #     outDist = getOutDist(centroid, k)
        #     wbIndex = k*innerDist/outDist
        #     print innerDist, outDist, wbIndex
        #     break


# k=5
# inner[i]:  499989.478243 1734 0
# inner[i]:  1284.58891513 14 1
# inner[i]:  43681.5149157 104 2
# inner[i]:  226991.013474 387 3
# inner[i]:  219409.732297 389 4
# 5.71024397709 493.952458779 0.0578015543358

# k=6
# inner[i]:  512338.066138 590 0
# inner[i]:  266042.881674 391 1
# inner[i]:  11663.1561665 83 2
# inner[i]:  100.069203591 5 3
# inner[i]:  1677.38062154 20 4
# inner[i]:  199318.807214 1539 5
# 4.81148509628 500.567337481 0.0576723817477

# k=7
# inner[i]:  12070.8018562 68 0
# inner[i]:  435.932981677 607 1
# inner[i]:  13851.8767829 74 2
# inner[i]:  233201.911924 382 3
# inner[i]:  8422.62434799 69 4
# inner[i]:  309407.791364 1010 5
# inner[i]:  285991.076502 418 6
# 5.92873811218 417.802960897 0.0993319116172


    end = time.time()
    print 'cost time:', end - start






    # for score in scoreList:
    #
    #     if score[1] in singleUserList:
