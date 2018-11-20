import scrapy
from urllib.parse import urlparse
import hashlib
import os, os.path
from scrapy.http import Request
from selenium import webdriver
from quote.items import SpeciallistItem
import time

class HaoDaiFuSpider(scrapy.spiders.Spider):
    name = "HaoDaiFu"
    #allowed_domains = ["www.haodf.com"]
    start_urls = ["http://www.haodf.com/keshi/list.htm"]

    def __init__(self):
        self.driver = webdriver.Chrome()
        start_urls = "http://www.haodf.com/keshi/list.htm"
        self.driver.get(start_urls)
        try:

            for i in range(0, 50):
                # 等待网站加载完成
                time.sleep(0.2)
                self.diver.find_elements_by_class_name('request_situ')[1].click()
        except:
            print
            '********************************************************'

    def __del__(self):
        self.driver.quit()

    def _url_params(self, url):
        result = urlparse.urlparse(url)
        return urlparse.parse_qs(result.query,True)

    def parse(self, response):
        print("hello")
        for sel in response.xpath("//div[@class='m_title_green']"):
            department = sel.xpath("span/text()").extract()[0]
            for sub in sel.xpath("following-sibling::div[1]/ul/li/a"):
                item = SpeciallistItem()
                item['department'] = department
                item['sub_department'] = sub.xpath("text()").extract()[0]
                print(item['sub_department'])
                url = sub.xpath("@href").extract()[0]
                department_url = "http://www.haodf.com" + url
                print(department_url)
                yield Request(department_url, callback=self.parse_more_department, meta = {'item': item})

    def parse_more_department(self, response):
        more_department_url = response.xpath("//table[@class='jblb']/tr[last()]/td[last()]/a/@href").extract()[0]
        print('more','http://' + more_department_url[2:])
        if (more_department_url):
            yield Request('http://'+ more_department_url[2:], callback=self.parse_hospital_department, meta = {'item': response.meta['item']})

    def parse_hospital_department(self, response):
        i = 0
        source_item = response.meta['item']
        department = source_item['department']
        sub_department = source_item['sub_department']
        yield source_item
#        for sel in response.xpath("//table[@class='hptj']/tr/td[@class='tuijian_diqu_tisheng_height25 tuijian_diqu_yisheng_space']/a"):
#            print('sel',sel)
#            if (i < 20):
#                item = SpeciallistItem()
#                item['department'] = department
#                item['sub_department'] = sub_department
#                item['hospital'] = sel.xpath("text()").extract()[0]
#                disease_url = sel.xpath("@href").extract()[0]
#                yield Request(disease_url, self.parse_disease, meta = {'item': item})
#                i += 1

    def parse_disease(self, response):
        source_item = response.meta['item']
        department = source_item['department']
        sub_department = source_item['sub_department']
        hospital = source_item['hospital']
        for sel in response.xpath("(//ul[@class='box_a-introList']|//ul[@class='box_a_otherList'])/li/a[@class='orange']"):
            item = SpeciallistItem()
            item['department'] = department
            # print(item['department'])
            item['sub_department'] = sub_department
            item['hospital'] = hospital
            item['disease'] = sel.xpath("text()").extract()[0]
            url = sel.xpath("@href").extract()[0]
            speciallist_url = "http://www.haodf.com" + url
            yield Request(speciallist_url, self.parse_speciallist, meta = {'item': item})


    def parse_speciallist(self, response):
        source_item = response.meta['item']
        department = source_item['department']
        sub_department = source_item['sub_department']
        hospital = source_item['hospital']
        disease = source_item['disease']
        for sel in response.xpath("//tr[@class='yy_jb_df2']"):
            item = SpeciallistItem()
            item['department'] = department
            item['sub_department'] = sub_department
            item['hospital'] = hospital
            item['disease'] = disease
            speciallist = sel.xpath("td[1]/table[@class='yy_jb_df3']//tr[1]/td[last()]/a[1]/text()").extract()[0]
            speciallist_info_url = sel.xpath("td[1]/table[@class='yy_jb_df3']//tr[1]/td[last()]/a[1]/@href").extract()[0]
            item['speciallist'] = speciallist
            self.driver.get(speciallist_info_url)
            response = response.replace(body = self.driver.page_source.replace("display:none", "display:block"))
            item['expert'] = response.xpath("id('full_DoctorSpecialize')/text()").extract()[0]
            avatar = response.xpath("id('bp_doctor_about')/div/div[2]/div/table[1]/tbody/tr[1]/td/div[1]/table/tbody/tr/td/img/@src")
            item['info'] = "".join(response.xpath("id('full')/text()").extract()[ : -1])
            if (not item['info']):
                item['info'] = response.xpath("id('bp_doctor_about')/div/div[2]/div/table[1]/tbody/tr[4]/td[3]/text()").extract()[0]
                if (avatar):
                    item['info'] = response.xpath("id('bp_doctor_about')/div/div[2]/div/table[1]/tbody/tr[5]/td[3]/text()").extract()[0]
            if (avatar):
                item['avatar'] = avatar.extract()[0]
                item['job_title'] = response.xpath("id('bp_doctor_about')/div/div[2]/div/table[1]/tbody/tr[3]/td[3]/text()").extract()[0]
            else:
                item['avatar'] = ''
                item['job_title'] = response.xpath("id('bp_doctor_about')/div/div[2]/div/table[1]/tbody/tr[2]/td[3]/text()").extract()[0]
            yield item
            # print(item)
