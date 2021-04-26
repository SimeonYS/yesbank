import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import YesbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class YesbankSpider(scrapy.Spider):
	name = 'yesbank'
	start_urls = ['https://www.yesbank.in/about-us/media/press-releases']

	def parse(self, response):
		years = response.xpath('//select[@id="dun"]/option/@value').getall()[1:]
		months = response.xpath('//select[@id="month"]/option/@value').getall()[1:]

		for year in years:
			for month in months:
				link = f'https://www.yesbank.in/pressreleaseslinkgenerating&selectval={year}&selectMonth={month}'
				yield response.follow(link, self.parse_links)

	def parse_links(self, response):
		post_links = response.xpath('//a/@href').getall()
		post_links = [link for link in post_links if not "javascript:;" in link]
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//div[@class="content"]//p').getall()[:5]
		date = re.findall(r'\w+\s\d+\,\s\d+',' '.join(date)) or re.findall(r'\d+\-\w+\-\d+',' '.join(date))
		title = response.xpath('(//h2)[last()]/text()').get()
		content = response.xpath('//div[@class="content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=YesbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
