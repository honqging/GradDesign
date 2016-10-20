# encoding: utf-8
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.cElementTree as ET
import time

tree = ET.parse("5920429.xml")
root = tree.getroot()

# for child in root:
#     print child.tag

for elem in tree.iter(tag = "d"):
    pDataList = elem.attrib['p'].split(',')
    danmuDate = time.localtime(float(pDataList[4]))
    danmuDate2 = time.strftime("%Y-%m-%d %H:%M:%S", danmuDate)
    print elem.text, pDataList[0], danmuDate2

print "-----------字幕解析完毕------------"
