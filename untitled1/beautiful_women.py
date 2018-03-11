import requests
import re
from bs4 import BeautifulSoup
from lxml import etree






headers = {"user_agent":"Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/58.0"}
proxies = {}
def download(url):
    """得到页面的html"""
    try:
        html = requests.get(url,params=None)
    except requests.RequestException as e:
        print(e)
        html = None
    html = html.content.decode("gbk")#对二进制数据解码
    return html






def get_list_urlandjpq(html):
    global page
    """获取列表页的图片(列表页不止一页，循环获取多页)且获取详情页的链接"""
    regex_1 = re.compile('src="(http://img1.*?\d+.jpg)"')
    regex_2 = re.compile("http://www.mm131.com/xiaohua/\d+.html")
    #列表页中的图片
    for jpq in re.findall(regex_1,html):
        all_jpq.add(jpq)
    #列表页中详情页的链接
    bs4_object = BeautifulSoup(html, "html.parser")
    for url in bs4_object.find("dl",class_="list-left public-box").find_all("a",href=regex_2):
        jpq_url.append(url["href"])

    #列表页中的下一页
    page += 1
    if re.search("list_2_" + str(page) + ".html",html):
        url = start_url + "/list_2_" + str(page) + ".html"#这是一个列表页
        html = download(url)
        get_list_urlandjpq(html)
    return jpq_url

def get_jpq(jpq_url):
    """获取详情页中的图片"""
    for url in jpq_url:
        html = download(url)
        #详情页本页的图片
        bs4_obj = BeautifulSoup(html,"html.parser")
        jpq = bs4_obj.find("div",class_="content-pic").img["src"]
        all_jpq.add(jpq)


        #详情页列表的图片
        regex_3 = re.compile("<a href='(.*?.html)' class=.*?>\d+</a>")
        for href in re.findall(regex_3,html):
            new_url = start_url + href
            html = download(new_url)
            bs4_obj = BeautifulSoup(html,"html.parser")
            jpq = bs4_obj.find("div", class_="content-pic").img["src"]
            all_jpq.add(jpq)
    return all_jpq











page = 1
all_jpq = set([])
jpq_url= []
def zhixing(stara_url):
    """执行"""
    global jpq_url
    start_html = download(start_url)
    get_list_urlandjpq(start_html)
    get_jpq(jpq_url)
    print(len(all_jpq))
    print((all_jpq))






start_url = "http://www.mm131.com/xiaohua/"
zhixing(start_url)


