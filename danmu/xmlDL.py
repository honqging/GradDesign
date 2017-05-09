# encoding: utf-8

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.cElementTree as ET
import time
import xml.sax
import requests
import json as js
import os
import numpy as np
from numpy import linalg as la
import jieba
import util

comUrl = 'http://comment.bilibili.tv'
currentTime = ''
everyDayTime = ''


# wordList = util.getTxtList('data/highFreqWord/highFreqWord.txt')
# nWordList = []
# for i in wordList:
#     w = unicode(i, "utf-8")
#     nWordList.append(w)
def decodeList(wordList):
    nWordList = []
    for i in wordList:
        w = unicode(i, "utf-8")
        nWordList.append(w)
    return nWordList

def buildUrl(cid):
    return '/'.join([comUrl, cid]).join('.xml')

def newDir(dirName):
    if not os.path.exists("../barrageData/" + dirName):
        os.chdir("../barrageData")
        os.mkdir(dirName)
        os.chdir("../danmu")

def downloadBD(vCid):
    # bUrl = buildUrl(vCid)
    bUrl = 'http://comment.bilibili.com/rolldate,' + vCid
    s = requests.get(bUrl)
    # print s.text
    jsonDoc = js.loads(s.text)
    sum = 0

    # new a dir to store all barrage .xml data
    newDir(vCid)
    for i in jsonDoc:
        # if int(i['timestamp']) == 1481299200:
        everyDayTime = str(i['timestamp'])
        dayUrl = 'http://comment.bilibili.com/dmroll,' + everyDayTime + ',' + vCid
        ds = requests.get(dayUrl)
        # ds.encoding = 'xml'
        # print type(ds.text)
        # print type(ds.content)

        # print os.getcwd()
        filePath = "../barrageData/" + vCid + "/" + str(i['timestamp']) + '.xml'
        if not os.path.isfile(filePath):
            fo = open(filePath, "w+")
            fo.write(ds.content)
            # print os.getcwd()

        print i, "downloaded to local path...."
    print "json length: ", len(jsonDoc)

def migrateBD(vCid):
    print os.getcwd()
    filePath = "../barrageData/" + vCid
    os.chdir(filePath)
    files = os.listdir(os.getcwd())
    # print files, type(files),len(files)
    barrageList = []
    ele = ''
    for file in files:
        tree = ET.parse(file)
        for elem in tree.iter(tag = 'd'):
            pDataList = elem.attrib['p'].split(',')
            if type(elem.text) == unicode:
                ele = elem.text.encode('utf-8')
            pDataList.append(ele)
            barrageList.append(pDataList)
        # print len(barrageList), type(barrageList), barrageList[1]

        # if files.index(file) == 28:
        #     break
    bListArray = np.array(barrageList)
    newbListArray = bListArray[:, [0,4,6]]
    # newbListArray.sort()

    # delete duplicated rows
    a = bListArray # return all barrage information
    # a = newbListArray # return selected barrage information
    b = np.ascontiguousarray(a).view(np.dtype((np.void, a.dtype.itemsize * a.shape[1])))
    _, idx = np.unique(b, return_index=True)
    newbListArray = a[idx]

    # print type(newbListArray[1]), len(newbListArray), newbListArray[55]
    print "-----", len(newbListArray), "barrage data loaded-----"
    os.chdir("../../danmu")

    # all barrage data with 9 parameters: 8 barrage parameters, and barrage data
    return newbListArray

# input: the return value of migrateBD()
# return: all divided barrage data: 2d list
def divideSent(allBD):
    # the list of all divided barrages
    divBarrageList = []

    wordList = util.getTxtList('data/highFreqWord/highFreqWord.txt')
    nWordList = decodeList(wordList)
    if type(allBD) == list:
        length = len(allBD)
        for i in range(length):
            # print type(allBD[i][-1])
            oneBarrageList = jieba.lcut(allBD[i][-1], cut_all = False)
            n = len(oneBarrageList)
            # remove word in wordList
            redWordL = set(oneBarrageList).intersection(set(nWordList))
            # print 'len(redWordL)', len(redWordL)
            oneBarrageList = list(set(oneBarrageList).difference(redWordL))
            # print 'reduced words', n - len(oneBarrageList)

            # oneBarrageList = jieba.lcut(sentence, cut_all=False)
            divBarrageList.append(oneBarrageList)
    else:
        length = allBD.shape[0]
        for i in range(length):
            n = len(oneBarrageList)
            oneBarrageList = jieba.lcut(allBD[i, -1], cut_all = False)

            # remove word in wordList
            redWordL = set(oneBarrageList).intersection(set(nWordList))
            # print 'len(redWordL)', len(redWordL)
            oneBarrageList = list(set(oneBarrageList).difference(redWordL))
            # print 'reduced words', n - len(oneBarrageList)


            # oneBarrageList = jieba.lcut(sentence, cut_all=False)
            divBarrageList.append(oneBarrageList)
    # dblLen = len(divBarrageList)
    return divBarrageList



if __name__ == '__main__':
    vCid = '7182741'
    downloadBD(vCid)
    # allBD = migrateBD(vCid)
    # print len(allBD)
    #
    # userList = allBD[:, 6]
    # uniUsers = np.unique(userList)
    #
    # # the list of all divided barrages
    # divBarrageList = divideSent(allBD)
    # dblLen = len(divBarrageList)
    # for i in divBarrageList:
    #     print i
    #
    # print dblLen
    # print '-----', len(uniUsers), 'users -----'
