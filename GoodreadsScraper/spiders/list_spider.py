"""Spider to extract URL's of books from a Listopia list on Goodreads"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC
import os
import time
import math
import sys
import scrapy
from .book_spider import BookSpider

GOODREADS_URL_PREFIX = "https://www.goodreads.com"

class ListSpider(scrapy.Spider):
    """Extract URLs of books from a Listopia list on Goodreads
        This subsequently passes on the URLs to BookSpider
    """
    name = "list"

    goodreads_list_url = "https://www.goodreads.com/review/list/62446163?ref=nav_mybooks"

    def __init__(self):
        super().__init__()
        self.book_spider = BookSpider()

        self.start_urls = ['https://www.goodreads.com/review/list/62446163?ref=nav_mybooks']

    def parse(self, response):
        list_of_books = response.css("#booksBody .title a::attr(href)").extract()
        
        for book in list_of_books:
            yield response.follow(book, callback=self.book_spider.parse)

        next_page = response.css('a.next_page').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
