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
            uniBContentList2.append([user, barrageList[bContentIndex][-1]])

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

    u1 = uniBContentListString[0:len(uniBContentListString)-1]
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

    print len(uniBContentListString)
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



def ldaa(vCid, topicNum):
    print 'current working directory:', os.getcwd()
    bList = xmlDL.migrateBD(vCid)

    # eg: uniBContentList: ['user', ['b1', 'b2', 'b3']]
    # eg: uniBContentList2: ['user1', 'b1'], ['user1', 'b2']....
    # eg: uniBContentListString: ['22ccd704', '\xe7\x88\xb7\xe7\x88\xb7QAQ']
    uniBContentList, uniBContentList2, uniBContentListString, bNumPerUser = getUserAndBarrageList(bList)

    # list of a user's total barrage
    # newUniBContentListString = removeBLessNum(uniBContentListString, bNumPerUser, 3)

    # list of a user's one barrage
    newUniBContentListString = removeBLessNum(uniBContentList2, bNumPerUser, 3)

    bContentList = xmlDL.divideSent(newUniBContentListString)

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

    # sys.exit(0)

    # print '---newUniBContentListString', newUniBContentListString[3][1], newUniBContentListString[10][1]
    # print '---bContentList', bContentList[3], bContentList[10]






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

    # calculate similarities
    # index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=topicNum)
    # sims = index[tfidf[example]]
    # print list(enumerate(sims))
    # print type(examSims)

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
    # print len(simMatrix), simMatrix[1]


    # print all lda topics words
    # such as:
    # 0.002*"合影" + 0.002*"钱" + 0.002*"撒花" + 0.002*"没" + 0.002*"完结" + 0.002*"看" + 0.002*"啊" + 0.002*"之" + 0.002*"湫" + 0.002*"一个"
    # 0.002*"买" + 0.002*"第一次" + 0.002*"支持" + 0.002*"啊" + 0.002*"没" + 0.002*"完结" + 0.002*"湫" + 0.002*"国漫" + 0.002*"撒花" + 0.002*"b"
    # 0.004*"第一次" + 0.003*"湫" + 0.003*"合影" + 0.003*"在" + 0.003*"存活" + 0.003*"买" + 0.003*"确认" + 0.003*"啊" + 0.003*"椿" + 0.002*"撒花"
    # 0.003*"完结" + 0.003*"撒花" + 0.003*"钱" + 0.003*"合影" + 0.002*"再见" + 0.002*"没" + 0.002*"啊" + 0.002*"湫" + 0.002*"好" + 0.001*"第一次"
    # 0.003*"存活" + 0.003*"确认" + 0.002*"合影" + 0.002*"没" + 0.002*"钱" + 0.002*"秋水共长天一色" + 0.002*"第一次" + 0.001*"靠" + 0.001*"也" + 0.001*"生日"
    for i in ldaOut:
        r = i[1]
        r = r.encode('utf-8')
        print r, type(r)
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

    # inner distance
    iRow = 0.0
    num = 0
    innDisMatrix = [0.0 for i in range(topicNum)]
    for topicId in range(topicNum):
        for i in range(len(simMatrixTopicList[topicId])-1):
            for j in range(i+1, len(simMatrixTopicList[topicId])):
                # print simMatrix[simMatrixTopicList[topicId][i]][simMatrixTopicList[topicId][j]][1]
                iRow += simMatrix[simMatrixTopicList[topicId][i]][simMatrixTopicList[topicId][j]][1]
            # print topicId, 'topic, num:', num
        lenOfIRow = len(simMatrixTopicList[topicId])
        numOfIRow = (lenOfIRow + 1) * lenOfIRow / 2
        innDisMatrix[topicId] = iRow/numOfIRow
        iRow = 0.0
    print 'inner distance:', innDisMatrix

    aveInnDis = sum(innDisMatrix) / len(innDisMatrix)
    print 'average inner distance:', aveInnDis

    # sys.exit()


    # external distance
    cols = topicNum
    rows = topicNum
    extDisMatrix = [[0.0 for col in range(cols)] for row in range(rows)]
    iRow = 0.0
    for topicId in range(topicNum):
        for ti2 in range(topicId+1, topicNum):
            for i in range(len(simMatrixTopicList[topicId])):
                for j in range(len(simMatrixTopicList[ti2])):
                    iRow += simMatrix[simMatrixTopicList[topicId][i]][simMatrixTopicList[ti2][j]][1]
                # iRow += iRow
            # print iRow
            lenOfIRow = len(simMatrixTopicList[topicId]) * len(simMatrixTopicList[ti2])
            extDisMatrix[topicId][ti2] = iRow / float(lenOfIRow)
            iRow = 0.0

    print 'external distance:', extDisMatrix

    totExtDis = 0
    aveExtDis = 0
    num = 0
    for i in extDisMatrix:
        for j in i:
            if j != 0:
                totExtDis += j
                num += 1
    aveExtDis = totExtDis / float(num)

    print 'average external distance:', aveExtDis
    print 'inner/external value:', aveInnDis/aveExtDis








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
        # print 'topic', topicId, 'is calculated.'
    # for i in topicDist:
    #     print i
    for i in topicNumList:
        print '------------topic', i, '-------------users:', topicUserNumList
        bContentList = xmlDL.divideSent(aTopicNewUniBContentListString[i])
        wordList = getMostWord(bContentList, 20)
        # for j in wordList:
        #     print j[0], j[1]

        for j in aTopicNewUniBContentListString[i]:
            print j[0], j[1]

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

    return 1/aveInnDis, 1/aveExtDis



if __name__ == '__main__':
    start = time.time()

    # 10506396
    vCid = xmlDL.vCid

    res1 = []
    res2 = []
    res3 = []
    # for i in range(3, 15):
    #     rr, bb = ldaa(vCid, i)
    #     res1.append(rr)
    #     res2.append(bb)
    #     res3.append(rr/bb)
    # print res1, res2, res3
    ldaa(vCid, 10)

    # res1 = [1.0524856030567495, 1.0633693280876479, 1.0524856030567495, 1.0633693280876479]
    # res2 = [1.7148415205679695, 2.0331786557644111, 3.0524856030567495, 4.0633693280876479]
    # res3 = [0.61375094458183965, 0.52300830774158136, 5.0524856030567495, 1.0633693280876479]

    # res1 = [1.0536764566835712, 1.0617300379997179, 1.0678292753331489, 1.0843669639287428, 1.0901584860513163, 1.0949943152153629, 1.0974523114443733, 1.0916883894929417, 1.1023611448884925, 1.109015211546823, 1.1134719136436293, 1.1052127030191337]
    # res2 = [1.690701968280315, 2.0350923498288953, 2.3313657375305334, 2.6190029210480317, 2.8995538803459144, 3.1553686897335864, 3.4810853035099627, 3.7567911588778493, 4.0663518095401878, 4.3141086286793247, 4.6675958115718323, 5.0051861828895072]
    # res3 = [0.62321832969491986, 0.52171098677118266, 0.45802735201222955, 0.41403808877571535, 0.37597455713472078, 0.34702579092518515, 0.3152615393646967, 0.29059065125649097, 0.27109340178147168, 0.25706705764762466, 0.23855362773338828, 0.22081350475979525]
    # plt.figure(1)
    # plt.subplot(311)
    # plt.plot(res1, 'r')
    # plt.xlabel("Topic Number")
    # plt.ylabel("Inner Distance")
    #
    # plt.subplot(312)
    # plt.plot(res2, 'g')
    # plt.xlabel("Topic Number")
    # plt.ylabel("External Distance")
    #
    # plt.subplot(313)
    # plt.plot(res3, 'b')
    # plt.xlabel("Topic Number")
    # plt.ylabel("Inner/External Distance")
    # plt.show()

    # print avePossValueL
    # ldaa(vCid, 7)





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
