from bs4 import BeautifulSoup
from urllib.request import urlopen,Request  
import random  
import os
import re  
import time
import json


DOMAIN = "http://www.haodf.com"
HEARDERS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"]  


def operate_file(url,html = ''):
    f = open(url,'w')
    f.write(html)
    f.close()


def getContent(url):  
    """ 
    此函数用于抓取返回403禁止访问的网页 
    """  
    random_header = random.choice(HEARDERS)  
  
    """ 
    对于Request中的第二个参数headers，它是字典型参数，所以在传入时 
    也可以直接将个字典传入，字典中就是下面元组的键值对应 
    """  
    req =Request(url)  
    req.add_header("User-Agent", random_header)  
    req.add_header("GET",url)  
    req.add_header("Host","www.haodf.com")  
    req.add_header("Referer","http://www.haodf.com/jibing/erkezonghe/list.htm")  
  
    content=urlopen(req).read().decode("gb2312")  
    return content  



#获取疾病类型与名字
def getDiseaseList(soup):
    data = {}
    disease_type_tag = soup.find_all('div',attrs={'class':'m_title_green'})
    disease_name_tag = soup.find_all('div',attrs={'class':'m_ctt_green'})
    disease_type_list = [l.string for l in disease_type_tag] #所有疾病类型
    disease_name_list = [[i.string for i in l.find_all('a')] for l in disease_name_tag] #所有疾病名称
    data["disease_type"] = disease_type_list
    data["disease_name"] = disease_name_list
    return data

#获去科室名称
def getRoomList(soup,roomname = ""):
    data = []
    room_tag = soup.find('div',attrs={'class':'ksbd'})

    #处理没有科室的情况
    if room_tag == None:
        none_data = {}
        none_data["room_name"] = roomname
        none_disease_data = getDiseaseList(soup)
        none_data["room_disease"] = none_disease_data
        data.append(none_data)
        return data


    room_name_list = [l.a.string for l in room_tag.find_all('li')] #所有科室名称
    room_href_list = [DOMAIN+l.a['href']  for l in room_tag.find_all('li')] #所有科室链接
    
    for i in range(len(room_name_list)):
        time.sleep(1)
        room_data = {}
        html = getContent(room_href_list[i])
        room_soup = BeautifulSoup(html,features='lxml')
        disease_data = getDiseaseList(room_soup)
        room_data["room_name"] = room_name_list[i]
        room_data["room_disease"] = disease_data
        print(room_name_list[i])
        data.append(room_data)
    return data

#获取学科
def getSubjectList(soup):
    data = []
    all_subject_tag = soup.find_all('div',attrs={'class':'kstl'})

    sub_name_list = [l.a.string for l in all_subject_tag] #所有科目名称
    sub_href_list = [DOMAIN+l.a['href'] for l in all_subject_tag] #所有科目链接

    for i in range(len(sub_name_list)):
        print(sub_name_list[i])
        sub_data = {}
        html = getContent(sub_href_list[i])
        sub_soup = BeautifulSoup(html,features='lxml')
        room_data = getRoomList(sub_soup,roomname = sub_name_list[i])
        sub_data["sub_name"] = sub_name_list[i]
        sub_data["sub_room"] = room_data
        data.append(sub_data)
    return data


url="http://www.haodf.com/jibing/erkezonghe/list.htm" 
html = getContent(url)
soup = BeautifulSoup(html,features='lxml')

all_data = {}

all_data["data"] = getSubjectList(soup)

in_json = json.dumps(all_data,ensure_ascii=False)
operate_file('data_json.txt',in_json)





