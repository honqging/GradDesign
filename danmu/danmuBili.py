# encoding: utf-8

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.cElementTree as ET
import time
import jieba

tree = ET.parse("5920429.xml")
root = tree.getroot()

# for child in root:
#     print child.tag

lists = []

for elem in tree.iter(tag = "d"):
    pDataList = elem.attrib['p'].split(',')
    danmuDate = time.localtime(float(pDataList[4]))
    danmuDate2 = time.strftime("%Y-%m-%d %H:%M:%S", danmuDate)
    # print elem.text, pDataList[0], danmuDate2
    
    # generator
    # seg_list = jieba.cut(elem.text, cut_all=False)
    # print type(seg_list)

    # list
    if elem.text == '':
	continue
    seg_list = jieba.lcut(elem.text, cut_all=False)   
    # lists.append(seg_list)
    print len(seg_list), max(seg_list), type(elem.text)
    

print len(lists)
print "-----字幕解析完毕-----"

