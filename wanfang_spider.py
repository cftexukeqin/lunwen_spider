import requests
from bs4 import BeautifulSoup as bs
import re
import time
import pandas
from retrying import retry

url = "http://www.wanfangdata.com.cn/search/searchList.do?searchType=all&showType=&searchWord=%E9%92%88%E7%81%B8%E5%87%8F%E8%82%A5&isTriggerTag="

url_lists = []
short_url_lists = []
title_lists = []
summary_lists = []
auth_lists = []
auth_per_page = []
@retry(stop_max_attempt_number = 3)
def get_url(url,search_type):
    header = {
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Host":"www.wanfangdata.com.cn",
    "Connection":"keep-alive"
    }
    # proxies = { "http": "http://61.135.217.7:80", "http": "http://180.173.48.100:53281", }
    
    res = requests.get(url,headers=header)
    soup = bs(res.text,'lxml')

    urls = soup.select('.icon_Miner')
    for i in urls:
        if search_type == 'p':
            short_url_lists.append(("http://www.wanfangdata.com.cn/details/detail.do?_type=perio&id="+i['onclick'].split(',')[1]).replace("'",''))
        elif search_type == 'c':
            short_url_lists.append(("http://www.wanfangdata.com.cn/details/detail.do?_type=conference&id="+i['onclick'].split(',')[1]).replace("'",''))
        elif search_type == 'd':
            short_url_lists.append(("http://www.wanfangdata.com.cn/details/detail.do?_type=degree&id="+i['onclick'].split(',')[1]).replace("'",''))
    return short_url_lists

def get_info(url,search_type):
    
    res = requests.get(url)
    soup = bs(res.text,'lxml')

    titles = soup.select('.crumbs font')
    for title in titles:
        title_lists.append(title.text)

    summarys = soup.select('.abstract textarea')
    for i in summarys:
        summary_lists.append(i.text)
    auths = soup.select('.college')
    for auth in auths:
        auth_per_page.append(auth.text)

    if search_type == 'p':
        total = list(zip(title_lists,auth_per_page,summary_lists))
    elif search_type == 'c':
        total = list(zip(title_lists,summary_lists))
    else:
        total = list(zip(title_lists,summary_lists))

    return total
                
def main():
    while True:
        try:
            key_word = input('请输入要检索的关键词(例如：四轴飞行器):')
            type = input('请选择论文类别(p:期刊论文 c：会议论文 d：学位论文)：')
            start_page = int(input('请输入要爬取的起始页：'))
            page_num = int(input('请输入要爬取的页数(每页默认50条数据)：'))

            if type == 'p':
                base_url = "http://www.wanfangdata.com.cn/search/searchList.do?searchType=perio&pageSize=50&page={}&searchWord={}&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=all"
            elif type == 'c':
                base_url = "http://www.wanfangdata.com.cn/search/searchList.do?searchType=conference&pageSize=50&page={}&searchWord={}&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=all"
            elif type == 'd':
                base_url = "http://www.wanfangdata.com.cn/search/searchList.do?searchType=degree&pageSize=50&page={}&searchWord={}&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=all"
            else:
                base_url = "http://www.wanfangdata.com.cn/search/searchList.do?searchType=all&pageSize=50&page={}&searchWord={}&order=correlation&showType=detail&isCheck=check&isHit=&isHitUnit=&firstAuthor=false&rangeParame=all"
            file_name = input('请输入文件名(默认保存在Excel中，只需输入文件名即可，如 期刊)：')
            print('正在检索...')
            for i in range(start_page,int(start_page+page_num)):
                new_url = base_url.format(i, key_word)
                all_page_urllists = get_url(new_url, type)

            for j in all_page_urllists:
                total = get_info(j, type)
                time.sleep(2)
        except Exception as e:
            print(e)
        else:
            break
    df =  pandas.DataFrame(total)
    df.to_excel(file_name+'.xlsx')
if __name__ == "__main__":
    print("""
*************************论文摘要分类爬取脚本*************************
Auth:                                                       DX.Ssssss
DateTime:                                                  2018-03-23
Version:                                                        1.0.V
Tips:各种反爬机制，速度稍微快点都会被服务器断开连接，因此设置了访问延
时，经过反复测试，发现每隔2-3秒访问网站可有效解决此问题，因此爬取时间较
长，请耐心等待！
*********************************************************************
    """)
    main()
