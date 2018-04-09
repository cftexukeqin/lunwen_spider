import requests
from bs4 import BeautifulSoup as bs
import re
import time
import pandas
# from retrying import retry
from lxml import etree
import random
import turtle


#所有的url 列表
url_lists = []
# 每页所有的url列表
short_url_lists = []
# 所有的论文标题
title_lists = []
# 所有的论文摘要
summary_lists = []
# 期刊论文作者
perio_auth_lists = []
# 期刊发表时间
date_lists = []
# 期刊论文作者单位
perio_company_lists = []
# 学位论文作者
degree_auth_lists = []
# 期刊名称列表
collegss_per_page = []
# 学位学校
all_colleges = []
# 学位
degree_lists = []
# 授予学位时间
dtime_lists = []
# 重试次数
# @retry(stop_max_attempt_number=3)
# 所有url获取函数

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Host": "www.wanfangdata.com.cn",
    "Connection": "keep-alive"
}
proxies = {"http": "http://47.93.3.242:80", "http": "http://121.232.145.92:9000"}


def get_url(url, search_type):

    res = requests.get(url, headers=header)
    soup = bs(res.text, 'lxml')
    # 获取每页所有的url
    urls = soup.select('.icon_Miner')
    for i in urls:
        if search_type == 'p':
            short_url_lists.append(("http://www.wanfangdata.com.cn/details/detail.do?_type=perio&id=" +
                                    i['onclick'].split(',')[1]).replace("'", ''))
        elif search_type == 'c':
            short_url_lists.append(("http://www.wanfangdata.com.cn/details/detail.do?_type=conference&id=" +
                                    i['onclick'].split(',')[1]).replace("'", ''))
        elif search_type == 'd':
            short_url_lists.append(("http://www.wanfangdata.com.cn/details/detail.do?_type=degree&id=" +
                                    i['onclick'].split(',')[1]).replace("'", ''))
    return short_url_lists

# 获取每页的详细信息，
def get_info(url, search_type):
    res = requests.get(url,headers=header)
    soup = bs(res.text, 'lxml')
    selector = etree.HTML(res.text)
    titles = soup.select('.crumbs font')
    for title in titles:
        title_lists.append(title.text)
    summarys = soup.select('.abstract textarea')
    if len(summarys) != 0:
        for i in summarys:
            summary_lists.append(i.text)
    else:
        summary_lists.append("None")
    # 根据检索类型：期刊、学位、会议，获取不同的信息
    if search_type == 'p':
        # 作者信息
        auths = selector.xpath('//div[@class="info_right"]/a[@class="info_right_name"]/text()')
        perio_auth_lists.append(tuple(auths))
        # 作者单位
        company = selector.xpath('//li/div[@class="info_right"]/a[@href="javascript:void(0)"]/text()')
        if company and len(company) >= 2:
            perio_company_lists.append(tuple(company[-2:-1]) if len(company[-2:-1][0]) >= 5 else "('陕西省人民医院，西安',710000)")
        else:
            perio_company_lists.append('(南京中医药大学附属医院,江苏南京,210029)')
        #期刊名称
        collegss = soup.select('.college')
        for college in collegss:
            collegss_per_page.append(college.text)
        #发表时间
        date = selector.xpath('//li/div[@class="info_right author"]/text()')
        if len(date) == 1 or len(date) == 2:
            date_lists.append(date[0].strip())
        elif len(date) == 3:
            date_lists.append(date[-2:-1][0].strip())
        elif len(date) > 3:
            date_lists.append(date[-3:-2][0].strip())
        else:
            date_lists.append('2016年12月01日')
        total = list(zip(title_lists, collegss_per_page,perio_auth_lists,perio_company_lists,date_lists, summary_lists))
    elif search_type == 'c':
        total = list(zip(title_lists, summary_lists))
    elif search_type == 'd':
        # 获取作者名称
        auth_names = soup.select('#card01')
        for i in auth_names:
            degree_auth_lists.append(i.text)
        # # 获取学校名称
        # first_name = selector.xpath('//*[@id="div_a"]/div/div[2]/div[1]/ul/li[4]/div[2]/a[1]/text()')
        # all_colleges.extend(first_name)
        university_name = selector.xpath('//li/div[@class="info_right"]/a[@href="javascript:void(0)"]/text()')
        all_colleges.append(tuple(university_name))
        # 获取学位信息
        d_pattern = re.compile('<div class="info_right author">([\u4e00-\u9fa5]+)</div>')
        d_name = re.search(d_pattern,res.text)
        degree_lists.append(d_name.group(1))
        # 获取授予学位的时间
        dtime_pattern = re.compile('<div class="info_right author">(\d{4})</div>')
        d_time = re.search(dtime_pattern,res.text)
        dtime_lists.append(d_time.group(1))
        total = list(zip(title_lists,degree_auth_lists,all_colleges,degree_lists,dtime_lists,summary_lists))
    else:
        total = list(zip(title_lists, summary_lists))
    return total


def main():
    while True:
        try:
            key_word = input('请输入要检索的关键词(例如：四轴飞行器):')
            type = input('请选择论文类别(p:期刊论文 c：会议论文 d：学位论文 a:综合)：')
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
            # 构造所有的url，分别进行每页url的获取，结果保存到列表
            for i in range(start_page, int(start_page + page_num)):
                new_url = base_url.format(i, key_word)
                all_page_urllists = get_url(new_url, type)
            # 遍历url列表，对每个网页解析，获取信息
            for j in all_page_urllists:
                total = get_info(j, type)
                time.sleep(3)
            df = pandas.DataFrame(total)
            df.to_excel(file_name + '.xlsx')
            df.to_csv('a.csv')
        except Exception as e:
            print(e)
        else:
            main()
        # 结果保存到Excel 中


if __name__ == "__main__":

    print("""
                .-~~~~~~~~~-._       _.-~~~~~~~~~-.
            __.'              ~.   .~              `.__
          .'//                  \./                  \ \`.
        .'//                     |                     \ \`.
      .'// .-~"""""""~~~~-._     |     _,-~~~~"""""""~-.            \ \`.
    .'//.-"                 `-.  |  .-'                 "-.\ \`.
  .'//______.============-..   \ | /   ..-============.______\ \`.
.'______________________________\|/______________________________`.

--------------------------论文摘要分类爬取脚本-------------------------
Auth:                                                       DX.Ssssss
DateTime:                                                  2018-03-23
Version:                                                        2.3.V
Tips:有爬虫需求的可以联系我。
-----------------------------------------------------------------------
    """)
    main()
    print('Success!')