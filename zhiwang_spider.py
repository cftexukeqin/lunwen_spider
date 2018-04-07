import time

url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1521718476297&keyValue=%E9%92%88%E7%81%B8&S=1&DisplayMode=custommode"
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
login_url = "http://kns.cnki.net/kns/logindigital.aspx?ParentLocation=http://www.cnki.net"
driver = webdriver.Chrome()

driver.get(login_url)
wait = WebDriverWait(driver, 10)
def login():
    userInput =wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
    )
    pwdInput = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#password')))

    userInput.send_keys('18220568578')
    pwdInput.send_keys('12354abcs')

    login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#submittext')))

    login_btn.click()
def get_zy():
    search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#txt_SearchText')))
    search_input.send_keys('针灸')

    search_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > div.wrapper.section1 > div.searchmain > div > div.input-box > input.search-btn')))
    search_btn.click()

def get_info():
    driver.switch_to.frame('iframeResult')
    time.sleep(3)
    title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#ctl00 > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > a')))
    print(title['href'])
    # doc = pq(html)
    # items = doc('.GridContent GridSingleRow GridRightColumn')
    # for item in items:
    #     cpu_info = {
    #         'image':item.find('.pic .img').attr('data-src'),
    #         'price':item.find('.price').text().split('\n')[1],
    #         'deal':item.find('.deal-cnt').text()[:-3],
    #         'name':item.find('.title').text(),
    #         'shop':item.find('.shop').text(),
    #         'location':item.find('.location').text()
    #     }
    #     yield cpu_info
    # print(items)

# def get_onepage_info():
#     title =

def main():
    login()
    get_zy()
    get_info()


if __name__ == '__main__':
    main()