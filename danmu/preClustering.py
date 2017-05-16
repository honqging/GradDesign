    # encoding:utf8
import requests
from bs4 import BeautifulSoup
import time
import json as js

import xmlDL

favBoxUrl = 'http://space.bilibili.com/ajax/fav/getBoxList'
favListUrl = 'http://space.bilibili.com/ajax/fav/getList'

# check if a user has fav part, fav_videos > 0
settingUrl = 'http://space.bilibili.com/ajax/settings/getSettings'

# get all video types of a user 'userId'
def getVType(userId):
    favBoxParams = {'mid': userId, '_': str(time.time())}

    # check if a user has fav part, fav_videos > 0
    rSetting = requests.get(settingUrl, params = favBoxParams)
    print rSetting.url
    if rSetting.status_code == 200:
        setJson = js.loads(rSetting.text)
        if setJson['status'] == False:
            return
        elif setJson['data']['privacy']['fav_video'] == 0:
            return

    r = requests.get(favBoxUrl, params = favBoxParams)
    # print r.url
    if r.status_code == 200:
        jsonDoc = js.loads(r.text)
        if jsonDoc['status'] == True:
            favBoxList = jsonDoc['data']['list']
            favTagss = []
            for i in favBoxList:
                print '--------box', favBoxList.index(i), '--------'
                reFavList = getFavList(userId, i['fav_box'])
                if type(reFavList) == list:
                    # for i in reFavList:
                    #     print i,
                    favTagss.extend(reFavList)
            return favTagss
        else:
            print userId, 'this user does not have favorite box....'
    else:
        print "unable to access..."

# get all videos under the fav_box 'favBoxId'
def getFavList(userId, favBoxId):
    favListParams = {'mid': userId, 'pagesize': '30', 'fid': favBoxId, '_': str(time.time())}
    r = requests.get(favListUrl, params = favListParams)
    # print r.url

    if r.status_code == 200:
        jsonDoc = js.loads(r.text)

        if jsonDoc['status'] == False:
            return

        # all fav_videos tags list
        favTags = []

        # get tags & number of these tags in this box
        favListParams = {'mid': userId, 'pagesize': '30', 'fid': favBoxId, '_': str(time.time())}
        r = requests.get(favListUrl, params = favListParams)
        jsonDoc = js.loads(r.text)
        if jsonDoc['status'] == True:
            # if jsonDoc[]
            favList = jsonDoc['data']['tlist']
            if favList is not None:
                for j in favList:
                    # print j['tname'].encode('utf-8')
                    favTags.extend([j['name'].encode('utf-8'), str(j['count'])])
                return favTags
        else:
            print 'no video in this box for page...'
    else:
        print 'unable to access...'

# return a list: user list
def readUsers(userTxt):
    userList = []

    # read all userId from file: userTxt, and return it
    with open(userTxt) as f:
        for i in f.readlines():
            userId = i.rstrip('\n').split(',')[1]

            # append userId which is able to be hashed...
            if userId != 'None':
                userList.append(userId)
        return userList

# write user fav tags to file: favTagFile
def writeFavTags(userTxtFile, favTagFile):
    userList = readUsers(userTxtFile)
    fo = open(favTagFile, 'w')
    for user in userList:
        if userList.index(user) < userList.index('847278'):
            continue

        userFavTagSet = getVType(user)
        # print user, userFavTagSet

        if userFavTagSet == None:
            continue

        fo.write(user)
        fo.write(',')
        for i in userFavTagSet:
            # print i
            fo.write(i)
            fo.write(',')
        fo.write('\n')
    fo.close()
    print "reading file ", userTxt, "finished, writen to ", favTagFile

# get all types of videos in the favTagFile
# print '音乐 生活 科技 番剧 电影 时尚 舞蹈 公告 游戏 鬼畜 广告 电视剧 动画 娱乐'
def analyFavTags(favTagFile):
    userFavTagList = []
    # userFavTag = []

    with open(favTagFile) as f:
        for i in f.readlines():
            iList = i.rstrip(',\n').split(',')
            userFavTagList.extend(iList[1::2])
    print type(userFavTagList), userFavTagList[1]
    a = list(set(userFavTagList))
    print len(a)
    for i in a:
        print i,

if __name__ == '__main__':
    userId = '24459450'
    vCid = xmlDL.vCid
    userTxt = 'data/users/' + vCid + '/userIdList.txt'

    # getFavList(userId, favBoxId)

    # print readUsers(userTxt)

    favTagFile = 'data/users/' + vCid + '/favTagTList4.txt'
    writeFavTags(userTxt, favTagFile)

    # used to analyze favTag1.txt
    tFav = 'favTagTlist1.txt'
    # analyFavTags(tFav)
