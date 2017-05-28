# encoding: utf-8

import numpy as np
import json as js
import requests
import time
import xmlDL
import jieba
import test
import matplotlib.pyplot as plt
import os

jieba.load_userdict('data/jiebaNewWord/jiebaNewWord.txt')

# print every element in a list 'l' in a line
def printList(l):
    for i in l:
        print i,
    print

# return a matched curve with the dimension 3
# input parameter type: np.ndarray
def matchedCurve(nda):
    xAxis = np.arange(0, nda.size, 1)
    coefficient = np.polyfit(xAxis, nda, 15) # coefficient： the coefficient of matched function
    func = np.poly1d(coefficient) # poly1d used to invoke function
    print xAxis, "coefficient:", coefficient, "func:", func
    return func

# count total number of barrageData
def getTotalNumber():
    bUrl = 'http://comment.bilibili.com/rolldate,3876153'
    s = requests.get(bUrl)
    # print s.text
    jsonDoc = js.loads(s.text)
    sum = 0

    # new a dir to store all barrage .xml data
    for i in jsonDoc:
        if int(i['timestamp']) > 1483200000:
            sum += int(i['new'])
    print sum

# def getFunRunTime(funcc):
#     start = time.time()
#     funcc()
#     end = time.time()
#     return end - start

def hashTrans(strw):
    url = 'http://biliquery.typcn.com/api/user/hash/' + strw
    try:
        r = requests.get(url)
    except:
        return
    if r.status_code == 200:
        jsonDoc = js.loads(r.text)
        if jsonDoc['error'] == 0:
            return jsonDoc['data'][0]['id']

# write userIdList of 'vCid' to the file 'filePath'
def writeUIdList(vCid, filePath):
    userList = xmlDL.migrateBD(vCid)[:, 6]
    uniUsers = np.unique(userList)
    print '---------totally', len(uniUsers), 'unique users in', vCid
    # print hashTrans(uniUsers[12])

    if not os.path.exists(filePath):
        os.mkdir(filePath)

    fo = open(filePath + 'userIdList.txt', "w+")
    for i in range(len(uniUsers)):
        transUserId = hashTrans(uniUsers[i])
        print transUserId
        fo.write(uniUsers[i] + ',' + str(transUserId))
        fo.write('\n')
    print '-----------all userIdList of', vCid ,'is downloaded to local'

# get getUserCodeIdList
# return a 2d list
def getUserCodeIdList(filePath):
    fo = open(filePath, "r")
    lines = fo.readlines()

    userCodeIdList = []
    for line in lines:
        line = line.strip('\n')
        userCodeId = line.split(',')
        userCodeIdList.append(userCodeId)
    return userCodeIdList

# get userId from 00251e3a to 586150, or return None
def getUserId(userCode, userCodeIdList):
    for userCodeId in userCodeIdList:
        if userCodeId[0] == userCode:
            return userCodeId[1]
            break
    return


def getTxtList(filePath):
    f = open(filePath)
    lines = f.readlines()

    wordList = []
    for line in lines:
        line = line.strip('\n')
        wordList.append(line)
        # print line

    return wordList

    # wordList = []
    # while line:
    #     wordList.append(line)
    #     print line,
    #     line = f.readline()
    # f.close()
    # return wordList

# compare similarity between two wordList
# Bag-of-words model
def getSimilarity(wordList1, wordList2):
    bag = wordList1 + wordList2
    bag = list(set(bag))

    # for i in bag:
    #     print i

    if len(bag) == 0:
        return
    vec1 = []
    vec2 = []
    for i in bag:
        vec1.append(wordList1.count(i))
        vec2.append(wordList2.count(i))

    product = 0
    sum1 = 0
    sum2 = 0
    for a,b in zip(vec1, vec2):
        # print a, b
        product += a * b
        sum1 += a ** 2
        sum2 += b ** 2

    if sum1 == 0 or sum2 == 0:
        return
    else:
        return float(product) / (sum1 ** 0.5 * sum2 ** 0.5)

# get all favTagTlist*.txt files of a video
def getFilesOfDir(vCid):
    print os.getcwd()
    filePath = 'data/users/' + vCid
    os.chdir(filePath)
    files = os.listdir(os.getcwd())
    files = [f for f in files if f[0:6] == 'favTag']
    os.chdir('../../../')

    return files

def decodeList(wordList):
    highFreqWordList = []
    for i in wordList:
        w = unicode(i, "utf-8")
        highFreqWordList.append(w)
    return highFreqWordList

if __name__ == '__main__':
    # 10506396
    vCid = xmlDL.vCid

    filePath = 'data/users/' + vCid + '/'
    # getTotalNumber()

    wordList1 = jieba.lcut('我觉得这个世界全怕猫。猫吃鱼也吃老鼠', cut_all=False)
    wordList2 = jieba.lcut('我觉得这个世界狗狗。猫吃鱼也打狗狗', cut_all=False)

    list1 = [1, 4, 1, 4, 9, 2]
    array1 = np.array(list1)
    array2 = np.arange(0, 10)
    # res = matchedCurve(array1)
    # print res(2), res(2.5)
    # plt.plot(array2, res(array2), 'b')
    # plt.show()

    # print getFilesOfDir(vCid)

    stopWords = getTxtList('/Users/admin/Summer/GradDesign/danmu/data/stopWord/stopWords.txt')
    h2 = decodeList(stopWords)
    print u'人' in h2
    # writeUIdList(vCid, filePath)










    # end
