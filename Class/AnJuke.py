import requests
from lxml import etree
import pandas as pd #csv保存模块
import time
import pymysql
import os
from urllib.parse import urljoin
from sqlalchemy import create_engine
import random #随机模块

#安居客
class AnJuKe(object):
  def __init__(self):
    self._errorXpath =  "/html/body/div[2]/div" ; #安居客网页异常
    self._errorMessage  =  "系统检测到您正在使用网页抓取工具访问安居客网站，请卸载删除后访问"; #安居客网页异常提示信息
    self._regionXpath = "/html/body/div[1]/div[2]/div[3]/div[1]/span[2]/a";  # 区域
    self._childRegionXpath = "/html/body/div[1]/div[2]/div[3]/div[1]/span[2]/div/a" #子区域
    self._csvFilePaht = "Result/AnJuKeUrls.csv" #url地址

    self._houseInfoXpath = "/html/body/div[1]/div[2]/div[4]/ul/li" #房屋信息列表
    self._nextUrl = "/html/body/div[1]/div[2]/div[4]/div[7]/a[@class='aNxt']" #下一页地址


    self._houseInfoCsvFilePaht = "Result/AnJuKeInfos.csv"  # url地址

  #下载房屋信息
  def DownHouses(self):
    urls =pd.read_csv(self._csvFilePaht, encoding='utf_8_sig')
    data = list()
    for url in  urls[(urls["区域名称"]=="九龙湖新区") &  (urls["类型"]=="小区")]["区域链接"]:
      self.SaveHouseInfo(data,url)



    self.SaveData(data,self._houseInfoCsvFilePaht)

  def SaveHouseInfo(self,data,url):
    infoHtml = etree.HTML(self.DownPage(url))
    infoHtmlXapth = infoHtml.xpath(self._houseInfoXpath)
    for childInfo in infoHtmlXapth:
      title = childInfo.xpath(".//a[1]")[0]
      details = childInfo.xpath(".//div[@class='details-item'][1]/span")
      commAddress = childInfo.xpath(".//span[@class='comm-address'][1]")[0]
      priceDet = childInfo.xpath(".//span[@class='price-det'][1]/strong")[0]
      unitPrice = childInfo.xpath(".//span[@class='unit-price'][1]")[0]
      #print("保存{0}".format(etree.tostring(details)))
      print("保存{0}".format(title.attrib['title']))
      data.append({
        "标题": title.attrib['title'],
        "链接":title.attrib['href'],
        "房型":details[0].text,
        "面积":details[1].text,
        "楼层":details[2].text,
        "建造年份":details[3].text,
        "具体地址":commAddress.attrib['title'],
        "总价":priceDet.text,
        "单价":unitPrice.text
      })
    infoNextUrl = infoHtml.xpath(self._nextUrl)
    if len(infoNextUrl) > 0:
      #print(infoNextUrl[0].attrib['href'])
      self.SaveHouseInfo(data,infoNextUrl[0].attrib['href'])


  #保存数据至本地
  def SaveData(self,data,filePath):
    pdData = pd.DataFrame(data)
    pdData.to_csv(filePath, encoding='utf_8_sig')

  #下载地区URL列表
  def DownURL(self):
    baseUrl = "https://nc.anjuke.com/sale/"

    print("正在爬取")
    text = self.DownPage(baseUrl)
    print("爬取完成")
    html = etree.HTML(text)  # 解析网页

    #首页URL
    htmlXapth = html.xpath(self._regionXpath)
    data = list()

    for info in htmlXapth:
      print("爬取{}数据中".format(info.text))
      infoUrl = info.xpath(".//@href")[0]
      data.append({"区域名称": info.text, "区域链接":infoUrl, "类型":"大区" })
      infoHtml = etree.HTML(self.DownPage(infoUrl))
      infoHtmlXapth = infoHtml.xpath(self._childRegionXpath)
      for childInfo in infoHtmlXapth:
        print("保存{}数据中".format(childInfo.text))
        data.append({"区域名称": childInfo.text, "区域链接": childInfo.xpath(".//@href")[0], "类型":"小区" })
      print("爬取{}数据完成".format(info.text))

    self.SaveData(data,self._csvFilePaht)

  #下载网页
  def DownPage(self, urlPath):
    theHeaders = {
      'Referer': 'https://nc.anjuke.com/sale/',
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
      'Cookie' : 'aQQ_ajkguid=2400BD1D-02AC-9802-EC9E-3D24FFB25706; wmda_uuid=86ee38557d0872ca0b8196bdd23a8df9; wmda_new_uuid=1; wmda_visited_projects=%3B6289197098934; 58tj_uuid=d569f468-a28e-44bc-a1f2-1e9150242e71; als=0; browse_comm_ids=1026858; _ga=GA1.2.1746640190.1544437827; ctid=41; ANJUKE_BUCKET=pc-home%3AErshou_Web_Home_Home-a; sessid=BB9E53DA-8AB9-FEE7-1D23-E0F73FFBDE09; lps=http%3A%2F%2Fnc.anjuke.com%2Fsale%2Fhonggutannanchang-jiulonghuxinqu%2Fp2%2F%7C; twe=2; _gid=GA1.2.2068275622.1550455754; wmda_session_id_6289197098934=1550481535107-7934208b-6c8d-5ecb; init_refer=https%253A%252F%252Fnc.anjuke.com%252Fsale%252F; new_uv=7; new_session=0; __xsptplusUT_8=1; _gat=1; __xsptplus8=8.8.1550481535.%232%7Csp0.baidu.com%7C%7C%7Canjueke%7C%23%23F7_9kDasR4JqhV5BruqhF7SUfW8-Hr5O%23'.format(time.time())
    }
    time.sleep(1)
    print("下载{}数据中".format(urlPath))
    text = requests.get(url=urlPath,headers=theHeaders).text
    #print(text)
    return text


#中环地产
class ZhongHuan(object):
  def __init__(self):
    self._indexUrl = "http://nc.zhdclink.com"
    self._baseUrl = "http://nc.zhdclink.com/house/index"
    self._houseInfoXpath = "/html/body/div[5]/div[1]/ul/li" #房屋信息列表
    self._nextUrl = "/html/body/div[5]/div[2]/ul/a/li[@class='prev' and text()='下一页']" #下一页地址
    self._houseInfoCsvFilePaht = "Result/ZhongHuanInfos{0}.csv"  # url地址
    self._urlModel = "http://nc.zhdclink.com/house/detail/{Id}" #url
    self._proxtList = "https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list" #代理列表

  #下载房屋信息
  def DownHouses(self):
    data = list()
    url = self._baseUrl;
    while(len(url) > 0):
      url = self.SaveHouseInfo(data,url)
      if len(data) > 1000:
          self.SaveData(data, self._houseInfoCsvFilePaht)
          data.clear()
    self.SaveData(data,self._houseInfoCsvFilePaht)

  def SaveHouseInfo(self,data,url):
    pageHtml = self.DownPage(url)
    if len(pageHtml) == 0 :
      print("未成功下载{0}数据，结束本次抓取。".format(url))
      return ""
    infoHtml = etree.HTML(pageHtml)
    infoHtmlXapth = infoHtml.xpath(self._houseInfoXpath)
    for childInfo in infoHtmlXapth:
      title = childInfo.xpath(".//div[1]/span/a")[0]
      details = childInfo.xpath("string(.//p[@class='horizon-detail'])").split()
      commAddress = ''.join(childInfo.xpath("string(.//p[@class='gray'])").split()).split('/')
      #print("详情{0}".format(commAddress.xpath("string(.)")))
      #print("详情{0}".format(commAddress))
      priceDet = childInfo.xpath(".//div[2]/p[1]")[0].text.strip()
      unitPrice = childInfo.xpath(".//div[2]/p[2]")[0].text.strip()
      #print("保存{0}".format(etree.tostring(details)))
      print("保存{0}".format(title.text.strip()))
      data.append({
        "HouseInfoId" : urljoin(self._indexUrl,title.attrib['href']).replace(self._urlModel.replace("{Id}",""),""),
        "Title": title.text.strip(),
        "URL":urljoin(self._indexUrl,title.attrib['href']),
        "HouseType":details[1],
        "Area":details[2],
        "Floor":commAddress[2],
        "YearOfBuild":commAddress[3],
        "SpecificAddress":commAddress[0],
        "TotalPrices":priceDet,
        "TheUnitPrice":unitPrice.replace("元/㎡","")
      })
    infoNextUrl = infoHtml.xpath(self._nextUrl)
    #print(infoNextUrl[0].xpath("..")[0].attrib['href'])
    if len(infoNextUrl) > 0:
      return urljoin(self._indexUrl,infoNextUrl[0].xpath("..")[0].attrib['href'])
    else:
      return ""


  #保存数据至本地
  def SaveData(self,data,filePath):
    #db = pymysql.connect("localhost", "root", "123456", "houseinfo")
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/houseinfo')
    pdData = pd.DataFrame(data)
    pdData.to_csv(filePath.replace("{0}",time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))), encoding='utf_8_sig')
    pdData.to_sql("houseinfo",engine,if_exists="append", index= False)

  #下载地区URL列表
  def DownURL(self):
    baseUrl = "https://nc.anjuke.com/sale/"

    print("正在爬取")
    text = self.DownPage(baseUrl)
    print("爬取完成")
    html = etree.HTML(text)  # 解析网页

    #首页URL
    htmlXapth = html.xpath(self._regionXpath)
    data = list()

    for info in htmlXapth:
      print("爬取{}数据中".format(info.text))
      infoUrl = info.xpath(".//@href")[0]
      data.append({"区域名称": info.text, "区域链接":infoUrl, "类型":"大区" })
      infoHtml = etree.HTML(self.DownPage(infoUrl))
      infoHtmlXapth = infoHtml.xpath(self._childRegionXpath)
      for childInfo in infoHtmlXapth:
        print("保存{}数据中".format(childInfo.text))
        data.append({"区域名称": childInfo.text, "区域链接": childInfo.xpath(".//@href")[0], "类型":"小区" })
      print("爬取{}数据完成".format(info.text))

    self.SaveData(data,self._csvFilePaht)

  def GetProxies(self):
    proxies = {
      "http": "http://10.10.1.10:3128",
      "https": "http://10.10.1.10:1080",
    }
    return proxies

  #下载网页
  def DownPage(self, urlPath,index=300,proxies = ''):
    theHeaders = {
      'Referer': 'http://nc.zhdclink.com/house/index/',
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
      #'Cookie' : 'aQQ_ajkguid=2400BD1D-02AC-9802-EC9E-3D24FFB25706; wmda_uuid=86ee38557d0872ca0b8196bdd23a8df9; wmda_new_uuid=1; wmda_visited_projects=%3B6289197098934; 58tj_uuid=d569f468-a28e-44bc-a1f2-1e9150242e71; als=0; browse_comm_ids=1026858; _ga=GA1.2.1746640190.1544437827; ctid=41; ANJUKE_BUCKET=pc-home%3AErshou_Web_Home_Home-a; sessid=BB9E53DA-8AB9-FEE7-1D23-E0F73FFBDE09; lps=http%3A%2F%2Fnc.anjuke.com%2Fsale%2Fhonggutannanchang-jiulonghuxinqu%2Fp2%2F%7C; twe=2; _gid=GA1.2.2068275622.1550455754; wmda_session_id_6289197098934=1550481535107-7934208b-6c8d-5ecb; init_refer=https%253A%252F%252Fnc.anjuke.com%252Fsale%252F; new_uv=7; new_session=0; __xsptplusUT_8=1; _gat=1; __xsptplus8=8.8.1550481535.%232%7Csp0.baidu.com%7C%7C%7Canjueke%7C%23%23F7_9kDasR4JqhV5BruqhF7SUfW8-Hr5O%23'.format(time.time())
     'Cookie': "city_token=%E5%8D%97%E6%98%8C; login_token=uSDWeKN57IikxJ2sFdT4BXVRhU1OcqLEZlGgCMp9jm0fzrab; UM_distinctid=169b2fbeb7b300-0f7cb459947171-424e0b28-1fa400-169b2fbeb7c13c; CNZZDATA1273460933=1237323342-1553485980-%7C1553492604"
    }
    time.sleep(0.3)
    print("下载{}数据中".format(urlPath))

    text = requests.get(url=urlPath,headers=theHeaders,proxies=proxies).text
    if text.find("502 Bad Gateway") >= 0 :
        if index < 3600:
            time.sleep(index)
            index = index*2
            print("重试{1}次下载{0}数据中{2}".format(urlPath,index,time.strftime('%H:%M:%S',time.localtime(time.time()))))
            return self.DownPage(urlPath,index)
        else:
            return ""
    else:
        return text
    #print(text)




class HongJi(object):
  def __init__(self):
    self._apiUrl = 'http://www.jxhjfc.com/ajax.do?method=searchWebEsf&key=0%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0&nowPage=1&size=30&order='