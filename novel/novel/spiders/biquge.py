# -*- coding: utf-8 -*-
from scrapy import Spider,Request
from ..items import NovelItem
import copy



class BiqugeSpider(Spider):
    name = "biquge"
    allowed_domains = []
    allstart_urls = ['https://www.qu.la/paihangbang/']
    otherurls = ['https://www.qu.la/book/4140/']
    start_urls = ['https://www.qu.la/book/4140/2585313.html']

    def start_requests(self):
        yield Request(self.allstart_urls[0],callback=self.allparse)
        # yield Request(self.start_urls[0],callback=self.parse)
        # yield Request(self.otherurls[0], callback=self.otherparse)

    def allparse(self,response):
        urls = response.xpath('.//div[@class="topbooks"]//li//@href').extract()
        for url in urls:
            au = str(url)
            url = response.urljoin(url)
            yield Request(url=url,meta={'au':copy.deepcopy(au)},callback=self.otherparse)

    def otherparse(self,response):
        urls = response.xpath('.//div[@id="list"]//dd//@href').extract()
        for url in urls:
            url = response.urljoin(url)
            au = response.meta['au']
            yield Request(url=url,meta={'au':copy.deepcopy(au)},callback=self.parse)

    def parse(self, response):
        item = NovelItem()
        try:
            title = response.xpath('.//div[@class="bookname"]//h1//text()').extract()[0]
        except:
            title = ''
        content = '\n'.join(response.xpath('.//div[@id="content"]//text()').extract()[:-2])
        item['au'] = response.meta['au']
        print(item['au'] + '********')
        item['title'] = title
        item['content'] = content
        url = response.xpath('.//div[@class="bottem1"]//a[@id="pager_next"]//@href').extract()[0]
        url = response.urljoin(url)
        yield item

        print(title)
        yield Request(url=url,callback=self.parse)
