# -*- coding:utf-8 -*-

import time,os

class Crack(object):
    
    '''
    思路是这样的，既然现在破解账号的密码这么难，网站都很注重安全，
    那么可以反过来
    很简单：就是
    生成所有可能的账号组合，然后一一进行登陆，匹配到正确的密码则返回真，
    然后保存，
    主要问题就是需要开启多个线程，不然测试所有的账号组合需要很多的时间，
    然后就是要防止程序意外停止运行后，之前测试过的信息要保存，不然就得
    从头开始匹配。
    还有一个问题就是测试的密码即使尝试完所有的账号后也不一定能有账号和它
    对应。
    
    '''
    
    PATH = os.path.dirname(os.path.abspath(__file__))
    
    # 号码前段3个数字的组合
    ID_SEG = [
                     135, 136, 137, 138, 139, 147, 150, 151, 152, 
                    157, 158, 159, 178, 182, 183, 184, 187, 188,
                    130, 131,132, 155, 156, 185, 186, 145, 176,
                    133, 153, 177, 180, 181, 189
                 ]
    # 当前测试的号码后八位
    CURRENT_COUNT = 0
    # 保存上一次测试到的号码是，防止重复测试
    LAST_COUNT_FILE = "last_count.txt"
    
    # 用于标识是否为密码匹配到合适的账号，也用于停止其他线程
    PASSWORD_MATCH = False
    
    def __init__(self,password):
        self.password = password
    
    # 设置本次开始测试的地址
    def set_local_info(self):
        if self.CURRENT_COUNT == 0:
            count= self.get_last_count()
            self.CURRENT_COUNT = int(count[3:])
            for i in self.ID_SEG:
                if (int(count[:3]) == i):
                    index = self.ID_SEG.index(i)
                    self.ID_SEG = self.ID_SEG[index:]
    
    # 读取本地记录的上一次测试情况，没有记录则返回0从0开始    
    def get_last_count(self):
        try:
            f = open(self.PATH+"/"+ self.LAST_COUNT_FILE,"r")
            last_count = f.read()
            f.close()
            print "last count is %s"%last_count
            return last_count
        except Exception,e:
            print e.message
            print "get last count error,init last count 0"
            return "00000000"
    
    # 保存当前测试的情况
    def save_last_count(self,count):
        try:
            f = open(self.PATH + "/" + self.LAST_COUNT_FILE,"w")
            f.write(count)
            f.close()
            print "save last count success!"
        except Exception,e:
            print e.message
            print "save last count error"
    
    # 保存匹配成功的用户信息
    def save_user(self,count,filename="users.txt"):
        try:
            f = open(self.PATH + "/" + filename,"a")
            f.write(count + ":" + self.password+"\n")
            f.close()
            print "save success !"
        except Exception,e:
            print e.message
            print "save failed"
    
    # 登录网站，子类只需要实现该方法即可
    def web_login(self,count):
        print "web_login"
    
    # 开始测试
    def test_count(self,count):
        count_limit = 9 ** 9    # 这是号码使有效的最大值
        for i in self.ID_SEG:
            while self.CURRENT_COUNT < count_limit and not Crack.PASSWORD_MATCH:
                count = str(i) + "%08d"%self.CURRENT_COUNT
                print "test %s %s"%(count,self.password)
                response = self.web_login(count)
                if response:
                    return count
                self.CURRENT_COUNT += 1
                if self.CURRENT_COUNT % 10 == 0:
                    self.save_last_count(str(i) + str(self.CURRENT_COUNT))
                time.sleep(0.5)
            time.sleep(0.5)
        return False
    
    def crack(self):
        start_time = time.time()
        self.set_local_info()
        count = self.test_count(self.password)
        if count:
            Crack.PASSWORD_MATCH = True
            print("password match count success!,it belows %s"%count)
            self.save_user(count)
            # temp = raw_input("go on (Y/N)?")
            # if temp == "y" or temp =="Y":
                # self.CURRENT_COUNT += 1
                # self.crack()
        else:
            print ("this password match count failed!")
        used_time = time.time() - start_time
        print u"this crack used %d second!"%used_time

        
if __name__ == "__main__":
    Crack("3.1415926").crack()