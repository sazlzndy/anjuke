import requests
from lxml import etree
import pandas as pd #csv保存模块
import time
import pymysql
import os
from urllib.parse import urljoin
from sqlalchemy import create_engine
import json

import js2py
import execjs

from selenium import webdriver

import re
import random #随机模块
from Class import HouseInfo
from Class import BaseDownloader



class AnJuKeApi(BaseDownloader.BaseDownloader):
  def __init__(self):
    self.UrlName = "安居客"
    #self.ApiUrl = "https://nc.anjuke.com/v3/ajax/map/sale/3866/prop_list/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p={0}&zoom=12&lat={1}_{2}&lng={3}_{4}&kw=&maxp=99&et=b1d5bf&ib=1&bst=pem360"
    self.ApiUrl = "https://nc.anjuke.com/v3/ajax/map/sale/711/prop_list/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p=1&zoom=12&lat=28.460809_28.917598&lng=115.502388_116.226782&kw=&maxp=99&et=43d2bd&ib=1&bst=pem592"

    self.ApiHeaderUrl = "https://nc.anjuke.com/map/sale/?from=navigation"

    self.ApiPageReg = "(?<=&p\=)\d+"
    self.MinLat = 28.51916
    self.MaxLat = 28.867442
    self.MinLng = 115.698866
    self.MaxLng = 116.134652


  def GetSession(self):


    headerInfo = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
      'Host': 'nc.anjuke.com',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
      'Accept-Encoding': "gzip, deflate, br",
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': "1"
    }

    s = requests.Session()
    r = s.get(self.ApiHeaderUrl,headers=headerInfo)
    print(r.cookies.values())
    r = s.get(self.ApiUrl,headers=headerInfo,cookies=r.cookies)
    print(r.text)
    #return s

    # 创建chrome参数对象
    options = webdriver.ChromeOptions()

    # 把chrome设置成无界面模式，不论windows还是linux都可以，自动适配对应参数
    options.add_argument('headless')


    brguge = webdriver.Chrome(executable_path="C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver",chrome_options=options)
    brguge.get(self.ApiHeaderUrl)  # 发送get请求
    #sessid = brguge.get_cookie("sessid")["value"]
    print(brguge.get_cookie())
    return sessid


    requestInfo2 = requests.get(url=self.ApiHeaderUrl,headers=headerInfo).text
    infoHtml = etree.HTML(requestInfo2)
    bst = infoHtml.xpath('//*[@id="bst"]')[0]
    tkval = infoHtml.xpath('//*[@id="tkval"]')[0]
    ver_val = infoHtml.xpath('//*[@id="ver_val"]')[0]


    with open('./Class/Ershou_Web_Mapv3_Home.js','r', encoding='UTF-8') as fp:
      js = fp.read()
      print(execjs.get().name)
      print("加载JS文件完成")
      loader = execjs.compile(js)
      #theJs2py = js2py.eval_js(js)
      print("execjs加载JS文件完成")
      r = loader.call('add',1,2)
      #r = theJs2py('3434', '1c278d023f31d59f88790b80d1695f82')
      print("add完成{0}".format(r))
      r = loader.call('del', "3434","1c278d023f31d59f88790b80d1695f82")
      #context = js2py.eval_js(js)
      #vl5x = context.window.gettoken('3434', '1c278d023f31d59f88790b80d1695f82')
      vl5x = r

    print('{0}|{1}|{2}|{3}'.format(bst.attrib['value'],tkval.attrib['value'],ver_val.attrib['value'],vl5x))



  def SaveHouseInfoByApi(self,data,url):
    theSession = self.GetSession()
    return ""


    jsonstr = self.DownPage(url,theSession)
    apiresult = json.loads(jsonstr)

    if apiresult['code'] == 1 :
      return ""

    total = apiresult['val']['pages']['total']
    page_size = apiresult['val']['pages']['page_size']
    page = apiresult['val']['pages']['page']
    props = apiresult['val']['props']
    for prop in props:
        #print(prop['long_title'])
        obj = HouseInfo.HouseInfo()
        obj.URL = "https://nc.anjuke.com/prop/view/{0}{1}".format(prop["source_type"], prop["id"])
        obj.HouseInfoId = prop["id"]
        obj.Title = prop["comm_name"]
        obj.HouseType = prop["rhval"]
        obj.Area =  re.match("^\d+",prop["area"])[0]
        obj.Floor = prop["floor_tag"]
        obj.LongTitle = prop["long_title"]
        obj.TotalPrices = prop["price"]
        obj.TheUnitPrice = obj.TotalPrices / int(obj.Area) * 10000
        obj.SourceUrl = self.UrlName
        obj.Fitment = prop["fitment_value"]
        obj.CommunityName = prop["comm_name"]
        if self.Need_Save_Info( str(obj.HouseInfoId), str(obj.TotalPrices)):
            print("保存{0}".format(obj.LongTitle))
            data.append(obj.to_dict())


    if page * page_size <= total and len(props) == 60:
        return self.ApiUrl.format(page+1, self.MinLat,self.MaxLat,self.MinLng,self.MaxLng)
    else:
        if total > 3500 :
            theMinLng = self.MinLng
            theMaxLng = self.MaxLng
            theMaxLat = 0
            while theMinLng < self.MaxLng:
              theMinLat = self.MinLat

              while theMinLat < self.MaxLat :
                  if theMaxLat > 0 :
                      theMinLat = theMaxLat
                  theMaxLat = theMinLat + ((self.MaxLat - self.MinLat) / 10)
                  return self.ApiUrl.format(1,theMinLat, theMaxLat,theMinLng, theMaxLng)
              if theMaxLng != self.MaxLng:
                theMinLng = theMaxLng
              theMaxLng = theMinLng + ((self.MaxLng - self.MinLng) / 10)
        return ""

    def CreateHeaders(self):
        return {
            'Referer': 'https://nc.anjuke.com/map/sale/?from=navigation',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            # 'Cookie' : 'aQQ_ajkguid=2400BD1D-02AC-9802-EC9E-3D24FFB25706; wmda_uuid=86ee38557d0872ca0b8196bdd23a8df9; wmda_new_uuid=1; wmda_visited_projects=%3B6289197098934; 58tj_uuid=d569f468-a28e-44bc-a1f2-1e9150242e71; als=0; browse_comm_ids=1026858; _ga=GA1.2.1746640190.1544437827; ctid=41; ANJUKE_BUCKET=pc-home%3AErshou_Web_Home_Home-a; sessid=BB9E53DA-8AB9-FEE7-1D23-E0F73FFBDE09; lps=http%3A%2F%2Fnc.anjuke.com%2Fsale%2Fhonggutannanchang-jiulonghuxinqu%2Fp2%2F%7C; twe=2; _gid=GA1.2.2068275622.1550455754; wmda_session_id_6289197098934=1550481535107-7934208b-6c8d-5ecb; init_refer=https%253A%252F%252Fnc.anjuke.com%252Fsale%252F; new_uv=7; new_session=0; __xsptplusUT_8=1; _gat=1; __xsptplus8=8.8.1550481535.%232%7Csp0.baidu.com%7C%7C%7Canjueke%7C%23%23F7_9kDasR4JqhV5BruqhF7SUfW8-Hr5O%23'.format(time.time())
            'Cookie': "sessid=D5F66A1B-EB3D-C1BE-D024-385222A5BB51; aQQ_ajkguid=8A44C344-C4FA-7994-32DE-A384761E7DE8; lps=http%3A%2F%2Fwww.anjuke.com%2F%3Fpi%3DPZ-baidu-pc-all-biaoti%7C; ctid=41; twe=2; ANJUKE_BUCKET=pc-home%3AErshou_Web_Home_Home-b; 58tj_uuid=d0569853-2fdb-469b-a0c8-993cf7abe9ad; init_refer=; new_uv=1; als=0; wmda_uuid=03ac4fa93e212bf49dfa33da5d5f4245; wmda_new_uuid=1; wmda_session_id_6289197098934=1555552883312-1e23e5d3-82c0-e005; wmda_visited_projects=%3B6289197098934; ajk_member_captcha=101681c88993d62b9b30584744218a62; new_session=0; browse_comm_ids=341485; propertys=oflj2n-pq4wbl_; _ga=GA1.2.1949356682.1555552914; _gid=GA1.2.1054890746.1555552914; __xsptplusUT_8=1; __xsptplus8=8.1.1555552883.1555554441.7%234%7C%7C%7C%7C%7C%23%23BFYm0z9CKD507cHeI7IYDrvCVaALPxht%23"
        }

  def DownHousesByApi(self):
    self.CreateSourceHouseInfo()
    data = list()
    url = self.ApiUrl.format("1", self.MinLat,self.MaxLat,self.MinLng,self.MaxLng)
    while (len(url) > 0):
      url = self.SaveHouseInfoByApi(data, url)
      if len(data) > 1000:
        self.SaveData(data)
        data.clear()
    self.SaveData(data)





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

    self._apiPageUri = "https://nc.anjuke.com/v3/ajax/map/sale/3866/prop_list/?room_num=-1&price_id=-1&area_id=-1&floor=-1&orientation=-1&is_two_years=0&is_school=0&is_metro=0&order_id=0&p={0}&zoom=12&lat=28.428286_28.885218&lng=115.437423_116.161816&kw=&maxp=99&et=b1d5bf&ib=1&bst=pem360"

  def DownHousesByApi(self):
    jsonstr = self.DownPage(self._apiPageUri.format(1))
    apiresult = json.loads(jsonstr)
    total = apiresult['val']['pages']['total']
    page_size = apiresult['val']['pages']['page_size']
    page = apiresult['val']['pages']['page']
    props = apiresult['val']['props']
    for prop in props:
      print(prop['long_title'])

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
  def DownPage(self, urlPath,session):
    theHeaders = {
      'Referer': self.ApiHeaderUrl,
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    time.sleep(1)
    print("下载{}数据中".format(urlPath))
    text = session.get(url=urlPath,headers=theHeaders).text
    return text


#中环地产
class ZhongHuan(BaseDownloader.BaseDownloader):



  def SaveHouseInfo(self,data,url):
    pageHtml = self.DownPage(url)
    if len(pageHtml) == 0 :
      print("未成功下载{0}数据，结束本次抓取。".format(url))
      return ""
    infoHtml = etree.HTML(pageHtml)
    infoHtmlXapth = infoHtml.xpath(self.HouseInfoXpath)
    for childInfo in infoHtmlXapth:
      title = childInfo.xpath(".//div[1]/span/a")[0]
      details = childInfo.xpath("string(.//p[@class='horizon-detail'])").split()
      commAddress = ''.join(childInfo.xpath("string(.//p[@class='gray'])").split()).split('/')
      #print("详情{0}".format(commAddress.xpath("string(.)")))
      #print("详情{0}".format(commAddress))
      priceDet = childInfo.xpath(".//div[2]/p[1]")[0].text.strip()
      unitPrice = childInfo.xpath(".//div[2]/p[2]")[0].text.strip()
      #print("保存{0}".format(etree.tostring(details)))

      obj = HouseInfo.HouseInfo()
      obj.URL = urljoin(self.IndexUrl, title.attrib['href'])
      obj.HouseInfoId = urljoin(self.IndexUrl, title.attrib['href']).replace(self.UrlModel.replace("{Id}", ""), "")
      obj.Title = title.text.strip()
      obj.HouseType =  details[1]
      obj.Area = details[2]
      obj.Floor =  commAddress[2]
      obj.YearOfBuild = commAddress[3]
      obj.SpecificAddress =  commAddress[0]
      obj.TotalPrices = priceDet
      obj.TheUnitPrice = unitPrice.replace("元/㎡", "")
      obj.SourceUrl = self.UrlName
      if self.Need_Save_Info(obj.HouseInfoId, obj.TotalPrices):
        print("保存{0}".format(title.text.strip()))
        data.append(obj.to_dict())
    infoNextUrl = infoHtml.xpath(self.NextUrl)
    #print(infoNextUrl[0].xpath("..")[0].attrib['href'])
    if len(infoNextUrl) > 0:
      return urljoin(self.IndexUrl,infoNextUrl[0].xpath("..")[0].attrib['href'])
    else:
      return ""


#鸿基房产
class HongJi(object):
  def __init__(self):
    self._apiUrl = 'http://www.jxhjfc.com/ajax.do?method=searchWebEsf&key=0%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0&nowPage=1&size=30&order='




