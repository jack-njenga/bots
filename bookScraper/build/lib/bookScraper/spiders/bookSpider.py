import scrapy, random
from urllib.parse import urlencode
from bookScraper.items import BookscraperItem


def get_proxy_url(url):
    payload = {"api_key": "API_KEY", "url": url, 'render_js': 'true',}
    proxy_url = "https://proxy.scrapeops.io/v1/?" + urlencode(payload)
    return proxy_url


class BookspiderSpider(scrapy.Spider):
    name = "bookSpider"
    allowed_domains = ["books.toscrape.com", "proxy.scrapeops.io"]
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {
        "FEEDS": {
            "new_books_data.json": {"format": "json", "overwite": True}
        }
    }

    # def start_requests(self):
    #     yield scrapy.Request(url=get_proxy_url(self.start_urls[0]), callback=self.parse)

    def parse(self, response):
        """
        Scrapes all books
        """
        books = response.css("article.product_pod")
        books = books[0:5]

        print(f"\n\n\n\t{'*'*10} Length of books : {len(books)} {'*'*10}\n\n\n")
        for book in books:
            book_url = book.css('h3 a::attr(href)').get()

            if "catalogue/" in book_url:
                book_url = "https://books.toscrape.com/" + book_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + book_url
            # book_url = get_proxy_url(book_url)
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            if "catalogue/" in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page
            # next_page_url = get_proxy_url(next_page_url)         
            # yield response.follow(next_page_url, callback=self.parse)


    def parse_book(self, response):
        """
        Scrapes each books page
        """
        title = response.css("div.product_main h1::text").get()
        price = response.css("p.price_color::text").get()
        availability = response.css("p.instock.availability::text").getall()
        availability = " ".join([line.strip() for line in availability if line.strip()])  # Clean whitespace
        rating = response.css("p.star-rating::attr(class)").get().split()[-1]  # Extract rating class
        description = response.css("#product_description ~ p::text").get()  # Description comes after #product_description header

        product_info = {}
        rows = response.css("table.table.table-striped tr")

        for row in rows:
            key = row.css("th::text").get().strip()
            value = row.css("td::text").get().strip()
            product_info[key] = value

        bookItems = BookscraperItem()

        bookItems["title"] = title
        bookItems["price"] = price
        bookItems["availability"] = availability
        bookItems["rating"] = rating
        bookItems["description"] = description
        bookItems["product_info"] = product_info

        yield bookItems

