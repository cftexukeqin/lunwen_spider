import time

import requests
import json
from bs4 import BeautifulSoup as bs
import re
import pandas

url_lists =[]
total_lists = []
page_urls = []

def get_url(base_url):
    res = requests.get(base_url)
    content = json.loads(res.content)
    con = content['message']
    print(con)
    con = con.split('<ul class="prolist"><li><table><tr><th>')[1].split('...</td></tr></table></li></ul>')[0]
    # con
    pattren = re.compile('a href="/QK/(.*?)" target="_blank"')
    results = re.findall(pattren,con)
    for i in results:
        if i.endswith('.html'):
            url_lists.append('http://www.cqvip.com/QK/'+i)
    return url_lists
        
def get_info(url):
    res = requests.get(url)
    soup = bs(res.text,'lxml')
    title = soup.select('.detailtitle h1')[0]
    summary = soup.select('.sum')[1]
    total_lists.append((title.text,summary.text))
    return total_lists

def main():
    total_urls = []
    now = int(time.time())
    key_word = input('请输入要检索的论文关键字：')
    start_page = input('请输入检索起始页：')
    page_num = input('请输入要检索的页数：')
    base_url = "http://www.cqvip.com/data/main/search.aspx?action=so&tid=0&k={}w=&o=&mn=&issn=&cnno=&rid=0&c=&gch=&cnt=&curpage={}&perpage=0&ids=&valicode=&_="+str(now)

    for i in range(int(start_page),int(page_num + start_page)):
        new_url = base_url.format(key_word,i)
        total_urls = get_url(new_url)
    for url in total_urls:
        total_info = get_info(url)
    df = pandas.DataFrame(total_info)
    df.to_excel('a.xlsx')
    
    

if __name__ == "__main__":
    main()
    print('Success!')