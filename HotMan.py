#-*- coding:utf-8 -*-

import sys
sys.path.append("H://relax")

import os
import time
from bs4 import BeautifulSoup
from WebManager import get_html
from MailManager import MailManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#今日政治人物热搜排行
#排行信息如下
#[(省|市,职位,姓名,热度),]
class HotMan(object):

    path = os.path.dirname(os.path.abspath(__file__))
    def __init__(self,url):
        self.url = url
        
    def get_html(self,url):
        from selenium import webdriver
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] =("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586" )
        #self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.driver = webdriver.Chrome()
        #self.driver.set_window_size(1280, 800)
        self.driver.get(url)
        #time.sleep(1)
        #self.driver.execute_script("window.scrollBy(0,200)","")
        time.sleep(2)
        html = self.driver.page_source
        #driver.quit()
        return html
    
    def get_local_sort(self,filename):
        pass
        
    def get_sort(self,html,type = "province"):
        if not html:
            print "get error"
            return None
        if type == "province":
            sort = self.get_sort_by_provinve(html)
        elif type == "city":
            sort = self.get_sort_by_city(html)
        else:
            return None
        return sort
    
    def get_sort_by_city(self,html):
        sort = []
        html = BeautifulSoup(html,'lxml')
        return sort
        
    def get_sort_by_provinve(self,html):
        sort = []
        # html = BeautifulSoup(html,'lxml')
        # print html
        # div = html.find("div",class_="ind_p2_left fl")
        # print div
        
        div = self.driver.find_element_by_css_selector("div[class=\"ind_p2_left fl\"")
        mans = div.find_elements_by_tag_name("li")
        for i in mans:
            province = i.find_element_by_tag_name("span").text
            level = i.find_element_by_tag_name("a").get_attribute("title")
            name = i.find_element_by_tag_name("em").text
            hot = i.find_element_by_tag_name("i").text
            sort_info = {
                            "province":province,"level":level,
                            "name":name,"hot",hot
                        }
            sort.append(sort_info)
        return sort
    
    def save_info(self,filename,sort):
        import time
        import codecs
        if not len(sort):
            return
        f = open(self.path + "/" + filename,"w")
        f.write(codecs.BOM_UTF8)
        s = csv.writer(f)
        time = str(time.ctime())
        for movie in sort:
            for i in movie.keys():
                try:
                    movie[i] = movie[i].encode("utf-8")
                except:
                    pass
            
            s.writerow(
                        [ movie["province"],movie["level"],movie["name"],\
                          movie["hot"]]
                        )
        f.close()
    
    def ifChange(self,filename,newsort):
        local_sort = self.get_local(filename)
        if local_sort == newsort:
            print "no update"
        else:
            self.save_info(filename,newsort)
    
    def send_mail_to(self,username,subject,message):
        MailManager().send_mail_to(username,subject,message)
        
        
    def run(self):
        while True:
            html = self.get_html(self.url)
            sort_provinve = self.get_sort(html,"province")
            sort_city = self.get_sort(html,"city")
            
            content = ""
            if sort_provinve:
                content += "今日省热搜:\n" + "-"*20 + "\n"
                for i in sort_provinve:
                    content = content + i[0] + " "*4 + i[1] + " "*4 + i[2] + "\n"
            
            if sort_city:
                content += "-"*20 + "\n" 
                content += "今日市热搜:\n"
                content += "-"*20 + "\n"
                for j in sort_city:
                    content = content + j[0] + " "*4 + j[1] + " "*4 + j[2] + "\n"
            
            if content:
                self.send_mail_to("1183008540@qq.com","today's hot man",content)
            
            time.sleep(300)

            
if __name__ =="__main__":
    url = "http://ldzl.people.com.cn/dfzlk/front/firstPage.htm"
    HotMan(url).run()