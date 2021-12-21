"""Spider to extract URL's of books from a Listopia list on Goodreads"""

import scrapy

from .book_spider import BookSpider

GOODREADS_URL_PREFIX = "https://www.goodreads.com/review/list/62446163-patrick-walsh?utf8=%E2%9C%93&utf8=%E2%9C%93&ref=nav_mybooks&title=patrick-walsh&per_page=infinite"
#"https://www.goodreads.com/review/list/62446163-patrick-walsh?utf8=%E2%9C%93&ref=nav_mybooks&per_page=100"
#GOODREADS_URL_PREFIX = "https://www.goodreads.com"

class ListSpider(scrapy.Spider):
    """Extract URLs of books from a Listopia list on Goodreads

        This subsequently passes on the URLs to BookSpider
    """
    name = "list3"

    ##"https://www.goodreads.com/list/show/1.Best_Books_ever?page=1"
    goodreads_list_url = "https://www.goodreads.com/review/list/62446163-patrick-walsh?utf8=%E2%9C%93&utf8=%E2%9C%93&ref=nav_mybooks&title=patrick-walsh&per_page=100"
    #goodreads_list_url = "https://www.goodreads.com/list/show/{}?page={}"

    def __init__(self):
        #__init__(self, list_name, start_page_no, end_page_no):
        super().__init__()
        self.book_spider = BookSpider()

        self.start_urls = []
        for page_no in range(int(1), int(1) + 1):
        #for page_no in range(int(start_page_no), int(end_page_no) + 1):
            list_url = self.goodreads_list_url
            self.start_urls.append(list_url)
            #list_url = self.goodreads_list_url.format(list_name, page_no)
            #self.start_urls.append(list_url)

    def parse(self, response):
        list_of_books = response.css("a.bookTitle::attr(href)").extract()

        for book in list_of_books:
            yield response.follow(book, callback=self.book_spider.parse)
