import requests
from lxml import etree
import re
import time
import math
import csv
import random
from user_agent import get_uesr_agent#获取user_agent
from requests.adapters import HTTPAdapter#设置尝试次数


name_item = ["姓名","职位","行医地点","关键字","擅长","医生简介","医生评价(10为最高)","预约量","问诊量","图文问诊价格","视听问诊价格","url"]
ip_file = "C:\\Users\heave落色\PycharmProjects\\untitled1\ip.csv"


def get_proxy(file):#从IP池中获取IP
    proxys = []
    with open(file) as f:
        reader = csv.reader(f)
        for proxy in list(reader)[1:]:
            proxys.append(proxy)
    random.seed()
    random_num = random.randint(0,len(proxys)-1)
    return proxys[random_num]


def download(url,try_time=0,proxystart="no"):#下载器
    if proxystart == "no":
        proxy = get_proxy(ip_file)
        proxies = {}.fromkeys(["http", "https"], f"{proxy[0]}:{proxy[1]}")
        proxies = {'http': '1.194.142.102:808', 'https': '1.194.142.102:808'}
    else:
        proxies = None
    data = {"User-Agent": f"{get_uesr_agent()}"}
    time.sleep(1)
    r = requests.Session()
    try:
        if proxystart != "yes":
            res = r.post(url,data=data)
        elif proxystart == "yes":
            res = r.post(url,proxies=proxies,data=data)
    except:
        if try_time < 3:
            try_time += 1
            if proxystart == "no":
                download(url, try_time=try_time)
            else:
                download(url,try_time=try_time,proxystart="no")
        return "下载失败"
    return res

def secend_url(url):#列表页链接
    item2 = []
    res = download(url)
    if res == "下载失败":
        return res
    html = res.text
    regex = '<strong id="J_ResultNum"> (.*) </strong>'
    num = re.findall(regex, html)
    page = int(num[0]) / 16
    num = math.ceil(page)
    for p in range(1, num + 1):
        doctor_url = url.rsplit(url.split("&")[-1])[0] + "pageNo=" + str(p)#列表页链接
        item2.append(doctor_url)
    return item2


def doctor_url(url):#医生链接
    item3 = []
    res = download(url)
    if res == "下载失败":
        return res
    selector = etree.HTML(res.text)
    infos = selector.xpath('//li[@class="g-doctor-item"]/div[@class="wrap"]/a|//li[@class="g-doctor-item last"]/div[@class="wrap"]/a')
    for info in infos:
        item3.append(info.attrib["href"])
    return item3


def doctor_line(url):#医生详情
    item4 = []
    res = download(url)
    if res == "下载失败":
        print(res)
        return res
    selector = etree.HTML(res.text)
    name = selector.xpath('//div[@class="detail word-break"]/h1/strong[@class="J_ExpertName"]')[0].text#姓名
    item4.append(name)
    if selector.xpath('//div[@class="detail word-break"]/h1/span'):
        position = ""
        for info in selector.xpath('//div[@class="detail word-break"]/h1/span'):
            position += info.text.lstrip().rstrip()#职位
    else:
        position = None
    item4.append(position)
    if selector.xpath('//div[@class="detail word-break"]/div[@id="card-hospital"]/p'):
        hospitals = ""
        for info in selector.xpath('//div[@class="detail word-break"]/div[@id="card-hospital"]/p'):
            hospital = ""
            for info in info.xpath('a|span'):
                hospital += info.text.lstrip().rstrip()
            hospitals += hospital + "/ "
    else:
        hospitals = None
    item4.append(hospitals.rstrip(" / "))
    if selector.xpath('//div[@class="detail word-break"]/div[@class="keys"]/a'):
        keys = ""
        for key in selector.xpath('//div[@class="keys"]/a'):
            keys += key.text.lstrip().rstrip() + " / "#关键字
    else:
        keys = None
    item4.append(keys)
    if selector.xpath('//div[@class="detail word-break"]/div[@class="goodat"]/a'):
        goodat = selector.xpath('//div[@class="detail word-break"]/div[@class="goodat"]/a')[0].attrib["data-description"]#擅长
    else:
        goodat = None
    item4.append(goodat)
    if selector.xpath('//div[@class="detail word-break"]/div[@class="about"]/a'):
        about = selector.xpath('//div[@class="detail word-break"]/div[@class="about"]/a')[0].attrib["data-description"]#医生简介
    else:
        about = None
    item4.append(about)
    if selector.xpath('//div[@class="status"]/div[@class="data"]//strong'):
        evaluate = selector.xpath('//div[@class="status"]/div[@class="data"]//strong')[0].text#医生评价
    else:
        evaluate = None
    item4.append(evaluate)
    if selector.xpath('//div[@class="status"]/div[@class="data"]//strong'):
        nr = selector.xpath('//div[@class="status"]/div[@class="data"]//strong')[1].text#预约量
    else:
        nr = None
    item4.append(nr)
    if selector.xpath('//div[@class="status"]/div[@class="data"]//strong'):
        ni = selector.xpath('//div[@class="status"]/div[@class="data"]//strong')[2].text#问诊量
    else:
        ni = None
    item4.append(ni)
    if selector.xpath('//div[@class="consult-type"]/ul/li[1]//p[@class="current-price"]'):
        tit = selector.xpath('//div[@class="consult-type"]/ul/li[1]//p[@class="current-price"]')[0].text#图文问诊价格
    else:
        tit = None
    item4.append(tit)
    if selector.xpath('//div[@class="consult-type"]/ul/li[2]//p[@class="current-price"]'):
        shihua = selector.xpath('//div[@class="consult-type"]/ul/li[2]//p[@class="current-price"]')[0].text#视听问诊价格
    else:
        shihua = None
    item4.append(shihua)
    item4.append(url)

    print("++++++++++++++++++完成一项")
    return item4




def join_csv(item,value):
    filename = "smalldoctor_" + value + ".csv"
    with open(filename,"a",encoding='gbk',newline="") as f:
        writer = csv.writer(f)
        try:
            writer.writerow(item)
        except UnicodeEncodeError:
            item_new = []
            item_new.append(item[0])
            item_new.append(item[-1])
            writer.writerow(item_new)


def mian(starurl,value):
    for url2 in secend_url(starturl):
        if url2 == None:
            pass
        for url3 in doctor_url(url2):
            if url3 == None:
                pass
            item = doctor_line(url3)
            join_csv(item,value)


starturls = {"https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f67b77e-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E5%A4%96%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"surgery",#外壳
            "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f640bba-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E5%86%85%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"medicine",#内科
           "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f6802e2-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E5%84%BF%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"children",#儿科,
            "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f68c1d2-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E4%B8%AD%E5%8C%BB%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"Chinese Medicine",#中医
            "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f688f14-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E7%9A%AE%E8%82%A4%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"skin",#皮肤科
            "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f67dd62-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E9%AA%A8%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"bone",#骨科
            "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f6866c4-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E8%80%B3%E9%BC%BB%E5%92%BD%E5%96%89%E5%A4%B4%E9%A2%88%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"Otorhinolaryngology",#耳鼻喉科
            "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f69043a-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E5%85%B6%E4%BB%96%E7%A7%91%E5%AE%A4&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"other",#其他
            "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f67f180-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E5%A6%87%E4%BA%A7%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0":"Women"#妇科
             }



for starturl,value in starturls.items():
    filename = "smalldoctor_" + value + ".csv"
    with open(filename,"w",newline="")  as f:
        writer = csv.writer(f)
        writer.writerow(name_item)
    mian(starturl,value)


















