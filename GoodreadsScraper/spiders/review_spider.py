"""Spider to extract information from reviews on My Books page"""

import scrapy
from ..items import ReviewItem, ReviewLoader

class ReviewSpider(scrapy.Spider):
    """Extract information from a MyBooks type page on Goodreads"""
    name = "review"

    def __init__(self):
        super().__init__()
        open("review_.jl",'w').close()
        self.start_urls = ['https://www.goodreads.com/review/list/62446163-patrick-walsh?order=d&ref=nav_mybooks&shelf=read','https://www.goodreads.com/review/list/62446163-patrick-walsh?order=d&ref=nav_mybooks&shelf=to-read','https://www.goodreads.com/review/list/62446163-patrick-walsh?order=d&ref=nav_mybooks&shelf=currently-reading']

    def parse(self, response):
        list_of_shelvings = response.css('tr[id^="review_"]')


        for shelving in list_of_shelvings:
            loader = ReviewLoader(item = ReviewItem(), selector = shelving)

            loader.add_css('url',".title a::attr(href)")
            loader.add_css('my_rating', 'tr .field.rating span[class^="staticStar"]::text')
            loader.add_css('my_review_date_read',".date_read_value::text")
            loader.add_css('my_review_date_added',".field.date_added>div>span::attr(title)")
            loader.add_value('shelf',response.request.url)

            yield loader.load_item()

        next_page = response.css('a.next_page').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)