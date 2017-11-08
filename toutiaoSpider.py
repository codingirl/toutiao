# -*- coding:utf-8 -*-
from toutiao.config import *
import requests
import re
import json
import os


headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X)\
         AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'}

def initUrl(offset):
    outUrl='https://m.toutiao.com/search_content/?offset='+str(offset)+'&count=10&from=search_tab&keyword='+KEYWORD
    return outUrl

#step1 从关键字网页里得到每一个图集的URL，返回图集链接集合
def getInnerUrlFromOutUrl(outurl):
    resp=requests.get(outurl,headers=headers)
    content=resp.content.decode()
    dictObj=json.loads(content)
    p=re.compile('href=\\"/group/(.*?)\\"')
    arr=p.findall(dictObj["html"])
    newArr=['https://m.toutiao.com/i'+item+'info/' for item in arr]
    # print(len(arr))
    # print(newArr)
    return newArr

#step2 得到图集里面每一张图片的URL,返回图片链接集合以及图片名称
def getImagesUrl(innerUrl):
    rp = requests.get(innerUrl, headers)
    rpContent = rp.content.decode()
    contentDict = json.loads(rpContent)['data']['content']
    pt2 = re.compile('src="(.*?)"')
    imgUrlArr = pt2.findall(contentDict)
    tujiName=re.findall('alt="(.*?)"',contentDict)[0]
    return imgUrlArr,tujiName

#step3 下载图片
def download_image(url):
    print('Downloading', url)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.content
            # save_image(response.content)
    except ConnectionError as e:
        print(e.args)
        return None

#step4 保存
def save_image(content,tujiName,i):
    file_path='/{0}/{1}.{2}'.format(os.getcwd()+'/'+tujiName,i,'jpg')
    print(file_path)

    if not os.path.exists(tujiName):
        os.mkdir(tujiName)
    else:
        if type(content) != None:
            with open(file_path, 'wb') as f:
                f.write(content)


def runOnePage(url):
    # 先测试走一波
    tujiUrlArr = getInnerUrlFromOutUrl(url)
    count = 0
    for tujiUrl in tujiUrlArr:
        imagesUrlArr, tuJiName = getImagesUrl(tujiUrl)
        # print(imagesUrlArr)
        # print(tuJiName)
        # print('该图集一共有'+str(len(imagesUrlArr))+'张图片')
        count += len(imagesUrlArr)
        i = 0
        for imgUrl in imagesUrlArr:
            imgCont = download_image(imgUrl)
            save_image(imgCont, tuJiName, str(i))
            i += 1
    print('这一页共得到这么多图片：', str(count))
    return count


if __name__ == '__main__':
    pageCount = 0
    for offset in range(0,13):
        pageUrl=initUrl(offset*10)
        pageCount+=runOnePage(pageUrl)

    print('一共多少图片：'+str(pageCount))
