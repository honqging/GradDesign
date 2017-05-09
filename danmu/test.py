# encoding: utf-8

# import jieba
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import KMeans
import scipy.cluster.hierarchy as hcluster
import time
import numpy.random as random
import numpy.core.fromnumeric
import jieba
import util




text = "他来到了网易杭研大厦"
# "小明硕士毕业于中国科学院计算所",
# "后在日本京都大学深造"]

def irisSample():
    iris=datasets.load_iris()
    irisdata=iris.data
    result=hcluster.fclusterdata(irisdata, criterion='maxclust',t=3)
    print("result is %s" % result)

def gaussianSample():
    timeCheckin=time.clock()
    X=random.randn(100,100)
    X[:50,:100]+=10
    result=hcluster.fclusterdata(X, criterion='maxclust',t=3)
    print("hierachical clustering on sample with shape(%d,%d) cost %s seconds " % (np.shape(X)[0],np.shape(X)[1],time.clock()-timeCheckin))
    print("result is %s" % result)
    clusterA=[label for label in result if(label==1)]
    clusterB=[label for label in result if(label==2)]
    print("There are %d samples in cluster 1" %(len(clusterA)))
    print("ClusterA is %s" % clusterA)
    print("There are %d samples in cluster 2" %(len(clusterB)))
    print("ClusterB is %s" % clusterB)

def write2file():
    fo = open('test.txt', 'w')
    fo.write("hahah" + '23333')

def getMax(a):
    b = []
    b = [i[1] for i in a]
    print b.index(max(b)), max(b),
        # b.i[1]

def getTest(input):
    return

if __name__ == "__main__":
    a = [(0, 0.088614310538297464), (1, 0.016160363049208325), (2, 0.016160540373025278), (3, 0.016160485641323257), (4, 0.016160371990146048), (5, 0.016160359902167829), (6, 0.016160376152101166), (7, 0.16273735720778679), (8, 0.016160360277401961), (9, 0.13198984036418515), (10, 0.14514823415439301), (11, 0.10420287658203534), (12, 0.016160378450192758), (13, 0.12430757128876919), (14, 0.11371657402896627)]
    # getMax(a)

    l = [['a', 'b'],
        ['c', 'd'],
        ['e', 'f'],
        ['g', 'h']]

    print np.transpose(l)
    print np.transpose(np.transpose(l))

    a = ['a','b','c','d','e']
    b = ['f','g','h','d','e']

    # list2d = [125.  126.   83.   18.  121.   44.   72.    0.  108.  113.   46.   66.  114.    0.  109.],
    #             # [ 799.  785.  558.  141.  737.  286.  425.    2.  659.  611.  376.  460.  765.    0.  657.],
    #             # [ 308.  321.  238.   48.  272.  116.  162.    0.  259.  236.  135.  173.  284.    1.  267.],
    #             # [ 557.  540.  378.   99.  490.  215.  315.    0.  457.  424.  232.  295.  514.    0.  449.],
    #             # [ 537.  535.  361.   86.  477.  176.  293.    0.  463.  416.  234.  297.  509.    0.  444.]]

    list2d = [[ 530,  521,  361,   92,  450,  190,  287,    1,  444,  424,  235,  278,  502,    0,  420],
             [ 369,  370,  276,   60,  345,  133,  207,    1,  319,  274,  163,  214,  347,    0,  307],
             [ 936,  911,  624,  151,  836,  344,  491,    0,  753,  716,  415,  519,  868,    1,  764],
             [ 156,  162,  116,   29,  153,   52,   78,    0,  135,  128,   72,   89,  148,    0,  139],
             [ 152,  157,  117,   28,  142,   55,  104,    0,  133,  119,   76,   99,  146,    0,  134],
             [ 183,  186,  124,   32,  171,   63,  100,    0,  162,  139,   62,   92,  175,    0,  162]]
    array2d = np.loadtxt('topicDist.txt')
    array3 = np.sum(array2d, axis=1)
    # array3.shape = (5, 1)

    array4 = np.transpose(np.transpose(array2d) / np.float16(array3))

    # array4 = np.loadtxt('topicDist.txt')
    colorList = ['b', 'c', 'g', 'k', 'm', 'r', 'y'] # do not use white 'w'
    for i in range(len(array4)):
        plt.plot(array4[i], colorList[i])
    plt.show()





    print array3.shape, array3
    # save 3 digits behind every element
    print np.around(array4, 3)

    # 音乐 动画 番剧 广告 电影 时尚 舞蹈 公告 游戏 鬼畜 娱乐 电视剧 生活 活动 科技
    listt = ['音乐', '游戏', '鬼畜', '动画', '电影', '舞蹈', '电影', '舞蹈', '游戏', '鬼畜', '动画', '音乐', '生活', '番剧', '电影', '舞蹈', '游戏', '鬼畜', '动画']
    for i in list(set(listt)):
        print i

    # 0.005*"第一次" + 0.005*"存活" + 0.004*"确认" + 0.004*"买" + 0.004*"站" + 0.003*"合影" + 0.003*"合影留念" + 0.003*"b" + 0.003*"微信" + 0.003*"零钱"
    # 0.003*"湫" + 0.003*"椿" + 0.002*"啊" + 0.002*"看" + 0.002*"在" + 0.002*"鲲" + 0.002*"不" + 0.002*"这" + 0.002*"有" + 0.002*"一个"
    # 0.002*"哎" + 0.002*"马化腾" + 0.002*"啊" + 0.002*"好" + 0.001*"秋水共长天一色" + 0.001*"生日" + 0.001*"MC" + 0.001*"湫" + 0.001*"人间" + 0.001*"对"
    # 0.002*"湫" + 0.002*"合影" + 0.002*"第一次" + 0.002*"支持" + 0.002*"裙子" + 0.002*"哪来" + 0.001*"啊" + 0.001*"好" + 0.001*"如果" + 0.001*"吗"
    # 0.007*"钱" + 0.007*"撒花" + 0.007*"完结" + 0.007*"没" + 0.006*"合影" + 0.004*"再见" + 0.003*"存活" + 0.003*"第一次" + 0.002*"确认" + 0.002*"买"
    # 0.002*"湫" + 0.002*"看到" + 0.002*"合影" + 0.002*"鲲" + 0.002*"椿" + 0.002*"视角" + 0.002*"看" + 0.001*"鱼" + 0.001*"不" + 0.001*"在"
    prob2dArray = [  [  3.7440,   1.2835,   3.2390,   1.1254,  7.5262,   2.3359,   3.5794,   8.7000,  7.4656,   6.1946,   4.3196,   2.4171,  6.2247,   1.3800,   8.9698],
                     [  3.2082,   1.1564,   3.6976,   1.2768,  8.0271,   2.5412,   3.5762,   0.0000,  7.5487,   5.9024,   4.6815,   2.5180,  6.2952,   0.0000,   8.3609],
                     [  1.4040,   4.7956,   1.4518,   3.3760,  3.6167,   6.5280,   1.5437,   0.0000,  3.0837,   2.5249,   1.6908,   9.4300,  2.3798,   0.0000,   3.9756],
                     [  1.3697,   5.4225,   1.4597,   4.6150,  3.6184,   9.7730,   1.6857,   0.0000,  3.3248,   2.4641,   2.1500,   1.0384,  2.9482,   0.0000,   4.2787],
                     [  3.2491,   1.0571,   3.3533,   1.1667,  6.1006,   1.8315,   3.2082,   1.7400,  6.9260,   5.6342,   3.4192,   1.9053,  6.3402,   0.0000,   8.4762],
                     [  1.5550,   5.6824,   1.5600,   5.7980,  4.5378,   8.6020,   1.9494,   0.0000,  4.1507,   3.0612,   2.3600,   9.4410,  3.0068,   0.0000,   4.2531]]
    prob2dArray = np.array(prob2dArray)
    # np.savetxt('temp.txt', prob2dArray)

    prob2dArray = np.loadtxt('topicPercDist.txt')

    colorList = ['b', 'c', 'g', 'k', 'm', 'r', 'y'] # do not use white 'w'
    # print type(prob2dArray)
    for i in range(len(prob2dArray)):
        plt.plot(prob2dArray[i], colorList[i])
    plt.show()


    topicNumList = range(5)
    aTopicNewUniBContentListString = []
    for i in topicNumList:
        aTopicNewUniBContentListString.append([])
    print aTopicNewUniBContentListString, type(aTopicNewUniBContentListString[1])





    start = time.time()
    # np.savetxt('test.txt', l)
    end = time.time()

    print 'cost', end - start, 'seconds to calculate the matrix.'
