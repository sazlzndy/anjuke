import requests #pip3 install  requests
from Class import AnJuke
from lxml import etree #pip3 install lxml
import pandas as pd #csv保存模块 #pip3 install pandas
import random #随机模块





ob = AnJuke.AnJuKeApi()

#ob = AnJuke.ZhongHuan()


ob.DownHousesByApi()

exit()
ob.DownURL()

exit()

proxies = {
  "http": "158.181.241.94:38110",
  "https": "158.181.241.94:38110"
}
print(ob._errorMessage)

text = requests.get(url='https://nc.anjuke.com/sale/').text

#with open('c:/1.txt', 'r', encoding='utf-8') as f:
#  text = f.read()

print("正在爬取")
print(text)
html = etree.HTML(text)  # 解析网页

regionXpath = "/html/body/div[1]/div[2]/div[3]/div[1]/span[2]/a"
htmlXapth = html.xpath(regionXpath)
data = list()

for info in htmlXapth:
  data.append({ "区域名称":info.text,"区域链接":info.xpath(".//@href")[0] })

pdData = pd.DataFrame(data)
pdData.to_csv("c:/1.csv", encoding='utf_8_sig')

#子区域  //*[@id="content"]/div[3]/div[1]/span[2]/div/a[1]

print("完成....")
#print("正在存储数据....")
#data = pd.DataFrame(self._data)
#data.to_csv("链家网租房数据.csv", encoding='utf_8_sig')  # 写入文件




#print(response.text)   #打印解码后的返回数据

#/html/body/div[1]/div[2]/div[3]/div[1]/span[2]

#//*[@id="content"]/div[3]/div[1]/span[2]



#class FangTianXia(object):