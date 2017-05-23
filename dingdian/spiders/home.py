# -*- coding: utf-8 -*-
import re
import scrapy  # 导入scrapy包
from bs4 import BeautifulSoup
from scrapy.http import Request  # 一个单独的request的模块，需要跟进URL的时候，需要用它
# 这是我定义的需要保存的字段，（导入dingdian项目中，items文件中的DingdianItem类）
from dingdian.items import DingdianItem

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Myspider(scrapy.Spider):
    # http://www.23us.com/class/2_1.html
    name = 'dingdian'
    allowed_domains = ['23us.com']
    bash_url = 'http://www.23us.com/class/'
    bashurl = '.html'

    def start_requests(self):
        for i in range(1, 11):
            url = self.bash_url + str(i) + '_1' + self.bashurl
            yield Request(url, self.parse)
        yield Request('http://www.23us.com/quanben/1', self.parse)

    def parse(self, response):
        print(response.url)
        max_num = BeautifulSoup(response.text, 'lxml').find(
            'div', class_='pagelink').find_all('a')[-1].get_text()
        bashurl = str(response.url)[:-7]
        for num in range(1, int(max_num)+1):
            url = bashurl + '_' + str(num) + self.bashurl
            # print('url:'+url)
            yield Request(url, callback=self.get_name)

    def get_name(self, response):
        tds = BeautifulSoup(response.text, 'lxml').find_all(
            'tr', bgcolor='#FFFFFF')
        for td in tds:
            novelname = td.find_all('a')[1].get_text()
            novelurl = td.find_all('a')[-1]['href']
            #print(novelname, novelurl)
            yield Request(novelurl, callback=self.get_chapterurl, meta={'name': novelname, 'url': novelurl})

    def get_chapterurl(self, response):
        item = DingdianItem()
        # 名字
        item['name'] = str(response.meta['name']).replace('\xa0', '')
        # 链接
        item['novelurl'] = response.meta['url']
        # 作者
        author = BeautifulSoup(response.text, 'lxml').find(
            'table').find_all('td')[1].get_text()
        item['author'] = str(author).replace('/', '')
        # category = BeautifulSoup(response.text, 'lxml').find(
        #     'table').find('a').get_text()
        # bash_url = BeautifulSoup(response.text, 'lxml').find(
        #     'p', class_='btnlinks').find('a', class_='read')['href']
        # name_id = str(bash_url)[-6:-1].replace('/', '')
        # item['category'] = str(category).replace('/', '')
        # item['name_id'] = name_id
        # print('作者：'+item['author'])
        return item