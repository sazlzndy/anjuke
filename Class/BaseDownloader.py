import json
import os
import requests
import pandas as pd #csv保存模块
from sqlalchemy import create_engine #mysql
import time
import re

from lxml import etree
from Class import HouseInfo
from urllib.parse import urljoin

'''
按页面下载模板
'''
#中环地产为模板
class BaseDownloader(object):
    IndexUrl = "http://nc.zhdclink.com"
    BaseUrl = "http://nc.zhdclink.com/house/index/pg1" #"http://nc.zhdclink.com/house/index"
    HouseInfoXpath = "/html/body/div[5]/div[1]/ul/li"  # 房屋信息列表
    NextUrl = "/html/body/div[5]/div[2]/ul/a/li[@class='prev' and text()='下一页']"  # 下一页地址
    HouseInfoCsvFilePaht = "Result/ZhongHuanInfos{0}.csv"  # url地址
    UrlModel = "http://nc.zhdclink.com/house/detail/{Id}"  # url模型
    ProxyList = "https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list"  # 代理列表
    MySqlString = "mysql+pymysql://root:123456@localhost:3306/houseinfo" #数据库连接字符串
    UrlName = "中环地产" #用于数据库区别
    SourceHouseInfo = {} #已有数据字典 key=ID value=总价
    ApiUrl = ""
    _downTimeSleep = 0.3
    _userCache = True


    """下载房屋信息
    """
    def DownHouses(self):
        self.CreateSourceHouseInfo()
        # proxies = self.GetProxies()
        data = list()
        url = self.BaseUrl
        while (len(url) > 0):
            url = self.SaveHouseInfo(data, url)
            if len(data) > 1000:
                self.SaveData(data, self.HouseInfoCsvFilePaht)
                data.clear()
        self.SaveData(data, self.HouseInfoCsvFilePaht)



    #新建房屋缓存
    def CreateSourceHouseInfo(self):
        if(self._userCache):
            return
        print("新建数据缓存中")
        engine = create_engine(self.MySqlString)
        pdData = pd.read_sql_query("select HouseInfoId,TotalPrices FROM (select HouseInfoId,TotalPrices FROM houseinfo where SourceUrl='{0}' ORDER BY Id desc ) as a GROUP BY HouseInfoId ".format(self.UrlName),engine)
        self.SourceHouseInfo = pdData.set_index('HouseInfoId').T.to_dict('list')
        print("数据缓存完成，共{0}条数据".format(len(self.SourceHouseInfo)))


    #是否需要保存数据，根据ID和总价判断是否有更新
    def Need_Save_Info(self, houseInfoId, totalPrices):
        if houseInfoId in self.SourceHouseInfo:
           if self.SourceHouseInfo[houseInfoId][0] == totalPrices :
               return False
           else :
               self.SourceHouseInfo[houseInfoId][0] = totalPrices
        else :
            self.SourceHouseInfo[houseInfoId] =  [totalPrices]


        return True

    #获取代理
    def GetProxies(self):
        filepath = 'verified_proxies.json'
        #判断文件是否存在
        if os.path.exists(filepath) :
          for line in open(filepath):
            proxies = json.loads(line)
            return proxies

        proxies = {}
        jsonProxies = self.DownPage(self.ProxyList)
        proxies_list = jsonProxies.split('\n')
        for proxy_str in proxies_list:
            proxy_json = json.loads(proxy_str)
            #测试是否可用
            host = proxy_json["host"]
            port = proxy_json['port']
            type = proxy_json['type']
            url = 'http://icanhazip.com'#http://2019.ip138.com/ic.asp 查看本机IP
            proxy = {
                "http": "{0}://{1}:{2}".format(type,host,port)
            }
            try:
              text = requests.get(url, proxies=proxy,timeout=10).text.strip()
            except:
              text = ""
            if text == host :
              proxies = {
                  "host" : host,
                  "port" : port,
                  "type" : type
              }
              proxiesJson = json.dumps(proxies)
              with open(filepath, 'a+') as f:
                f.write(proxiesJson + '\n')
              print("已写入：%s" % proxies)
        return proxies


      #保存数据至本地
    def SaveData(self,data,filePath=""):
        #db = pymysql.connect("localhost", "root", "123456", "houseinfo")
        engine = create_engine(self.MySqlString)
        pdData = pd.DataFrame(data)
        if(len(filePath) > 0):
            pdData.to_csv(filePath.replace("{0}",time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))), encoding='utf_8_sig')
        pdData.to_sql("houseinfo",engine,if_exists="append", index= False)


    def CreateHeaders(self):
        return {
            'Referer': 'http://nc.zhdclink.com/house/index/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            # 'Cookie' : 'aQQ_ajkguid=2400BD1D-02AC-9802-EC9E-3D24FFB25706; wmda_uuid=86ee38557d0872ca0b8196bdd23a8df9; wmda_new_uuid=1; wmda_visited_projects=%3B6289197098934; 58tj_uuid=d569f468-a28e-44bc-a1f2-1e9150242e71; als=0; browse_comm_ids=1026858; _ga=GA1.2.1746640190.1544437827; ctid=41; ANJUKE_BUCKET=pc-home%3AErshou_Web_Home_Home-a; sessid=BB9E53DA-8AB9-FEE7-1D23-E0F73FFBDE09; lps=http%3A%2F%2Fnc.anjuke.com%2Fsale%2Fhonggutannanchang-jiulonghuxinqu%2Fp2%2F%7C; twe=2; _gid=GA1.2.2068275622.1550455754; wmda_session_id_6289197098934=1550481535107-7934208b-6c8d-5ecb; init_refer=https%253A%252F%252Fnc.anjuke.com%252Fsale%252F; new_uv=7; new_session=0; __xsptplusUT_8=1; _gat=1; __xsptplus8=8.8.1550481535.%232%7Csp0.baidu.com%7C%7C%7Canjueke%7C%23%23F7_9kDasR4JqhV5BruqhF7SUfW8-Hr5O%23'.format(time.time())
            'Cookie': "UM_distinctid=16913127fc745-0ec4ea4970d57f-424e0b28-1fa400-16913127fc8b51; city_token=%E5%8D%97%E6%98%8C; login_token=l6TO0uWIswbQR7Pmzg4EN8aUintBqdjDMH25fAcGv9eFyKVL; CNZZDATA1273460933=196818978-1550802930-null%7C1553570296"
        }

    # 下载网页
    def DownPage(self, urlPath, sleepNumber=300, proxies='', index=0):
        theHeaders = self.CreateHeaders()
        time.sleep(self._downTimeSleep)
        print("下载{}数据中".format(urlPath))

        text = requests.get(url=urlPath, headers=theHeaders, proxies=proxies).text
        if text.find("502 Bad Gateway") >= 0:
            # 尝试下一页
            if index < 5:
                filepath = "errorUrl.txt"
                with open(filepath, 'a+') as f:
                    f.write(urlPath + '\n')
                pageIndex = re.search('[\d]+', urlPath).group(0)
                newPageIndex = int(pageIndex) + 1
                newUrl = urlPath.replace(str(pageIndex), str(newPageIndex))
                return self.DownPage(newUrl, sleepNumber, proxies, index + 1)
            else:
                if sleepNumber < 3600:
                    print("{0}读取失败暂停{1}秒 {2}".format(urlPath, sleepNumber,
                                                     time.strftime('%H:%M:%S', time.localtime(time.time()))))
                    time.sleep(sleepNumber)
                    sleepNumber = sleepNumber * 2
                    print("重试下载{0}数据中{2}".format(urlPath, sleepNumber,
                                                 time.strftime('%H:%M:%S', time.localtime(time.time()))))
                    return self.DownPage(urlPath, sleepNumber)
                else:
                    return ""
        else:
            return text

    def SaveHouseInfo(self, data, url):
        pageHtml = self.DownPage(url)
        if len(pageHtml) == 0:
            print("未成功下载{0}数据，结束本次抓取。".format(url))
            return ""
        infoHtml = etree.HTML(pageHtml)
        infoHtmlXapth = infoHtml.xpath(self.HouseInfoXpath)
        for childInfo in infoHtmlXapth:
            title = childInfo.xpath(".//div[1]/span/a")[0]
            details = childInfo.xpath("string(.//p[@class='horizon-detail'])").split()
            commAddress = ''.join(childInfo.xpath("string(.//p[@class='gray'])").split()).split('/')
            # print("详情{0}".format(commAddress.xpath("string(.)")))
            # print("详情{0}".format(commAddress))
            priceDet = childInfo.xpath(".//div[2]/p[1]")[0].text.strip()
            unitPrice = childInfo.xpath(".//div[2]/p[2]")[0].text.strip()
            # print("保存{0}".format(etree.tostring(details)))

            obj = HouseInfo.HouseInfo()
            obj.URL = urljoin(self.IndexUrl, title.attrib['href'])
            obj.HouseInfoId = urljoin(self.IndexUrl, title.attrib['href']).replace(self.UrlModel.replace("{Id}", ""),"")
            obj.Title = title.text.strip()
            obj.HouseType = details[1]
            obj.Area = details[2]
            obj.Floor = commAddress[2]
            obj.YearOfBuild = commAddress[3]
            obj.SpecificAddress = commAddress[0]
            obj.TotalPrices = priceDet
            obj.TheUnitPrice = unitPrice.replace("元/㎡", "")
            obj.SourceUrl = self.UrlName
            if self.Need_Save_Info(obj.HouseInfoId, obj.TotalPrices):
                print("保存{0}".format(title.text.strip()))
                data.append(obj.to_dict())
        infoNextUrl = infoHtml.xpath(self.NextUrl)
        # print(infoNextUrl[0].xpath("..")[0].attrib['href'])
        if len(infoNextUrl) > 0:
            return urljoin(self.IndexUrl, infoNextUrl[0].xpath("..")[0].attrib['href'])
        else:
            return ""


