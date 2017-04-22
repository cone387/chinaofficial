#encoding=utf-8

import sys
sys.path.append("H://relax")

import json
import time
import os
from bs4 import BeautifulSoup
from WebManager import get_html
from ManInfoRobot import ManInfoRobot


#主页面上有所有的省份信息，每个省份上有各省的人物信息
#所以有入如下步骤：
#1、获取已存在的人物信息
#2、抓取所有省份连接
#3、抓取所有省份对应的人物信息
#4、抓取到的信息与本地信息对比，保留不存在的

#中国政府官员信息  
class ChineseOffical(ManInfoRobot):
    def __init__(self,url):
        ManInfoRobot.__init__(self,url)
    
    #获取所有的省份链接并返回
    def get_provice_link(self,html):
        html = BeautifulSoup(html,'lxml')
        province_root_url='http://ldzl.people.com.cn' 
        province_urls = []
        div=html.find('div',class_='fl nav_left_2j').ul
        if not div:
            print "not found div class fl nav_left_2j"
            return None
        li=div.find_all('li')
        for i in li:
            if i.a.has_attr('href'):
                url = province_root_url + i.a['href']
                if url in province_urls:
                    continue
                province_urls.append(url)
        return province_urls
        
    #获取所有的个人链接
    def get_man_link(self,html):
        if not html:
            return
        province_urls = self.get_provice_link(html)
        
        print u"一共有%d省份"%len(province_urls)
        #用于生成个人信息的链接
        man_root_url = "http://ldzl.people.com.cn/dfzlk/front/"
        man_links = []  
        for url in province_urls:
            exists_urls = []
            print u"正在获取%s的信息"%url
            html = self.get_html(url)
            if not html:
                continue
            html = BeautifulSoup(html,'lxml')
            a = html.find_all("a")
            for i in a:
                if i.has_attr('href') and i['href'][:10] == "personPage":   
                    link = man_root_url + i['href']
                    if link in exists_urls:
                        #print "%s exist"%link
                        continue
                    exists_urls.append(link)
                    man_links.append(link)
        return man_links
        
    def get_man_info(self,html):
        html = BeautifulSoup(html,'lxml')
        info = {}
        card = html.find("dl",class_="clearfix")
        if not card:
            print "no"
            return None
        if card.dd.span.text:
            info["level"] = card.dd.span.text     #政治级别
        if card.dd.div.em.text: 
            info["name"] = card.dd.div.em.text   #名字
            print u"正在抓取%s的信息..."%info["name"]
        
        temp = card.dd.p.text.split(u"\n")
        if temp[0].split(u"：")[1]:
            info["sex"] = None
        info["sex"] = temp[0].split(u"：")[1]
        
        if temp[1].split(u"：")[1]:
            info["birth"] = None
        info["birth"] = temp[1].split(u"：")[1]
        
        if not temp[2].split(u"：")[1]:
            info["homeplace"] = None
        info["homeplace"] = temp[2].split(u"：")[1]
        
        if not temp[3].split(u"：")[1]:
            info["degree"] = None
        info["degree"] = temp[3].split(u"：")[1]
        
        info["resource"] = "人民网"
        info["url"] = ""
        return info
        

if __name__=="__main__":
    url = "http://ldzl.people.com.cn/dfzlk/front/personProvince1.htm"
    test_url = "http://ldzl.people.com.cn/dfzlk/front/personPage4990.htm"
    c = ChineseOffical(url).run()
    '''
    html = c.get_html(url)
    print len(html)
    info = c.get_man_info(html)
    print info
    c.man_infos.append(info)
    c.save_man_info("man_infos.csv")
    '''
root_url='http://ldzl.people.com.cn/dfzlk/front/'   #用于生成各个人物介绍的url
baseUrl='http://ldzl.people.com.cn/dfzlk/front/personProvince1.htm'     #爬虫入口地址
province_url='http://ldzl.people.com.cn'    #用于生成要爬取的所有 省和市的地址

#先抓取每个官员的名字，然后再通过名字的连接进入详细介绍，在介绍里抓取其他需要的信息
'''需要抓取的又姓名，职位，大学，学历，性别，年龄,出生地
        网页上的个人简介信息有这一特点     开头第一段都是----姓名，性别，名族，出生年月，出生地
'''

urls=[]
errors=[]
names={}
path  = os.path.dirname(os.path.abspath(__file__))

def record_error(errors):
    print u'---------------------------------------------------------------'
    print u'开始保存本次的错误信息......................'
    if not len(errors):
        print u'-----------------------------------------------------------'
        print u"                    本次抓取没有出现错误.                      "
        return None
    f=open(path+'/errors.txt','w')
    #time=time.ctime()
    num=1
    #f.write(time+'\r\n')
    for error in errors:
        f.write(str(num)+"******"+error+'\r\n')
        num+=1
    print u'----------------------------------------------------------------'
    print u'保存错误信息成功............................'
    f.close()
    
#获取网页信息并用BeautifulSoup解析，返回解析的结果  
def get_html(url):
    try:
        html=requests.get(url,timeout=5)
        if html.status_code==200:
            html=html.text
            soup=BeautifulSoup(html,'lxml')
            return soup
        return None
    except:
        return None

#获取每个官员的个人简介信息，保存在names字典里，每歌官员名字作为字典的key
def get_name_detailed(name):
    html=get_html(name['url'])
    if not html:
        print u'------------------------------------------------------------'
        print u'---------------抓取%s的个人信息错误！'%name['name']
        errors.append(str((name['name'].encode('utf-8')+name['url'].encode('utf-8'))))
        return None
    
    print u'----->正在抓取[   %s       ]的信息...'%name['name']
    #单独抓取他们的职位信息
    ul=html.find('ul',class_='clearfix ld')
    profession=ul.span.text
    name[u'职位']=profession
    p=ul.p.text
    p=p.split('\n')
    for i in p:
        temp=i.split(u'：')
        if temp[0]:
            name[temp[0]]=temp[1]
    '''
 获取到名片信息，再用string.split解析字符串即可
    '''  
            
#生成待爬取的每个省份的url，保存在urls列表里
def province_url_produced(baseURL):
    html=get_html(baseURL)
    if not html:
        return None
    div=html.find('div',class_='fl nav_left_2j')
    if not div:
        return None
    li=div.find_all('li')
    for i in li:
        if i.a.has_attr('href'):
            temp=province_url+i.a['href']
            urls.append(temp)


#爬虫的入口网页，在这里获取所有的省份信息，以及要爬取的官员名字    
def parser_html(html):
    if not html:
        return None
    start=html.find('div',class_='fr p2j_sheng_right title_2j')
    '''
                            经分析发现名字都在class=‘fr p2j_sheng_right title_2j’和class=‘ld2 new_ld’两个容器里，
                            所以先找到这两个个容器就行了，然后找到里面的a元素里面的href和文字内容也就是名字
    '''
    #获取当前领导的执权地 
    if not start:
        return 
    province=start.find('h2').text
    print u'-------------------------------------------------------------------'
    print u'                  正在抓取%s的领导信息.'%province
    print u'-------------------------------------------------------------------'
    
    #找到主要领导的名字信息
    official=start.find('ul',class_='clearfix ld')
    if not official:
        return 
    official=official.find_all('em')
    for i in official:
        if i.text:
            names[i.text]={"name":i.text,"url":root_url+i.a['href']}
            get_name_detailed(names[i.text])
        
    #找到各党委班子和政府副职的领导名字
    
    name=start.find_all('p')
    for p in name:
        for j in p.find_all('a'):
            if names.has_key(j.text):
                print u'--------------------------%s已经抓取过了.'%j.text
            if j.text:
                names[j.text]={"name":j.text,"url":root_url+j['href']}
                get_name_detailed(names[j.text])
    
    #找到各省市区县党政领导人物名字
    name=start.find('div',class_='ld2 new_ld')
    if not name:
        return
    name=name.find_all('li')
    for i in name:
        if not i.has_attr('class'):
            if names.has_key(i.em.text):
                print u'-------------------------'+i.em.text+u'已经存在'
            if names.has_key(i.i.text):
                print u'-------------------------'+i.i.text+u'已经存在' 
            if i.em.text:
                names[i.em.text]={"name":i.em.text,"url":root_url+i.em.a['href']}
                get_name_detailed(names[i.em.text])
            
                names[i.i.text]={"name":i.i.text,"url":root_url+i.i.a['href']}
                get_name_detailed(names[i.i.text])

def save_mes(names):
    print u'----------------------------------------------------------------'
    print u'                    正在保存数据'
    if not names:
        print u'                    要存储的数据为空'
        return None
    num=1
    f=open(path+'/OfficialRelationship.txt','w')
    for name in names:
        f.write(str(num)+"******"+name.encode('utf-8')+"******")
        temp=json.dumps(names[name], ensure_ascii=False)
        f.write(temp.encode('utf-8'))
        f.write('\r\n\r\n')
        num+=1
    f.close()
    print u'-----------------------------------------------------------------'
    print u'                       成功保村信息'

def run():
    num=0
    province_url_produced(baseUrl)
    
    for url in urls:
        print u'----------------------------------------------------------'
        print u'                    正在抓取%s的信息...'%url
        html=get_html(url)
        if not html:
            break;
        parser_html(html)
        for i in names.items():
            if len(i[1])>2:
                num+=1
    print u'---------------------------------------------------------------'
    print u'                            共抓取了%s条有效信息                                                       '%num

    save_mes(names)
    record_error(errors)

# if __name__=='__main__':
    # start=time.time()
    # run()
    # end=time.time()
    # print u'-----------------------------------------------------------------'
    # print u"                共用时-%ds"%int(end-start)