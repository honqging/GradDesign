# encoding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn import datasets
from sklearn.cluster import KMeans
import time

favTagTlist = ["favTagTlist1.txt", "favTagTlist2.txt", "favTagTlist3.txt", "favTagTlist4.txt"]

# get a single line of tag data of userId
# userId: user0
# return: [ 1.  1.  1. ...,  1.  0.  1.]
def getTagLineOfUser(tagMatrix, tagVNumMatrix, userList, userId):
    if userId in userList:
        userIndex = userList.index(userId)

        # eg: [ 1.  1.  1. ...,  1.  0.  1.]
        tagLine = tagMatrix[userIndex]
        tagVNumLine = tagVNumMatrix[userIndex]
        return tagLine, tagVNumLine
    else:
        return

# return the 2d arrayMatrix and its related userList
# [[ 1.  1.  1. ...,  1.  0.  1.] user0
#  [ 1.  0.  1. ...,  0.  0.  1.] user1....
#  [ 1.  1.  1. ...,  1.  0.  1.]
#  ...,
#  [ 0.  1.  0. ...,  0.  0.  1.]
#  [ 1.  1.  0. ...,  1.  0.  0.]
#  [ 1.  1.  1. ...,  1.  0.  0.]]
#
# len(userList) == shape(arrayMatrix)[0]
def scanAllTags(favTagTlist):
    userFavTagList = []
    userFavTagVNumList = []
    userList = []
    catAll = []
    for i in favTagTlist:
        with open(i) as f:
            for j in f.readlines():
                line = j.rstrip(',\n')
                tagList = line.split(',')

                # user no tags, ignore
                if len(tagList) == 1:
                    continue
                # eg: [音乐, 生活, 番剧, 电影, 舞蹈, 游戏, 鬼畜, 动画]
                uniTagList = list(set(tagList[1::2]))
                uniTagVNumList = []

                # the number of videos about a tag(eg: 电影: 10)
                # eg: [10, 123, 23, 15, 23, 22, 222, 21]
                uniTagVNum = 0
                for tag in uniTagList:
                    tagIList = [i for i, v in enumerate(tagList) if v == tag]
                    for index in tagIList:
                        uniTagVNum += int(tagList[index + 1])
                    uniTagVNumList.append(uniTagVNum)
                # print len(uniTagList), uniTagVNumList

                userFavTagList.append(uniTagList)
                userFavTagVNumList.append(uniTagVNumList)
                # userFavTagList.append(uniTagListAndU)
                userList.append(tagList[0])
                catAll.extend(uniTagList)

    tagMatrix, tagVNumMatrix = getArrayMatrix(userFavTagList, userFavTagVNumList, list(set(catAll)))

    # print arrayMatrix
    # print arrayMatrix.shape
    # print len(userFavTagList), len(set(catAll)), len(userList)

    return tagMatrix, tagVNumMatrix, userList, list(set(catAll))

# return 2 params, 1st represents if the tag exist, 2nd represents the number of videos about the tag
def getArrayMatrix(listMatrix, userFavTagVNumList, catList):
    tRow = len(listMatrix)
    tColomn = len(catList)

    tagMatrix = np.zeros((tRow, tColomn))
    tagVNumMatrix = np.zeros((tRow, tColomn))

    for i in range(tRow):
        for j in listMatrix[i]:
            if j in catList:
                tagMatrix[i, catList.index(j)] = 1
                tagVNumMatrix[i, catList.index(j)] = userFavTagVNumList[i][listMatrix[i].index(j)]
    return tagMatrix, tagVNumMatrix

if __name__ == "__main__":
    start = time.time()
    tagMatrix, tagVNumMatrix, userList, catAll = scanAllTags(favTagTlist)


    print tagMatrix, '\n', tagVNumMatrix, tagMatrix.shape, tagVNumMatrix.shape

    end = time.time()
    print 'cost', end - start, 'seconds --------------'
