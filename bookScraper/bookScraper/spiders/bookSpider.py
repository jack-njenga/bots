import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookSpider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        """
        Scrapes all books
        """
        books = response.css("article.product_pod")

        for book in books:
            book_url = f"https://books.toscrape.com/{book.css('h3 a::attr(href)').get()}"

            yield {
                "name": book.css("h3 a::text").get(),
                "price": book.css("div.product_price p::text").get(),
            }
        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            if "catalogue/" in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page
            
            yield response.follow(next_page_url, callback=self.parse)


    def parse_book(self, book_url, response):
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
            value = rows.css("td::text").get().strip()
            product_info[key] = value

        yield {
            "title": title,
            "price": price,
            "availability": availability,
            "rating": rating,
            "description": description,
            "product_info": product_info,
        }
