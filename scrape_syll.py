import sys
import re
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm


def main():
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--disable-gpu')
	#location of chrome.exe
	options.binary_location=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
	#location of chromedriver
	driver=webdriver.Chrome(chrome_options=options,executable_path=r'C:\chromedriver_win32\chromedriver.exe')
	driver.set_window_size(900,1600)
	urls=navigate(driver)
	time.sleep(1)
	posts=scrape_posts(driver,urls)
	print('Writing...',file=sys.stderr)
	with open('lecture_list.csv','w',encoding='utf-8',newline='') as f:
		writer=csv.writer(f)
		for key in posts.keys():
			writer.writerow([key])
			for list in posts[key]:
				writer.writerow(list)
		
def navigate(driver):
	print('Navigation...',file=sys.stderr)
	driver.get('https://risyu.jmk.ynu.ac.jp/gakumu/Public/Syllabus/')
	assert '横浜国立大学シラバス' in driver.title
	
	select=Select(driver.find_elements_by_id("ctl00_phContents_ddl_fac")[0])
	select.select_by_visible_text('理工学部')
	driver.find_elements_by_id('ctl00_phContents_btnSearch')[0].click()
	time.sleep(3)
	select=Select(driver.find_elements_by_id('ctl00_phContents_ucGrid_ddlLines')[0])
	select.select_by_visible_text("全件")
	urls=[]
	for a in driver.find_elements_by_tag_name('a'):
		url=a.get_attribute('href')
		if not url:
			pass
		elif re.search(r'https://risyu.jmk.ynu.ac.jp/gakumu/Public/Syllabus/DetailMain.*je_cd=1',url):
			urls.append(url)
	return urls
	
	
def scrape_posts(driver,urls):
	posts={
		'free':[],
		'report':[],
		'test':[],
	}
	wait=WebDriverWait(driver,10)
	print('Scraping...',file=sys.stderr)
	for url in tqdm(urls):
		time.sleep(1)
		driver.get(url)
		element=wait.until(EC.presence_of_element_located((By.ID, "ctl00_phContents_sylSummary_txtSbjName")))
		html=driver.page_source
		parser(html,posts)
	return posts
	
def parser(html,posts):
	soup=BeautifulSoup(html,'html.parser')
	lct_num=soup.find(id='ctl00_phContents_sylSummary_txtLctCd').text
	name=soup.find(id='ctl00_phContents_sylSummary_txtSbjName').text
	report=re.findall('..レポート..',html)
	exam=re.findall('..試験..',html)
	test=re.findall('.[^小]テスト..',html)
	if not (report or exam or test):
		posts['free'].append([lct_num,name,[report,exam,test]])
	if report:
		posts['report'].append([lct_num,name,report])
	if exam or test:
		posts['test'].append([lct_num,name,[exam,test]])
	
if __name__=='__main__':
	main()