# encoding: utf-8

import numpy as np
import json as js
import requests
import time
import xmlDL
import jieba
import test
import matplotlib.pyplot as plt

jieba.load_userdict('data/jiebaNewWord/jiebaNewWord.txt')


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
    r = requests.get(url)
    if r.status_code == 200:
        jsonDoc = js.loads(r.text)
        if jsonDoc['error'] == 0:
            return jsonDoc['data'][0]['id']

def getUIdList():
    userList = xmlDL.migrateBD()[:, 6]
    uniUsers = np.unique(userList)
    # print uniUsers[12], type(uniUsers[13]), len(uniUsers)
    # print hashTrans(uniUsers[12])

    fo = open("10506396Users.txt", "w")
    for i in range(len(uniUsers)):
        transUserId = hashTrans(uniUsers[i])
        print transUserId
        fo.write(uniUsers[i] + ',' + str(transUserId))
        fo.write('\n')

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

    # print vec1
    # print vec2
    # print product, sum1, sum2

    if sum1 == 0 or sum2 == 0:
        return
    else:
        return float(product) / (sum1 ** 0.5 * sum2 ** 0.5)


if __name__ == '__main__':
    # getTotalNumber()

    wordList1 = jieba.lcut('我觉得这个世界全怕猫。猫吃鱼也吃老鼠', cut_all=False)
    wordList2 = jieba.lcut('我觉得这个世界狗狗。猫吃鱼也打狗狗', cut_all=False)

    list1 = [1, 4, 1, 4, 9, 2]
    array1 = np.array(list1)
    array2 = np.arange(0, 10)
    res = matchedCurve(array1)
    # print res(2), res(2.5)
    plt.plot(array2, res(array2), 'b')
    plt.show()





    # getUIdList()
