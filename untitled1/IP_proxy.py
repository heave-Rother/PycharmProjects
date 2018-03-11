"""建立一个IP代理池"""
import requests
from lxml import etree
import csv
import time
import subprocess as sp
import re


def fetch(url,proxy=None):
    """模拟浏览器打开网页"""
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:58.0) Gecko/20100101 Firefox/58.0",
        "Refere":"http://www.xicidaili.com/nn"
    }
    s.headers.update(headers)
    proxies = {}.fromkeys(["http","https"],f"{proxy[0]}:{proxy[1]}")if proxy else None#当proxy(即用户代理)不为None时，创建一个字典包含两个元素，分别以"http","https"为键。
                                                                                      #proxy[0]为IP,proxy[1]为端口
    return s.get(url,timeout=8,proxies=proxies,headers=headers).text


def get_data(homeurl,pagename):
    """爬取代理服务器的地址"""
    all_ip = {}
    for i in range(1,pagename+1):
        r = fetch(homeurl + str(i))
        html = etree.HTML(r)
        for tr in html.xpath('//table[@id="ip_list"]/tr[@class="odd"]|//table[@id="ip_list"]/tr[@class=""]'):
            tds = tr.xpath('td')
            all_ip[tds[1].text] = tds[2].text
    print(len(all_ip))
    return all_ip
# #-----------------------------------------------------------------------以上完成爬虫任务-----------------------------------------------------------------------------

def check(target_url,ip,port):
    """对IP地址的可用性进行检查----打开网页的方式"""
    proxy = []
    proxy.append(ip)
    proxy.append(port)
    try:
        fetch(target_url,proxy)
    except :
        print("此ip不可用")
        return None
    else:
        print("IP:  " + ip + ":" + port + "可用")
        return ip




def join_file(ipanport):
    """将可用的IP放入一个csv文件中"""
    with open("ip.csv","a+",newline="") as file:
        writer = csv.writer(file)
        writer.writerow(ipandport)












homeurl = "http://www.xicidaili.com/nn/"
target_url = "https://www.guahao.com/search/expert?iSq=1&standardDepartmentId=7f67f180-cff3-11e1-831f-5cf9dd2e7135&standardDepartmentName=%E5%A6%87%E4%BA%A7%E7%A7%91&consult=2&p=%E5%85%A8%E5%9B%BD&fg=1&sort=0"
pagename = 20
namelist = ["ip","port"]
with open("ip.csv","w",newline="") as f:
    writer = csv.writer(f)
    writer.writerow(namelist)
for ip,port in get_data(homeurl,pagename).items():
    canip = check(target_url,ip,port)
    if canip != None:
        ipandport = []
        ipandport.append(ip)
        ipandport.append(port)
        join_file(ipandport)



















