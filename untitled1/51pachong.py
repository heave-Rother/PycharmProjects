from urllib.request import urlopen,Request,build_opener,install_opener,ProxyHandler
from urllib.error import URLError,HTTPError
from urllib.parse import urlparse#用于对url进行分析
import re
from bs4 import BeautifulSoup
from lxml import etree
import csv



FLS = ["职位","职位描述","薪资","福利","招收人数","学历","经验","地址","链接"]

def download(url,proxy=None,User_agent="Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",num_retries=0,timeout=8):
    """下载器"""
    headers = {"User agent":User_agent}#用户代理
    requests = Request(url,headers=headers)#在向urlopen传递信息时使用.
    opener = build_opener()
    print("download.........[+]" + url)


    if proxy:
        res = urlparse(proxy)
        protocol = res.scheme
        ip = res.netloc  # 将新的ip代理解析

        handler = ProxyHandler({protocol: ip})
        opener.add_handler(handler)  # 创建一个新的打开方式，并将IP代理导入。

        install_opener(opener)  # 将该打开方式应用全局
        try:
            html = opener.open(requests,timeout=timeout).read()
        except URLError as e:
            if hasattr(e, "code") and 500 <= e.code <= 600:
                print(e)
                html = None
                if num_retries < 2:
                    num_retries += 1
                    print("try to %d times" % num_retries)
                    download(url, User_agent="heave",proxy=new_ip,num_retries=num_retries,timeout=1)
            print(e)
            html = None
        return html


    try:
        print()
        html = urlopen(requests,timeout=timeout).read().decode()
    except HTTPError or URLError as e:
        if hasattr(e,"code") and 500 <=e.code<= 600:
            print(e)
            html = None
            if num_retries < 2:
                num_retries += 1
                print("try to %d times" % num_retries)
                download(url, User_agent="heave",num_retries=num_retries)
        print(e)
        html = None
    return html

bs4_lines = []
def bs4_get_lines(html):
    """用bs4得到职位列表"""

    bs4_object = BeautifulSoup(html,"html.parser")
    for line in bs4_object.find("ul",id="list_con").find_all("li"):
        url_line = line.a["href"]
        bs4_lines.append(url_line)
    if bs4_object.find("a",class_="next",herf=""):
        next_page = bs4_object.find("a",class_="next")["href"]
        html = download(next_page)
        bs4_get_lines(html)
    return bs4_lines


re_lines = []
def re_get_lines(html):
    """用re得到职位列表"""
    regex = re.compile('__addition="0"><a href="(http://.*?[\d]{36}_[\d]{27})".*?tongji_label="listclick"')

    for line in re.findall(regex,html):
        re_lines.append(line)
    bs4_object = BeautifulSoup(html, "html.parser")
    if bs4_object.find("a",class_="next",herf=""):
        next_page = bs4_object.find("a",class_="next")["href"]
        print(next_page)
        html = download(next_page)
        re_get_lines(html)
    return re_lines



lxml_lines = []
def lxml_get_lines(html):
    """用lxml得到职位列表"""
    html = etree.HTML(html.lower())
    for line in html.xpath("//a[@tongji_label='listclick']"):
        line = line.attrib["href"]
        lxml_lines.append(line)
    if html.xpath('//a[@class="next"]'):
        next_page = html.xpath('//a[@class="next"]')#返回一个列表，即使是一个也是列表
        print(next_page[0].attrib["href"])
        html = download(next_page[0].attrib["href"])
        lxml_get_lines(html)
    return lxml_lines


def job(all_lines):
    """得到职位详情"""
    #with open("58jib.csv", a) as filename:
    for line in all_lines:
        html = download(line)
        bs4_object = BeautifulSoup(html,"html.parser")
        a =  bs4_object.find("span",class_="pos_title").get_text()#职位
        a = a.lstrip()
        b =  bs4_object.find("span",class_="pos_name").get_text()#职位描述
        b = b.lstrip()
        c= bs4_object.find("span", class_="pos_salary").get_text()#薪资
        c = c.lstrip()
        d = ""
        if bs4_object.find("div",class_="pos_welfare"):#福利，第十一个没有福利
            for key in bs4_object.find("div",class_="pos_welfare").find_all("span"):#福利
                d = d + "," + key.get_text()
            d = d[1:]
            d = d.lstrip()
        e = []
        for key in bs4_object.find("div",class_="pos_base_condition").find_all("span"):#福利
            e.append(key.get_text())
        e_1 = e[0].lstrip()
        e_2 = e[1].lstrip()
        e_3 = e[2].lstrip()
        f = ""
        f = bs4_object.find("div", class_="pos-area").find("span",class_=None).get_text()
        f = f.lstrip()
        H = []
        H.append(a)
        H.append(b)
        H.append(c)
        if d:
            H.append(d)
        H.append(e_1)
        H.append(e_2)
        H.append(e_3)
        H.append(f)
        H.append(line)

        job_d = dict(zip(FLS,H))
        for key,value in job_d.items():
            print(key + ":" + value)








#url = "https://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E8%A5%BF%E5%AE%89&kw=java&p=1"
#url = "http://jobs.zhaopin.com/514689632250727.htm?ssidkey=y&ss=201&ff=03&sg=273e313ecea74ac9b3d9852465c22946&so=1"
url = "http://jz.58.com/canguan/?utm_source=link&spm=u-LscBIm_2J9tMeMj.psy_110&PGTID=0d202408-0229-6944-ffd4-082fbafae699&ClickID=1"

class ZhiXing():
    """爬虫功能的集成"""
    def __init__(self,home_url,get_lines):
        self.home_url = home_url
        self.get_lines = get_lines


    def re_paqu(self):
        html = download(self.home_url)
        all_lines = (self.get_lines(html))
        if self.get_lines == re_get_lines:
            all_lines = all_lines[1:]
        job(all_lines)



c = ZhiXing(url,re_get_lines)
c.re_paqu()


#本代码的扩展：
    # 1：sleep_time
    # 2：将文件保存为csv格式
    # 3：起请求时间