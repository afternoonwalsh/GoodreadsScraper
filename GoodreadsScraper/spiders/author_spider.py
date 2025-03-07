# Modified version of havanagrawal's original Goodreads Scraper: https://github.com/havanagrawal/GoodreadsScraper

"""Spider to extract information from a /author/show page"""

import scrapy

from ..items import AuthorItem, AuthorLoader

class AuthorSpider(scrapy.Spider):
    name = "author"

    def __init__(self, author_crawl="False"):
        # The default arg for author_crawl is intentionally a string
        # since command line arguments to scrapy are strings
        super().__init__()
        self.author_crawl = author_crawl.lower() in {"true", "yes", "y"}
        open("author_.jl",'w').close()
        if self.author_crawl:
            self.start_urls = ["https://www.goodreads.com/review/list/62446163?ref=nav_mybooks"]

    def parse(self, response):
        url = response.request.url

        # Don't follow blog pages
        if "/blog?page=" in url:
            return

        #if url.startswith("https://www.goodreads.com/review/list/62446163?ref=nav_mybooks/"):
        if url.startswith("https://www.goodreads.com/author/show/"):
            yield self.parse_author(response)

        # Exit early if an author crawl is not enabled
        if not self.author_crawl:
            return

        # If an author crawl is enabled, we crawl similar authors for this author,
        # authors that influenced this author,
        # as well as any URL that looks like an author bio page
        influence_author_urls = response.css('div.dataItem>span>a[href*="/author/show"]::attr(href)').extract()

        for author_url in influence_author_urls:
            yield response.follow(author_url, callback=self.parse)

        similar_authors = response.css('a[href*="/author/similar"]::attr(href)').extract_first()
        if similar_authors:
            yield response.follow(similar_authors, callback=self.parse)

        all_authors_on_this_page = response.css('a[href*="/author/show"]::attr(href)').extract()
        for author_url in all_authors_on_this_page:
            yield response.follow(author_url, callback=self.parse)

    def parse_author(self, response):
        loader = AuthorLoader(AuthorItem(), response=response)
        loader.add_value('url', response.request.url)
        loader.add_css("name", 'h1.authorName>span[itemprop="name"]::text')

        loader.add_css("birth_date", 'div.dataItem[itemprop="birthDate"]::text')
        loader.add_css("death_date", 'div.dataItem[itemprop="deathDate"]::text')

        loader.add_css("genres", 'div.dataItem>a[href*="/genres/"]::text')
        loader.add_css("influences", 'div.dataItem>span>a[href*="/author/show"]::text')

        loader.add_css("avg_rating", 'span.average[itemprop="ratingValue"]::text')
        loader.add_css("num_reviews", 'span[itemprop="reviewCount"]::attr(content)')
        loader.add_css("num_ratings", 'span[itemprop="ratingCount"]::attr(content)')

        loader.add_css("about", 'div.aboutAuthorInfo')

        loader.add_css('img_url', 'img[itemprop="image"]::attr(src)')
        loader.add_xpath('birthplace','/html/body/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/text()[5]')

        return loader.load_item()
