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

# def numberDistribution(scoreList):
#     continue


tree = ET.parse("3876153ddd.xml")
print type(tree)
root = tree.getroot()

# for child in root:
#     print child.tag

scoreList = []
newScore = []
newScoree = []
newScoreX = []
newScoreY = []

for elem in tree.iter(tag = "d"):
    pDataList = elem.attrib['p'].split(',')
    if len(pDataList) != 10:
        continue
    if int(pDataList[8]):
        print pDataList[8]
        barrageDate = time.localtime(float(pDataList[4]))
        barrageDate2 = time.strftime("%Y-%m-%d %H:%M:%S", barrageDate)
        # print type(pDataList[8])

        # list
        if type(elem.text) == str:
            # print elem.text
            continue
        elif type(elem.text) == unicode:
            word_list = jieba.lcut(elem.text, cut_all=False)
            # for word in word_list:
            #     print word,
            # print "word_list", type(word_list)
            a = sentimentAnalysis.getScore(word_list)
            # if int(pDataList[4]) < 1482754065:
            #     if int(pDataList[8]) == 1:

            # eg: a = 2282.95996094 0 2 0 666真爱 0

            a = (float(pDataList[0]), 0) + a + (elem.text, 0)
            scoreList.append(a)
            # b = (float(pDataList[0]), 0) + a + (elem.text, 0)
            # scoreList2.append(b)
            # print len(word_list), elem.text, type(word_list)
        else:
            # print elem.text
            continue


scoreList.sort()

for i in scoreList:
    for j in i:
        print j,
    print

summ = 0
for s in scoreList:
    if s[2] + s[3] > 0:
        # print s
        summ += 1
print summ, " positive barrages.."


interval = 20
# total barrage number in every 'interval' seconds
totalLen = int(scoreList[-1][0]/interval) + 1
print totalLen
aveBarrageNum = np.linspace(0, 0, totalLen)
totalBarragePosScore = np.zeros(totalLen)
totalBarrageNegScore = np.zeros(totalLen)
aveBarragePosScore = np.zeros(totalLen)
aveBarrageNegScore = np.zeros(totalLen)

totalBarragePosScoree = np.zeros(totalLen)
aveBarragePosScoree = np.zeros(totalLen)
posScoreNumm = np.zeros(totalLen)

# positive and negative barrage number in every 'interval' seconds
posScoreNum = np.zeros(totalLen)
negScoreNum = np.zeros(totalLen)

# total positive and negative score in 10s
for score in scoreList:
    # print score[0], score[4] # output time & text
    # total barrage number in every 10s
    intScore0 = int(score[0]/interval)
    aveBarrageNum[intScore0] += 1

    value = score[2] + score[3]
    newScoree.append([score[0], value])
    totalBarragePosScoree[intScore0] += value
    posScoreNumm[intScore0] += 1

    if value > 0:
        newScore.append([score[0], score[2]])
        totalBarragePosScore[intScore0] += score[2]
        posScoreNum[intScore0] += 1
        if totalBarragePosScore[intScore0] > 60000:
            print score[0]
    elif value == 0:
        newScore.append([score[0], 0])
    else:
        newScore.append([score[0], score[3]])
        totalBarrageNegScore[intScore0] += score[3]
        negScoreNum[intScore0] += 1
    # print totalBarragePosScore[50]

    # if int(score[0]/interval) == 189:
    #     print score[4], sentimentAnalysis.getScoreBySent(score[4])
print "-----字幕解析完毕-----"

for index in range(len(negScoreNum)):
    if negScoreNum[index] == 0:
        aveBarrageNegScore[index] = 0
    else:
        aveBarrageNegScore[index] = totalBarrageNegScore[index]/negScoreNum[index]

for index in range(len(posScoreNum)):
    if posScoreNum[index] == 0:
        aveBarragePosScore[index] = 0
    else:
        aveBarragePosScore[index] = totalBarragePosScore[index]/posScoreNum[index]

    if aveBarragePosScore[index] > 300:
        print totalBarragePosScore[index], posScoreNum[index]

for index in range(len(posScoreNumm)):
    if posScoreNumm[index] == 0:
        aveBarragePosScoree[index] = 0
    else:
        aveBarragePosScoree[index] = totalBarragePosScoree[index]/posScoreNumm[index]


for score in newScore:
    newScoreX.append(score[0])
    newScoreY.append(score[1])
    # if math.fabs(score[1])>5:
    #     print score

# plt.figure(1)
# print "newScoreX", newScoreX
# print "newScoreY", newScoreY
# print "aveBarragePosScore", aveBarragePosScore
# print "aveBarrageNegScore", aveBarrageNegScore
# plt.plot(newScoreX, newScoreY)

plt.figure(2)
plt.title("Time-Barrage Number")
plt.xlabel("Barrage Time(30s)")
plt.ylabel("Barrage Number")

# plot the first curve
plt.plot(aveBarrageNum)
print '------------------print aveBarrageNum', aveBarrageNum

# plot the second(matching) curve
func1 = util.matchedCurve(aveBarrageNum)
xAxis1 = np.arange(0, aveBarrageNum.size, 1)
plt.plot(xAxis1, func1(xAxis1), 'r')

# sys.exit()

plt.figure(3)
plt.title("Time-Positive/Negtive Sentiment")

plt.subplot(311)
plt.xlabel("Barrage Time(30s)")
plt.ylabel("Positive Sentiment")
plt.plot(aveBarragePosScore)
func311 = util.matchedCurve(aveBarragePosScore)
xAxis311 = np.arange(0, aveBarragePosScore.size, 1)
plt.plot(xAxis311, func311(xAxis311), 'r')

plt.subplot(312)
plt.xlabel("Barrage Time(30s)")
plt.ylabel("Negtive Sentiment")
plt.plot(aveBarrageNegScore)
func312 = util.matchedCurve(aveBarrageNegScore)
xAxis312 = np.arange(0, aveBarrageNegScore.size, 1)
plt.plot(xAxis312, func312(xAxis312), 'r')

plt.subplot(313)
plt.xlabel("Barrage Time(30s)")
plt.ylabel("Integrated Sentiment")
plt.plot(aveBarragePosScoree)
func313 = util.matchedCurve(aveBarragePosScoree)
xAxis313 = np.arange(0, aveBarragePosScoree.size, 1)
plt.plot(xAxis313, func313(xAxis313), 'r')

# plt.figure(4)
# plt.plot(aveBarrageNegScore2)
plt.show()
