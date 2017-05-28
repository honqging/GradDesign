# encoding: utf-8

from gensim import corpora, models, similarities
import matplotlib.pyplot as plt
import time
import numpy as np
import os
import sys

import xmlDL
import util
import clustering


# return the topic type with max posibility and the posibility of doc
# eg: doc--[(0, 0.033333333333334041), (1, 0.033333333333659149), (2, 0.03333333333337106), (3, 0.033333333333336511), (4, 0.033333333333333631), (5, 0.033333333577374141), (6, 0.033333333333333381), (7, 0.53333330176939997), (8, 0.033333333641347308), (9, 0.033333333333333388), (10, 0.033333333333333409), (11, 0.033333358397907714), (12, 0.033333333333333381), (13, 0.033333333333333368), (14, 0.033333339280269603)]
def getMax(doc):
    b = []
    b = [i[1] for i in doc]
    return b.index(max(b)), max(b)

# return a length of unique users and their barrage
# return 2 arguments, userList and related barrageList
# eg: uniBContentList: ['user', ['b1', 'b2', 'b3']]
# eg: uniBContentList2: ['user1', 'b1'], ['user1', 'b2']....
# eg: uniBContentListString: ['22ccd704', '\xe7\x88\xb7\xe7\x88\xb7QAQ']
def getUserAndBarrageList(barrageList):
    # duplicate users list
    dupUList = [barrage[6] for barrage in barrageList]
    uniUList = list(set(dupUList))

    print len(dupUList), len(uniUList)

    uniBContentList = []
    uniBContentList2 = []
    uniBContentListString = []

    # bNumPerUser[0]: the number of barrage comments of user 0
    bNumPerUser = []
    for user in uniUList:
        user2BList = [i for i, v in enumerate(dupUList) if v == user]
        bNumPerUser.append((user, len(user2BList)))

        bContentList = []
        for bContentIndex in user2BList:
            bContentList.append(barrageList[bContentIndex][-1])
            uniBContentList2.append([user, barrageList[bContentIndex][0], barrageList[bContentIndex][-1]])

        # 1st
        # all barrage comments sent by one user
        totalBofUser = ' '.join(bContentList)

        uniBContentList.append([user, bContentList])
        uniBContentListString.append([user, totalBofUser])

    # for i in range(len(uniUList)):
    #     print uniBContentList[i]
    return uniBContentList, uniBContentList2, uniBContentListString, bNumPerUser

# bNumPerUser: [('a', 2), ('b', 3), ('c', 1)]
def UBdistribution(bNumPerUser):
    # # duplicate users list
    # dupUList = [barrage[6] for barrage in barrageList]
    # uniUList = list(set(dupUList))
    # print len(dupUList), len(uniUList)
    #
    # # bNumPerUser[0]: the number of barrage comments of user 0
    # bNumPerUser = []
    # for user in uniUList:
    #     user2BList = [i for i, v in enumerate(dupUList) if v == user]
    #     bNumPerUser.append(len(user2BList))

    # numOfUsersList[0]: the number of users who has only 1 barrage
    numOfUsersList = [0] * 3
    for i in range(len(bNumPerUser)):
        if bNumPerUser[i][1] == 1:
            numOfUsersList[0] += 1
        elif bNumPerUser[i][1] == 2:
            numOfUsersList[1] += 1
        elif bNumPerUser[i][1] >= 3:
            numOfUsersList[2] += 1

            # print userIndex, userId
            # print i, bNumPerUser[i][0], bNumPerUser[i][1]
    return numOfUsersList

# remove users whose barrage number is less than lessNum
def removeBLessNum(uniBContentListString, bNumPerUser, lessNum):
    bNumMoreUserL = [i[0] for i in bNumPerUser if i[1] >= lessNum]
    print len(bNumMoreUserL), len(uniBContentListString)

    # print len(set(bNumMoreUserL).intersection(set(uniBContentListString)))
    # print set(bNumMoreUserL).intersection(set(uniBContentListString))

    u1 = uniBContentListString[0:len(uniBContentListString)]
    # u2 = uniBContentListString[10001:len(uniBContentListString)-1]
    for i in u1:
        try:
            if i[0] in bNumMoreUserL:
                continue
            else:
                # print i[0], i[1]
                uniBContentListString.remove(i)
        except:
            continue
    # for i in u2:
    #     if i[0] in bNumMoreUserL:
    #         continue
    #     else:
    #         # print i[0], len(i[1]), i[1]
    #         uniBContentListString.remove(i)

    return uniBContentListString

# get word appearing most in barrage comments
# return num words
def getMostWord(bContentList, num):
    print type(bContentList), type(bContentList[1])
    bContentList1d = []
    for i in bContentList:
        bContentList1d.extend(i)
    print "number of all words:", len(bContentList1d)
    bContentList1dSet = set(bContentList1d)
    print "number of unique words:", len(list(bContentList1dSet))
    xx = [(i, bContentList1d.count(i)) for i in bContentList1dSet]
    xx.sort(key=lambda x:x[1], reverse=True)
    # for i in range(100):
    #     print xx[i][0], xx[i][1]

    return xx[0:num] if len(xx) > num else xx

# input: 0.002*"合影" + 0.002*"钱" + 0.002*"撒花" + 0.002*"没" + 0.002*"完结" + 0.002*"看" + 0.002*"啊" + 0.002*"之" + 0.002*"湫" + 0.002*"一个"
# output: "合影" + "钱" + "撒花"....
def rmNum(ldaOutLine):
    splitRes = ldaOutLine.split('"')
    res = splitRes[1::2]
    return res

# return dic, corpus, tfidf based on the barrage of vCid
def preLda(vCid):
    bList = xmlDL.migrateBD(vCid)

    # eg: uniBContentList: ['user', ['b1', 'b2', 'b3']]
    # eg: uniBContentList2: ['user1', '157.430', 'b1'], ['user1', '159.430', 'b2']....
    # eg: uniBContentListString: ['22ccd704', '\xe7\x88\xb7\xe7\x88\xb7QAQ']
    uniBContentList, uniBContentList2, uniBContentListString, bNumPerUser = getUserAndBarrageList(bList)

    # list of a user's total barrage
    # newUniBContentListString = removeBLessNum(uniBContentListString, bNumPerUser, 3)

    # list of a user's one barrage
    newUniBContentListString = removeBLessNum(uniBContentList2, bNumPerUser, 3)

    bContentList = xmlDL.divideSent(newUniBContentListString, 1)

    # remove barrage comments which have no N or A
    print len(bContentList), len(newUniBContentListString)
    for bContentI in range(len(bContentList)):
        try:
            if len(bContentList[bContentI]) == 0:
                # bContentList.remove(bContentList[bContentI])
                # newUniBContentListString.remove(newUniBContentListString[bContentI])
                del bContentList[bContentI]
                del newUniBContentListString[bContentI]
        except:
            continue
    print len(bContentList), len(newUniBContentListString)

    print '---newUniBContentListString', newUniBContentListString[3][0], newUniBContentListString[10][1], newUniBContentListString[10][2]
    # print '---bContentList', bContentList[3], bContentList[10]

    # sys.exit()

    # 276088 words tatally
    # 17941 unique words
    # dictionary of all words
    dic = corpora.Dictionary(bContentList)
    print type(dic)
    # for word, index in dic.token2id.iteritems():
    #     word = word.encode('utf-8')
    #     print word, index
    print 'dictionary number of docs, num_pos, number of terms: ', dic.num_docs, dic.num_pos, len(dic)

    # text corpus
    corpus = [dic.doc2bow(text) for text in bContentList]
    # print max(corpus)

    tfidf = models.TfidfModel(corpus)
    print tfidf, type(tfidf)
    example = [(0, 1), (2, 1)]
    print tfidf[example]
    for word, index in dic.token2id.iteritems():
        if index == 4 or index == 0:
            word = word.encode('utf-8')
            print word, index
    return dic, corpus, tfidf, bContentList, newUniBContentListString


def ldaa(dic, corpus, tfidf, bContentList, newUniBContentListString, topicNum):
    corpus_tfidf = tfidf[corpus]
    print '------------------type(corpus_tfidf):', type(corpus_tfidf)
    # for i in corpus_tfidf:
    #     print i

    lda = models.LdaModel(corpus_tfidf, id2word=dic, num_topics=topicNum)
    ldaOut = lda.print_topics(topicNum)


    li = 5
    vec = [(0, 1), (4, 1)]
    vec = dic.doc2bow(bContentList[li])

    # get similarity matrix of len(bContentList) * len(bContentList)
    index = similarities.MatrixSimilarity(lda[corpus])
    simMatrix = []

    # get the Similarity Matrix(eg: 100 * 100) of all barrages,
    for bIndex in range(len(bContentList)):
        vec = bContentList[bIndex]
        vec_bow = dic.doc2bow(bContentList[bIndex])
        vec_lda = lda[vec_bow]
        sims = index[vec_lda]

        # print list(enumerate(sims))

        # sorted with similarity from high to low
        # sims = sorted(enumerate(sims), key=lambda item: -item[1])
        # print sims, len(sims), type(sims)

        simMatrix.append(list(enumerate(sims)))

    # eg: simMatrix[1] = [(0, 0.91061151), (1, 0.99999994), (2, 0.99999994), (3, 0.99999994), (4, 0.73748994), (5, 0.81874228)......]
    # print len(simMatrix), simMatrix[1]
    # sys.exit()


    # print all lda topics words
    # such as:
    # 0.002*"合影" + 0.002*"钱" + 0.002*"撒花" + 0.002*"没" + 0.002*"完结" + 0.002*"看" + 0.002*"啊" + 0.002*"之" + 0.002*"湫" + 0.002*"一个"
    # 0.002*"买" + 0.002*"第一次" + 0.002*"支持" + 0.002*"啊" + 0.002*"没" + 0.002*"完结" + 0.002*"湫" + 0.002*"国漫" + 0.002*"撒花" + 0.002*"b"
    # 0.004*"第一次" + 0.003*"湫" + 0.003*"合影" + 0.003*"在" + 0.003*"存活" + 0.003*"买" + 0.003*"确认" + 0.003*"啊" + 0.003*"椿" + 0.002*"撒花"
    # 0.003*"完结" + 0.003*"撒花" + 0.003*"钱" + 0.003*"合影" + 0.002*"再见" + 0.002*"没" + 0.002*"啊" + 0.002*"湫" + 0.002*"好" + 0.001*"第一次"
    # 0.003*"存活" + 0.003*"确认" + 0.002*"合影" + 0.002*"没" + 0.002*"钱" + 0.002*"秋水共长天一色" + 0.002*"第一次" + 0.001*"靠" + 0.001*"也" + 0.001*"生日"
    for i in ldaOut:
        r = i[1].encode('utf-8')
        print r

    for i in ldaOut:
        r = i[1].encode('utf-8')
        print 'Topic', ldaOut.index(i), ':',
        util.printList(rmNum(r))

    # sys.exit()

    print type(ldaOut[0])
    print type(ldaOut[0][0])

    corpus_lda = lda[corpus_tfidf]
    resList = []
    iii = 0

    # eg: doc [(0, 0.033333333333334041), (1, 0.033333333333659149), (2, 0.03333333333337106), (3, 0.033333333333336511), (4, 0.033333333333333631), (5, 0.033333333577374141), (6, 0.033333333333333381), (7, 0.53333330176939997), (8, 0.033333333641347308), (9, 0.033333333333333388), (10, 0.033333333333333409), (11, 0.033333358397907714), (12, 0.033333333333333381), (13, 0.033333333333333368), (14, 0.033333339280269603)]
    for doc in corpus_lda:
        # eg: res = (3, 0.72867093662442284), res has 72% posibility to be in type 3
        res = getMax(doc)
        resList.append(res)
    print '---type(corpus_tfidf), type(corpus_lda)', type(corpus_tfidf), type(corpus_lda)
    print '---len(resList)', len(resList)

    # len = topicNum
    simMatrixTopicList = []
    for topicId in range(topicNum):
        simMatrixTopic = [i for i in range(len(resList)) if resList[i][0] == topicId]
        print topicId, 'topic has:', len(simMatrixTopic), 'barrage'
        simMatrixTopicList.append(simMatrixTopic)
        # print len(simMatrixTopic), simMatrixTopic



    # without square
    # # inner distance
    # # sum of all similarity of i'th row
    # iRow = 0.0
    # num = 0
    # innDisMatrix = [0.0 for i in range(topicNum)]
    # for topicId in range(topicNum):
    #     for i in range(len(simMatrixTopicList[topicId])-1):
    #         for j in range(i+1, len(simMatrixTopicList[topicId])):
    #             # print simMatrix[simMatrixTopicList[topicId][i]][simMatrixTopicList[topicId][j]][1]
    #             iRow += simMatrix[simMatrixTopicList[topicId][i]][simMatrixTopicList[topicId][j]][1]
    #         # print topicId, 'topic, num:', num
    #     lenOfIRow = len(simMatrixTopicList[topicId])
    #     numOfIRow = (1 + lenOfIRow - 1) * (lenOfIRow - 1) / 2
    #     innDisMatrix[topicId] = iRow/numOfIRow
    #     iRow = 0.0
    # print 'inner distance:', innDisMatrix
    #
    # aveInnDis = sum(innDisMatrix) / len(innDisMatrix)
    # print 'average inner distance:', aveInnDis
    #
    # # external distance
    # cols = topicNum
    # rows = topicNum
    # extDisMatrix = [[0.0 for col in range(cols)] for row in range(rows)]
    # iRow = 0.0
    # for topicId in range(topicNum):
    #     for ti2 in range(topicId+1, topicNum):
    #         for i in range(len(simMatrixTopicList[topicId])):
    #             for j in range(len(simMatrixTopicList[ti2])):
    #                 iRow += simMatrix[simMatrixTopicList[topicId][i]][simMatrixTopicList[ti2][j]][1]
    #             # iRow += iRow
    #         # print iRow
    #         lenOfIRow = len(simMatrixTopicList[topicId]) * len(simMatrixTopicList[ti2])
    #         extDisMatrix[topicId][ti2] = iRow / float(lenOfIRow)
    #         iRow = 0.0
    #
    # print 'external distance:', extDisMatrix
    #
    # totExtDis = 0
    # aveExtDis = 0
    # num = 0
    # for i in extDisMatrix:
    #     for j in i:
    #         if j != 0:
    #             totExtDis += j
    #             num += 1
    # aveExtDis = totExtDis / float(num)
    #
    # print 'average external distance:', aveExtDis
    # print 'inner/external value:', aveInnDis/aveExtDis




    # within square(**2)

    # inner distance
    # sum of all similarity of i'th row
    iRow = 0.0
    num = 0
    innDisMatrix = [0.0 for i in range(topicNum)]

    # innDisMatrixNum[0]: the number of similarity value every topic
    innDisMatrixNum = [0.0 for i in range(topicNum)]
    for topicId in range(topicNum):
        for i in range(len(simMatrixTopicList[topicId])-1):
            for j in range(i+1, len(simMatrixTopicList[topicId])):
                iRow += (simMatrix[simMatrixTopicList[topicId][i]][simMatrixTopicList[topicId][j]][1]) ** 2
            # print topicId, 'topic, num:', num
        lenOfIRow = len(simMatrixTopicList[topicId])
        numOfIRow = (1 + lenOfIRow - 1) * (lenOfIRow - 1) / 2
        innDisMatrix[topicId] = iRow/numOfIRow
        # innDisMatrixNum[topicId] = numOfIRow
        iRow = 0.0
    print 'inner distance:', innDisMatrix

    aveInnDis = 1/(sum(innDisMatrix)/topicNum)
    print 'average inner distance:', aveInnDis

    # external distance
    cols = topicNum
    rows = topicNum
    extDisMatrix = [[0.0 for col in range(cols)] for row in range(rows)]

    # extDisMatrixNum[0]: the number of similarity value every topic
    # extDisMatrixNum = [[0.0 for col in range(cols)] for row in range(rows)]
    iRow = 0.0
    # countt = 0
    for topicId in range(topicNum):
        for ti2 in range(topicId+1, topicNum):
            for i in range(len(simMatrixTopicList[topicId])):
                for j in range(len(simMatrixTopicList[ti2])):
                    iRow += (simMatrix[simMatrixTopicList[topicId][i]][simMatrixTopicList[ti2][j]][1]) ** 2
                    # countt += 1
            # print iRow
            iRowNum = len(simMatrixTopicList[topicId]) * len(simMatrixTopicList[ti2])
            # print 'iRowNum:', iRowNum, 'countt:', countt
            extDisMatrix[topicId][ti2] = iRow/iRowNum
            iRow = 0.0
            # countt = 0

    print 'external distance:', extDisMatrix

    totExtDis = 0
    aveExtDis = 0

    for i in extDisMatrix:
        for j in i:
            totExtDis += j
    extNoneZeroNum = (1 + cols - 1) * (cols - 1)/2

    aveExtDis = 1/(totExtDis/extNoneZeroNum)

    print 'average external distance:', aveExtDis
    print 'inner/external value:', aveInnDis/aveExtDis

    # return aveInnDis, aveExtDis

















    # sys.exit()


    topicPosi = []
    for topicId in range(topicNum):
        posiList = [i[1] for i in resList if i[0] == topicId]

        # average accuracy rate
        possi = sum(posiList)/len(posiList)
        topicPosi.append(possi)

    # sys.exit(0)

    fullPath = os.getcwd()

    # concatenate full path
    userCodeIdListFilePath = fullPath + '/data/users/' + vCid + '/userIdList.txt'
    userCodeIdList = util.getUserCodeIdList(userCodeIdListFilePath)
    # for i in userCodeIdList:
    #     print i

    favTagTlist = util.getFilesOfDir(vCid)

    # concatenate full path
    favTagTlist = [fullPath + '/data/users/' + vCid + '/' + tagT for tagT in favTagTlist]
    for i in favTagTlist:
        print i
    tagMatrix, tagVNumMatrix, userList, catAll = clustering.scanAllTags(favTagTlist)

    catNum = len(catAll)

    # eg: topicDist =
    # [[125.  126.   83.   18.  121.   44.   72.    0.  108.  113.   46.   66.  114.    0.  109.],
    # [ 799.  785.  558.  141.  737.  286.  425.    2.  659.  611.  376.  460.  765.    0.  657.],
    # [ 308.  321.  238.   48.  272.  116.  162.    0.  259.  236.  135.  173.  284.    1.  267.],
    # [ 557.  540.  378.   99.  490.  215.  315.    0.  457.  424.  232.  295.  514.    0.  449.],
    # [ 537.  535.  361.   86.  477.  176.  293.    0.  463.  416.  234.  297.  509.    0.  444.]]
    # 音乐 动画 番剧 广告 电影 时尚 舞蹈 公告 游戏 鬼畜 娱乐 电视剧 生活 活动 科技
    topicDist = np.zeros((topicNum, catNum))
    # every percentage of topic
    topicPercDist = np.zeros((topicNum, catNum))

    topicDistNoneNum = np.zeros(topicNum)
    userIdNoneNum = 0

    # topic index list: [0, 1, 2, 3, 4]
    topicNumList = range(topicNum)

    # a list of: all users' barrage data of a topic
    aTopicNewUniBContentListString = []
    topicUserNumList = []

    for i in topicNumList:
        aTopicNewUniBContentListString.append([])
        topicUserNumList.append(0)

    for i in range(len(resList)):
        # print i
        topicId = resList[i][0]
        if topicId in topicNumList:
            userId = util.getUserId(newUniBContentListString[i][0], userCodeIdList)
            # print newUniBContentListString[i][0], userId
            aTopicNewUniBContentListString[topicId].append(newUniBContentListString[i])
            topicUserNumList[topicId] += 1

            if userId is not None:
                # print userId, favTagTlist, type(favTagTlist)
                res = clustering.getTagLineOfUser(tagMatrix, tagVNumMatrix, userList, userId)
                if res is not None:
                    tagLineOfUI, tagVNumLineOfUI = res
                # userId is not in the list
                else:
                    continue

                if tagLineOfUI is not None:
                    # print len(tagLineOfUI), userId, tagLineOfUI
                    topicDist[topicId] += tagLineOfUI

                    # the perc distribution of tagVideo number of a user
                    tagVPercLineOfUI = np.around(tagVNumLineOfUI / float(sum(tagVNumLineOfUI)), 3)
                    topicPercDist[topicId] += tagVPercLineOfUI
                else:
                    topicDistNoneNum += 1
            else:
                userIdNoneNum += 1

    topicWordBListL = []
    # topicWordBListLSec = []
    topicWordBListL2 = []

    # print Top 10 frequent words in a topic & the barrageList of the topic, in one time
    for i in topicNumList:
        bContentList2 = xmlDL.divideSent(aTopicNewUniBContentListString[i], 0)
        wordList2 = getMostWord(bContentList2, 20)
        print '------------topic', i, ':',
        for j in wordList2:
            print j[0],
        print

    # print Top 10 frequent words in a topic & the barrageList of the topic
    for i in topicNumList:
        print '------------topic', i, '-------------users:', topicUserNumList
        bContentList = xmlDL.divideSent(aTopicNewUniBContentListString[i], 0)
        wordList = getMostWord(bContentList, 20)
        for j in wordList:
            print j[0], j[1]

        for j in aTopicNewUniBContentListString[i]:
            # eg: abb5230a 417.671 灵尊：哟，火柴棍
            # print j[2]

            if wordList[0][0].encode('utf-8') in j[2]:
                util.printList(j)

        # the index list of all barrage in topic i which contains the 1st frequent word in topic i
        topicIWord1BList = [j[1] for j in aTopicNewUniBContentListString[i] if wordList[0][0].encode('utf-8') in j[2]]
        topicWordBListL.append(topicIWord1BList)

        # second word
        # topicIWord1BListSec = [j[1] for j in aTopicNewUniBContentListString[i] if wordList[1][0].encode('utf-8') in j[2]]
        # topicWordBListLSec.append(topicIWord1BListSec)

        # 0.002*"合影" + 0.002*"钱" + 0.002*"撒花" + 0.002*"没" + 0.002*"完结" + 0.002*"看" + 0.002*"啊" + 0.002*"之" + 0.002*"湫" + 0.002*"一个"
        # "合影" + "钱" + "撒花" + "没" + .....
        wordList2 = rmNum(ldaOut[i][1].encode('utf-8'))

        # get the most weight word in wordList2(after deleting actors' name)
        # eg: wordList2 = '''0.440*"小凡" + 0.030*"鲸鱼" + 0.018*"上线" + 0.014*"灰" + 0.013*"套路" + 0.012*"官方" + 0.010*"小痴" + 0.009*"滴血" + 0.009*"姐姐" + 0.009*"嘴"'''
        # firstWord = '上线', (default firstWord is '小凡')
        firstWord = wordList2[0]
        for word in wordList2:
            if word in util.getTxtList('data/stopWord/jiebaNewWord_Qingyunzhi.txt'):
                continue
            else:
                firstWord = word
                break

        # the index list of all barrage in topic i which contains the 1st frequent word(with weight) in topic i
        topicIWord1BList2 = [j[1] for j in aTopicNewUniBContentListString[i] if firstWord in j[2]]
        topicWordBListL2.append(topicIWord1BList2)

    plt.figure(1)
    plt.subplot(211)
    for i in topicWordBListL2:
        y = [topicWordBListL2.index(i) for indexx in range(len(i))]
        plt.scatter(i, y, marker = 'x', color = 'r')
    plt.plot([], marker = 'x', color = 'r', label = 'Most weight words')
    plt.xlim(0,)
    plt.legend()
    plt.xlabel('Barrage Time(s)')
    plt.ylabel('Topic ID')

    plt.subplot(212)
    for i in topicWordBListL:
        y = [topicWordBListL.index(i) for indexx in range(len(i))]
        plt.scatter(i, y, marker = '.', color = 'b')
        # print 'len(i), len(y):', len(i), len(y), i, y
    plt.plot([], marker = '.', color = 'b', label = 'Most frequent words')
    plt.xlim(0,)
    plt.legend()
    plt.xlabel('Barrage Time(s)')
    plt.ylabel('Topic ID')

    plt.show()




    print 'the num of users of different topics:', topicUserNumList
    print 'the num of users who is not in userCodeIdList:', userIdNoneNum
    print '-------------------------'


    # print topicDist

    topicDist2 = np.sum(topicDist, axis=1)
    # the percentage of tag of a user
    topicDist3 = np.transpose(np.transpose(topicDist) / np.float16(topicDist2))
    print topicDist3, '\n'

    print topicPercDist, topicPercDist[1][1]
    np.savetxt('topicDist.txt', topicDist)
    np.savetxt('topicPercDist.txt', topicPercDist)




    print topicNum, "topics possibility average value:", topicPosi, sum(topicPosi)/len(topicPosi)

    resIndexList = [i[0] for i in resList]
    resTypeList = list(set(resIndexList))
    # number of type index
    resTCountList = []
    # barrage sequence number of type index
    indexList = []

    for index in resTypeList:
        resTCountList.append(resIndexList.count(index))
        indexList.append([i for i, v in enumerate(resIndexList) if v==index])

    # print resTCountList
    # print indexList[0]

    # type 0
    print 'all barrage comments of type 000000000000000------------'
    # for i in indexList[0]:
    #     print uniBContentList[i][-1]

    plt.xlabel("Barrage Type")
    plt.ylabel("Barrage Number")
    plt.plot(resTCountList, 'r-')

    # plt.show()

    # return 1/aveInnDis, 1/aveExtDis
    return aveInnDis, aveExtDis





if __name__ == '__main__':
    start = time.time()

    # inputt = '''0.440*"小凡" + 0.030*"鲸鱼" + 0.018*"上线" + 0.014*"灰" + 0.013*"套路" + 0.012*"官方" + 0.010*"小痴" + 0.009*"滴血" + 0.009*"姐姐" + 0.009*"嘴"'''
    # wordList2 = rmNum(inputt)
    # sys.exit()
    # 10506396
    vCid = xmlDL.vCid

    dic, corpus, tfidf, bContentList, newUniBContentListString = preLda(vCid)

    res1 = []
    res2 = []
    res3 = []
    res4 = []
    startNum = 5
    endNum = 30
    for i in range(startNum, endNum):
        rr, bb = ldaa(dic, corpus, tfidf, bContentList, newUniBContentListString, i)
        res1.append(rr)
        res2.append(bb)
        res3.append(rr/bb)
        res4.append(i*rr/bb)
    print 'res1, res2, res3, res4:', res1, res2, res3, res4
    # ldaa(dic, corpus, tfidf, bContentList, 3)

    # res1 = [1.0544493026127693, 1.0631692852322596, 1.0706627594883988, 1.0762710917061373, 1.0745842686447082, 1.0933972543829975, 1.0888570040125489, 1.0911575219351848, 1.0927331799748239, 1.0945941533688093, 1.1063791046526219, 1.1067955828816247]
    # res2 = [1.7322792524164738, 2.0461452351681504, 2.3313144203074438, 2.6418363406085343, 2.9201591076490407, 3.2109596182074238, 3.5214219904499773, 3.8210286583022359, 4.0992489887148995, 4.3890003206949713, 4.7383323344126937, 4.9375910218306878]
    # res3 = [0.60870630479574606, 0.51959619823608916, 0.45925283615206414, 0.40739506651582491, 0.36798825989650735, 0.34052040025137603, 0.30920946338311806, 0.28556643237007523, 0.26656911619252288, 0.2493948674844223, 0.23349546350250994, 0.22415699842050976]
    xlim = range(startNum, len(res1)+startNum)

    plt.figure(1)
    plt.subplot(411)
    plt.plot(xlim, res1, 'r')
    plt.xlabel("Topic Number")
    plt.ylabel("Inner Distance")

    plt.subplot(412)
    plt.plot(xlim, res2, 'g')
    plt.xlabel("Topic Number")
    plt.ylabel("External Distance")

    plt.subplot(413)
    plt.plot(xlim, res3, 'b')
    plt.xlabel("Topic Number")
    plt.ylabel("Inn/Ext Distance")

    plt.subplot(414)
    plt.plot(xlim, res4, 'y')
    plt.xlabel("Topic Number")
    plt.ylabel("M * Inn/Ext Distance")
    # plt.show()






    # bList = xmlDL.migrateBD()

    # eg: uniBContentList: ['user', ['b1', 'b2', 'b3']]
    # eg: uniBContentListString: ['22ccd704', '\xe7\x88\xb7\xe7\x88\xb7QAQ']
    # uniBContentList, uniBContentListString, bNumPerUser = getUserAndBarrageList(bList)
    # print UBdistribution(bNumPerUser)
    # print len(uniBContentListString)
    # removeBLessNum(uniBContentListString, bNumPerUser, 3)
    # bContentList = xmlDL.divideSent(uniBContentListString)
    # wordList = getMostWord(bContentList, 100)
    # for i in wordList:
    #     print i[0], i[1]


    end = time.time()

    print 'cost', end - start, 'seconds --------------'
