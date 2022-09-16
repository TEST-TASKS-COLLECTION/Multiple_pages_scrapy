import profile
import scrapy
from ..items import DataWebItem

class MrdataSpider(scrapy.Spider):
    name = 'mrdata'
    allowed_domains = ['salonlofts.com']
    main_urls = ['https://salonlofts.com']
    start_urls = ['https://salonlofts.com/salons/in/tampa_bay_area']
    parts = ["hair", "nail", "skin", "massage"]

    def parse(self, response):
        # print(response.text)
        #  https://salonlofts.com/salons/in/tampa_bay_area
        cities = response.css("select.form-control > option::text").getall()[1:]
        url_cities = [self.main_urls[0]+f"/salons/in/{c.split('-')[1].strip().lower().replace(' ', '_')}" for c in cities]
        # print("*"*15)
        # print(cities)
        # print(url_cities)
        # print("*"*15)
        for i, url in enumerate(url_cities):
            yield response.follow(url, callback=self.parse_city, headers={"state": cities[i]}, meta={'state': cities[i]})
        
    def parse_city(self, response):
        # https://salonlofts.com/salons/virginia_gateway
        # print("referer city in parse_city is", response.request.headers.get("state"))
        # print(response.request.meta.get("state"), "pikachu huna parxa  hai")
        # state = response.request.headers.get("state")
        state = response.request.meta.get("state")
        roads_temp_url = response.css("li.store-details > a::attr('href')").getall() 
        addr_1 = [i.strip() for i in response.css("div.address-1::text").getall()]
        addr_2 = [i.strip() for i in response.css("div.address-2::text").getall()]
        # print("*"* 15)
        # print("in state", state)
        # print("Address 1 is:", addr_1)
        # print("Address 2 is:", addr_2)
        # print("*"* 15)
        roads_url = [self.main_urls[0]+f"{road}" for road in roads_temp_url]
        for r_url in roads_url:
            yield response.follow(r_url, callback=self.parse_within_data, meta={"state": state, "addr_1": addr_1, "addr_2": addr_2, "r_url": r_url})
        # pass
    # https://salonlofts.com/salons/salons/clarendon
    # https://salonlofts.com/salons/clarendon
    def parse_within_data(self, response):
        # https://salonlofts.com/salons/clarendon/hair
        # https://www.salon-concepts.com/salon/uptown
        state = response.request.meta.get("state")
        addr_1 = response.request.meta.get("addr_1")
        addr_2 = response.request.meta.get("addr_2")
        r_url = response.request.meta.get("r_url") # https://salonlofts.com/salons/eden_prairie
        # print("*"*15)
        # print(response.request.meta)
        # print("THE REFERER URL IS:")
        # print("*"*15)
        # url = f"{response.request.meta.get('redirect_urls')[0]}"
        for s_type in self.parts:
            f_url = r_url+f"/{s_type}"
            # print("*"*15)
            # print("THE REFERER URL IS:", f_url)
            # print("also the r_url is:", r_url)
            # print("*"*15)
            yield response.follow(f_url, callback=self.parse_type, meta={"state": state, "addr_1": addr_1, "addr_2": addr_2, "s_type": s_type, "url": f_url})
    
    def parse_type(self, response):
        # print("*"*21)
        # print("in parse type, the url is", response.request.meta.get("url"))
        # print("*"*21)
        state = response.request.meta.get("state")
        addr_1 = response.request.meta.get("addr_1")
        addr_2 = response.request.meta.get("addr_2")
        s_type = response.request.meta.get("s_type")
        url = response.request.meta.get("url")
        if response.css("div.stylist-phone") and response.css("div.stylist-email"):
            item = DataWebItem()
            item['state'] = state
            item['addr_1'] = addr_1
            item['addr_2'] = addr_2
            item['s_type'] = s_type
            ph_nums = response.css("div.stylist::attr('data-phone')").getall()
            names =  response.css("div.stylist::attr('data-name')").getall()
            emails = response.css("div.stylist-email a::text").getall()
            for p, n, e in zip(ph_nums, names, emails) :
                item['ph_num'] = p
                item['name'] = n
                item['email'] = e
                yield item
        else:
            # https://salonlofts.com/anna_tkacheva
            # /luxuryiv_hydration
            profile_urls = [f"{self.main_urls[0]}{i.strip()}" for i in response.css("a.view-my-profile-link::attr('href')").getall()]
            for profile in profile_urls:
                yield response.follow(profile, callback=self.parse_person, meta={"state": state, "addr_1": addr_1, "addr_2": addr_2, "s_type": s_type})

            # yield response.follow(url+f"/{s_type}", callback=self.parse_type, meta={"state": state, "addr_1": addr_1, "addr_2": addr_2, "s_type": s_type})
    
    def parse_person(self, response):
        state = response.request.meta.get("state")
        addr_1 = response.request.meta.get("addr_1")
        addr_2 = response.request.meta.get("addr_2")
        s_type = response.request.meta.get("s_type")
        # url = response.request.meta.get("url")
        item = DataWebItem()
        item['state'] = state
        item['addr_1'] = addr_1
        item['addr_2'] = addr_2
        item['s_type'] = s_type
        if response.css("div.book-online-link p::text").get():
            item['ph_num'] = response.css("div.book-online-link p::text").get().split("Call")[1].strip()
        else:
            item['ph_num'] = "NA"
        item['name'] = response.css("h1.loft-owner-name::text").get().strip()
        item['email'] = response.css("a.email-address::attr('href')").get().split(":")[1]
        yield item
        
