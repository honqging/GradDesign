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
import jieba.posseg as pseg
import util

# all words should be added
jieba.load_userdict('data/jiebaNewWord/jiebaNewWord.txt')
jieba.load_userdict('data/jiebaNewWord/jiebaNewWord_Qingyunzhi.txt')


comUrl = 'http://comment.bilibili.tv'
currentTime = ''
everyDayTime = ''

# 10506396 大鱼海棠
# 5114160 大圣归来
# 1675077 西游降魔篇 29953
# 3876153 言叶之庭
# 5061993 这个杀手不太冷
# 4441226 伪装者01
# 4523969 伪装者20
# 9075603 青云志01
# 9648652 青云志07 7634
# 9648653 青云志08
# 15964545 全职高手01
# 15964540 全职高手02
# 17599975 全职高手07
# 18226264 全职高手08
# 17894824 全职高手09
# 18879785 極彩色【AGAI • EVALIA • REITA】原创振付(ReolxGigaP)
# 18915609 【sun】极乐净土 扬州大学毕业晚会 删减版
# 18860815 【C菌】黑魂版刺客信条!《刺客信条：起源》超长试玩！
# 18834653 《马里奥疯狂兔子》超长试玩！
# 18950057 董小姐在日本街头响起
# 18904668 录像证明李小龙的真实力量，轻量级身材，重量级的力道！
# 18845234 【鹿迪】陆地夫妇之《lie to me》脑洞特辑3
# 18234425 【暴走看啥片儿第三季】91 欢乐颂2小时代之女德时代，神奇女侠男朋友压力大
# 18766805 【暴走大事件第五季】18 琼瑶已被气哭！木子化身紫薇花样演绎还珠格格


vCid = '17894824'

def decodeList(wordList):
    highFreqWordList = []
    for i in wordList:
        w = unicode(i, "utf-8")
        highFreqWordList.append(w)
    return highFreqWordList

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
    totalLen = len(jsonDoc)
    print "--------------------the length of jsonDoc is:", totalLen

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

        print jsonDoc.index(i), '/', totalLen, i, "downloaded to local..."
    print "json length: ", len(jsonDoc)

def migrateBD(vCid):
    print 'migrateBD cwd:', os.getcwd()
    filePath = "../barrageData/" + vCid
    os.chdir(filePath)
    files = os.listdir(os.getcwd())
    # print files, type(files), len(files) # type = list
    barrageList = []
    ele = ''
    for file in files:
        # print file
        try:
            tree = ET.parse(file)
        except:
            print file, "this file is not able to parse.."
            continue
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

# input: (1) the return value of migrateBD()
# (2) delProperty: 0: delete actors' name
#                  1: hold actors' name
# return: all divided barrage data: 2d list
def divideSent(allBD, delProperty):
    # the list of all divided barrages
    divBarrageList = []

    # all words should be deleted
    highFreqWords = util.getTxtList('/Users/admin/Summer/GradDesign/danmu/data/highFreqWord/highFreqWords.txt')
    stopWords = util.getTxtList('/Users/admin/Summer/GradDesign/danmu/data/stopWord/stopWords.txt')

    if delProperty == 0:
        newWordsQingyunzhi = util.getTxtList('data/stopWord/jiebaNewWord_Qingyunzhi.txt')
        print 'Qingyunzhi is deleted...'
    elif delProperty == 1:
        newWordsQingyunzhi = []
        print 'Qingyunzhi is not deleted...'
    else:
        newWordsQingyunzhi = []

    highFreqWordList = decodeList(highFreqWords)
    stopWordList = decodeList(stopWords)
    newWordsQingyunzhiList = decodeList(newWordsQingyunzhi)

    # length = type(allBD) == list ? len(allBD):allBD.shape[0]
    if type(allBD) == list:
        length = len(allBD)
    else:
        length = allBD.shape[0]

    for i in range(length):
        # oneBarrageList = jieba.lcut(allBD[i][-1], cut_all = False)
        if type(allBD) == list:
            oneBarrageList_cut = pseg.cut(allBD[i][-1])
        else:
            oneBarrageList_cut = pseg.cut(allBD[i, -1])

        oneBarrageList = []

        # type(oneBarrageList_cut) == generator
        oneBarrageList = [word for word, flag in oneBarrageList_cut if flag == 'n']
        # oneBarrageList = [word for word, flag in oneBarrageList_cut if flag == 'n' or flag == 'a']

        # remove word in highFreqWords
        redWordL = list((set(highFreqWordList).union(set(stopWordList))).union(set(newWordsQingyunzhiList)))

        # for i in range(len(redWordL)):
        #     print redWordL[i]
            # if isinstance(redWordL[i], str):
            #     redWordL[i] = unicode(redWordL[i], 'utf-8')

        lenB = len(oneBarrageList)
        for i in range(lenB):
            # print lenB, i
            if i >= lenB:
                break
            # if oneBarrageList[i].encode('utf-8') == '逸才':
            #     print 'now is', oneBarrageList[i], type(oneBarrageList[i])
            if oneBarrageList[i] in redWordL:
                # print 'deleted....', oneBarrageList[i]
                del oneBarrageList[i]
                lenB -= 1

        divBarrageList.append(oneBarrageList)
    # dblLen = len(divBarrageList)
    return divBarrageList



if __name__ == '__main__':
    start = time.time()

    print '------------- processing ' + vCid + '-------------'
    for i in range(0):
        print i
    downloadBD(vCid)
    # allBD = migrateBD(vCid)
    # res = divideSent(allBD, 1)

    # mid = time.time()
    # print "spend time half way: ", mid - start
    #
    # ss = 0
    # for i in res:
    #     for j in i:
    #         print j,
    #         if len(j) == 0:
    #             ss += 1
    #     print
    # print ss, len(allBD), type(allBD)


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

    end = time.time()
    print "spend time: ", end - start
