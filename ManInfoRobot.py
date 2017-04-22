#-*- coding:utf-8 -*-

import sys
sys.path.append("H://relax")

import os
import csv
import time
import codecs
from WebManager import get_html

#抓取人物信息
#格式如下：
#   姓名  |   性别  |   出生年月    |   籍贯  |   学历/学位   领导级别
# {  
#   "name":name,
#   "sex":sex,
#   "birth":birth,
#   "homeplace":homeplace,
#   "degree":degree,//学位
#   "level":level
# }

class ManInfoRobot(object):
    local_infos = []
    man_infos = []
    errors = []
    path = os.path.dirname(os.path.abspath(__file__))
    def __init__(self,url):
        self.url = url
        self.get_local_info("man_infos.csv")
        
    #   姓名  |   性别  |   出生年月    |   籍贯  |   学历/学位   |   领导级别  |  信息来源
    def get_local_info(self,filename):
        try:
            f = open(self.path + "/" + filename,"rb")
            csv_file = csv.reader(f)
            for news in csv_file:
                #print news[0]
                self.local_infos.append(news[6])
            f.close()
            print "get locals!"
        except:
            f = open(self.path + "/" + filename,"wb")
            f.write(codecs.BOM_UTF8)
            csv_file = csv.writer(f)
            csv_file.writerow(["姓名","性别","出生年月","籍贯","学历|学位","领导级别","链接","信息来源"])
            f.close()
            print "not get locals"
    
    def get_html(self,url):
        html = get_html(url)
        if html == None:
            self.errors.append(url)
        return html
            
    def get_man_link(self,html):
        links = []
        print "get man link"
        return links
    
    def get_man_info(self,html):
        info = {}
        print "get man info"
        return info
    
    def save_man_info(self,filename,info):

        import time
        import codecs
        # if not len(self.man_infos):
            # return
        f = open(self.path + "/" + filename,"ab")
        f.write(codecs.BOM_UTF8)
        s = csv.writer(f)
        for i in info.keys():
            try:
                info[i] = info[i].encode("utf-8")
            except:
                pass
        try:
            s.writerow(
                        [ info["name"],info["sex"],info["birth"],\
                        info["homeplace"],info["degree"],info["level"],info["url"],info["resource"]]
                    )
        except:
            print u"save %s error"%man["name"]
        # for man in self.man_infos:
            # for i in man.keys():
                # try:
                    # man[i] = man[i].encode("utf-8")
                # except:
                    # pass
            # try:
                # s.writerow(
                            # [ man["name"],man["sex"],man["birth"],\
                            # man["homeplace"],man["degree"],man["level"],man["url"],man["resource"]]
                            # )
            # except:
                # print u"save %s error"%man["name"]
                
        # f.close()
        print "save success!"
    
    def record_error(self):
        import time
        import codecs
        if not len(self.errors):
            return
        f = open(self.path + "/errors.csv","ab")
        f.write(codecs.BOM_UTF8)
        s = csv.writer(f)
        for error in self.errors:
            try:
                error = error.encode("utf-8")
            except:
                pass
            try:
                s.writerow([error])
            except:
                print "write %s error"%error
    
    #抓取所有人物信息链接
    #遍历人物链接
    #抓取每个人的详细信息
    def run(self):
        number = 0
        start_time = time.time()
        html = self.get_html(self.url)
        if not html:
            return
        links = self.get_man_link(html)

        for link in links:
            html = self.get_html(link)
            if not html:
                continue
            if link in self.local_infos:
                print "this info exists"
                continue
            info = self.get_man_info(html)
            if not info:
                continue
            info["url"] = link
            #self.man_infos.append(info)
            self.save_man_info("man_infos.csv",info)
            number += 1
        
        time_uesd = time.time() - start_time
        print u"-----------------------------------------"
        print u"爬取完毕..."
        print u"成功获取了%d个人的信息"%number
        print u"一共用时%d秒"%time_uesd

if __name__ == "__main__":
    ManInfoRobot("http://www.baidu.com").run()
        
            
        