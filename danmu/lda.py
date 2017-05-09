# encoding: utf-8

from gensim import corpora, models, similarities
import matplotlib.pyplot as plt
import time
import numpy as np

import xmlDL
import util
import clustering

userCodeIdListFilePath = "10506396Users.txt"
favTagTlist = ["favTagTlist1.txt", "favTagTlist2.txt", "favTagTlist3.txt", "favTagTlist4.txt"]


# return the topic type with max posibility and the posibility of a
# eg: a--[(0, 0.033333333333334041), (1, 0.033333333333659149), (2, 0.03333333333337106), (3, 0.033333333333336511), (4, 0.033333333333333631), (5, 0.033333333577374141), (6, 0.033333333333333381), (7, 0.53333330176939997), (8, 0.033333333641347308), (9, 0.033333333333333388), (10, 0.033333333333333409), (11, 0.033333358397907714), (12, 0.033333333333333381), (13, 0.033333333333333368), (14, 0.033333339280269603)]
def getMax(a):
    b = []
    b = [i[1] for i in a]
    return b.index(max(b)), max(b)

# return a length of unique users and their barrage
# return 2 arguments, userList and related barrageList
# eg: uniBContentList: ['user', ['b1', 'b2', 'b3']]
# eg: uniBContentListString: ['22ccd704', '\xe7\x88\xb7\xe7\x88\xb7QAQ']
def getUserAndBarrageList(barrageList):
    # duplicate users list
    dupUList = [barrage[6] for barrage in barrageList]
    uniUList = list(set(dupUList))

    print len(dupUList), len(uniUList)

    uniBContentList = []
    uniBContentListString = []

    # bNumPerUser[0]: the number of barrage comments of user 0
    bNumPerUser = []
    for user in uniUList:
        user2BList = [i for i, v in enumerate(dupUList) if v == user]
        bNumPerUser.append((user, len(user2BList)))

        bContentList = []
        for bContentIndex in user2BList:
            bContentList.append(barrageList[bContentIndex][-1])

        # 1st
        # all barrage comments sent by one user
        totalBofUser = ' '.join(bContentList)

        uniBContentList.append([user, bContentList])
        uniBContentListString.append([user, totalBofUser])

    # for i in range(len(uniUList)):
    #     print uniBContentList[i]
    return uniBContentList, uniBContentListString, bNumPerUser

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
    initial = 0
    initial2 = 0
    initial3 = 0

    # print len(set(bNumMoreUserL).intersection(set(uniBContentListString)))
    # print set(bNumMoreUserL).intersection(set(uniBContentListString))


    u1 = uniBContentListString[0:10000]
    u2 = uniBContentListString[10001:len(uniBContentListString)-1]
    for i in u1:
        try:
            if i[0] in bNumMoreUserL:
                continue
            else:
                # print i[0], i[1]
                uniBContentListString.remove(i)
        except:
            continue
    for i in u2:
        if i[0] in bNumMoreUserL:
            continue
        else:
            # print i[0], len(i[1]), i[1]
            uniBContentListString.remove(i)

    print len(uniBContentListString)
    # for i in uniBContentListString:
    #     print len(i[1]), i[1]
    #     if len(i[1]) < 3:
    #         print i
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
    bList = xmlDL.migrateBD(vCid)

    # eg: uniBContentList: ['user', ['b1', 'b2', 'b3']]
    # eg: uniBContentListString: ['22ccd704', '\xe7\x88\xb7\xe7\x88\xb7QAQ']
    uniBContentList, uniBContentListString, bNumPerUser = getUserAndBarrageList(bList)

    newUniBContentListString = removeBLessNum(uniBContentListString, bNumPerUser, 3)
    bContentList = xmlDL.divideSent(newUniBContentListString)

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
    print dic.num_docs, dic.num_pos, len(dic)

    # text corpus
    corpus = [dic.doc2bow(text) for text in bContentList]
    # print max(corpus)

    tfidf = models.TfidfModel(corpus)
    print tfidf, type(tfidf)
    example = [(0, 1), (2, 1)]
    print tfidf[example]
    for word, index in dic.token2id.iteritems():
        if index == 3 or index == 0:
            word = word.encode('utf-8')
            print word, index

    # calculate similarities
    # index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=topicNum)
    # sims = index[tfidf[example]]
    # print list(enumerate(sims))
    # print type(examSims)

    corpus_tfidf = tfidf[corpus]
    # for i in corpus_tfidf:
    #     print i


    lda = models.LdaModel(corpus_tfidf, id2word=dic, num_topics=topicNum)
    ldaOut = lda.print_topics(topicNum)

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
        print r

    print type(ldaOut[0])
    print type(ldaOut[1][1])

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

    topicPosi = []
    for topicId in range(topicNum):
        posiList = [i[1] for i in resList if i[0] == topicId]

        # average accuracy rate
        possi = sum(posiList)/len(posiList)
        topicPosi.append(possi)

    catNum = 15

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
    userCodeIdList = util.getUserCodeIdList(userCodeIdListFilePath)
    # for i in userCodeIdList:
    #     print i

    tagMatrix, tagVNumMatrix, userList, catAll = clustering.scanAllTags(favTagTlist)

    # topic index list: [0, 1, 2, 3, 4]
    topicNumList = range(topicNum)
    aTopicNewUniBContentListString = []
    topicUserNumList = [0, 0, 0, 0]
    for i in topicNumList:
        aTopicNewUniBContentListString.append([])
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
        bContentList = xmlDL.divideSent(aTopicNewUniBContentListString[i])
        wordList = getMostWord(bContentList, 20)
        for j in wordList:
            print j[0], j[1]
        print type(aTopicNewUniBContentListString[i])
        for j in aTopicNewUniBContentListString[i]:
            print j[0], j[1]
        print '-------------------------'

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



if __name__ == '__main__':
    start = time.time()

    vCid = "10506396"
    # for i in range(3, 7):
    #     ldaa(vCid, i)
    ldaa(vCid, 4)


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
