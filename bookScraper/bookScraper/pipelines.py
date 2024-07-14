# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
     def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        # print(f"\n{'*'*50}\n")
        # print(f"Adapter: {adapter}")
        # print(f"Field Names: {field_names}")
        for field_name in field_names:
            if field_name not in ['description', 'product_info']:
                value = adapter.get(field_name)
                # print(f"===> {field_name} : {value}")
                adapter[field_name] = value.strip()


        ## Price --> convert to float
        price_keys = ['price']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)


        ## Availability --> extract number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0])


        ## Stars --> convert text to number
        stars_string = adapter.get('rating')
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[0].lower()
        starts_map = {"zero": 0, "one": 1, "three": 3, "four": 4, "five": 5}
        adapter["rating"] = starts_map[stars_text_value]

        return item
