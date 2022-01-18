# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re
import datetime

import scrapy
from scrapy import Field
from scrapy.loader import ItemLoader

from scrapy.loader.processors import Identity, Compose, MapCompose, TakeFirst, Join

from dateutil.parser import parse as dateutil_parse
from w3lib.html import remove_tags


def num_page_extractor(num_pages):
    if num_pages:
        return num_pages.split()[0]
    return None


def safe_parse_date(date):
    try:
        date = dateutil_parse(date, fuzzy=True, default=datetime.datetime.min)
        date = date.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        date = None

    return date


def extract_publish_dates(maybe_dates):
    maybe_dates = [s for s in maybe_dates if "published" in s.lower()]
    return [safe_parse_date(date) for date in maybe_dates]


def extract_year(s):
    s = s.lower().strip()
    match = re.match(".*first published.*(\d{4})", s)
    if match:
        return match.group(1)


def extract_ratings(txt):
    """Extract the rating histogram from embedded Javascript code

        The embedded code looks like this:

        |----------------------------------------------------------|
        | renderRatingGraph([6, 3, 2, 2, 1]);                      |
        | if ($('rating_details')) {                               |
        |   $('rating_details').insert({top: $('rating_graph')})   |
        |  }                                                       |
        |----------------------------------------------------------|
    """
    codelines = "".join(txt).split(";")
    rating_code = [line.strip() for line in codelines if "renderRatingGraph" in line]
    if not rating_code:
        return None
    rating_code = rating_code[0]
    rating_array = rating_code[rating_code.index("[") + 1 : rating_code.index("]")]
    ratings = {5 - i:int(x) for i, x in enumerate(rating_array.split(","))}
    return ratings


def filter_asin(asin):
    if asin and len(str(asin)) == 10:
        return asin
    return None


def isbn_filter(isbn):
    if isbn and len(str(isbn)) == 10 and isbn.isdigit():
        return isbn


def isbn13_filter(isbn):
    if isbn and len(str(isbn)) == 13 and isbn.isdigit():
        return isbn


def filter_empty(vals):
    return [v.strip() for v in vals if v.strip()]


def split_by_newline(txt):
    return txt.split("\n")

def extract_my_review(txt):
    #txt = str(txt) 
    #txt = re.search('(?<="display:none">).*?(?=<\/span)',str(txt))#.group(0)
    empty_review_text = '<td class="field review" style="display: none"><label>review</label><div class="value">\n            <span class="greyText">None</span>\n    <div class="clear"></div>\n</div></td>'
    #free_text = 'freeTextreview'
    #txt1 = re.search('.*?',str(txt)).group(0)
    #txt1 = re.search('(?<="freeTextContainerreview\d\d\d\d\d\d\d\d\d\d">).*?(?=<\/span)',str(txt)).group(0)
    #return txt1

    if empty_review_text not in txt:
        try:
            #txt = txt[0]
            txt = re.search('(?<="display:none">).*?(?=<\/span)',str(txt)).group(0)
            return txt.strip #.group(0)
        except:
            txt = re.search('(?<="freeTextContainerreview\d\d\d\d\d\d\d\d\d\d">).*?(?=<\/span)',str(txt)).group(0)
            return txt.strip       
    else:
         return 'not reviewed'

    #     if empty_review_text not in txt:
    #     if free_text in txt:
    #         #txt = txt[0]
    #         txt = re.search('(?<="display:none">).*?(?=<\/span)',str(txt)).group(0)
    #         return txt #.group(0)
    #     else:
    #         txt = re.search('(?<="freeTextContainerreview\d\d\d\d\d\d\d\d\d\d">).*?(?=<\/span)',str(txt)).group(0)
    #         #return "bb" #txt
    # else:
    #     return 'not reviewed'

def extract_my_rating(txt):
    if txt:
        #txt = txt[0]
        #re.search('(?<=>).*(?=<)',txt)
        return txt #.group(0)
    else:
        return 'not rated'

def extract_shelf(url):
    if url:
        url1 = url[0].split("=")
        url2 = url1[-1]
        return url2
    else:
        return 'none'

# def extract_shelf_list(lst):
#     url_prefix = 'https://www.goodreads.com/'
#     for shelf in lst:
#         shelf_url = url_prefix + re.match(,shelf).group(0)

class BookItem(scrapy.Item):
    # Scalars
    url = Field()

    title = Field(input_processor=MapCompose(str.strip))
    author = Field(input_processor=MapCompose(str.strip))

    num_ratings = Field(input_processor=MapCompose(str.strip, int))
    num_reviews = Field(input_processor=MapCompose(str.strip, int))
    avg_rating = Field(input_processor=MapCompose(str.strip, float))
    num_pages = Field(input_processor=MapCompose(str.strip, num_page_extractor, int))

    language = Field(input_processor=MapCompose(str.strip))
    publish_date = Field(input_processor=extract_publish_dates)

    original_publish_year = Field(input_processor=MapCompose(extract_year, int))

    isbn = Field(input_processor=MapCompose(str.strip, isbn_filter))
    isbn13 = Field(input_processor=MapCompose(str.strip, isbn13_filter))
    asin = Field(input_processor=MapCompose(filter_asin))

    series = Field()

    # Lists
    awards = Field(output_processor=Identity())
    places = Field(output_processor=Identity())
    characters = Field(output_processor=Identity())
    genres = Field(output_processor=Compose(set, list))


    # Dicts
    rating_histogram = Field(input_processor=MapCompose(extract_ratings))

    img_url = Field()


class BookLoader(ItemLoader):
    default_output_processor = TakeFirst()

class AuthorItem(scrapy.Item):
    # Scalars
    url = Field()

    name = Field()
    birth_date = Field(input_processor=MapCompose(safe_parse_date))
    death_date = Field(input_processor=MapCompose(safe_parse_date))

    avg_rating = Field(serializer=float)
    num_ratings = Field(serializer=int)
    num_reviews = Field(serializer=int)

    # Lists
    genres = Field(output_processor=Compose(set, list))
    influences = Field(output_processor=Compose(set, list))

    # Blobs
    about = Field(
        # Take the first match, remove HTML tags, convert to list of lines, remove empty lines, remove the "edit data" prefix
        input_processor=Compose(TakeFirst(), remove_tags, split_by_newline, filter_empty, lambda s: s[1:]),
        output_processor=Join()
    )

    img_url = Field()
    birthplace = Field(input_processor=MapCompose(str.strip))

class AuthorLoader(ItemLoader):
    default_output_processor = TakeFirst()

class ReviewItem(scrapy.Item):
    url = Field()
    my_rating = Field() #Field(input_processor=extract_my_rating) #str.strip, num_page_extractor, int)
    #my_shelves = Field(output_processor=Identity())
    my_review = Field(input_processor=extract_my_review)
    my_review_1 = Field()
    my_review_date_read = Field(input_processor=MapCompose(safe_parse_date))
    my_review_date_added = Field(input_processor=MapCompose(safe_parse_date))
    #my_review_date_read_1 = Field()
    shelf = Field(input_processor=extract_shelf)

class ReviewLoader(ItemLoader):
    default_output_processor = TakeFirst()
