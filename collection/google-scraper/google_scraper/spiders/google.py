# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
import json
from datetime import datetime
# Insert Scraperapi API key here. Signup here for free trial with 1,000 requests: https://www.scraperapi.com/signup
API_KEY = 'ENTER-API-KEY-HERE'


def get_url(url):
    payload = {'api_key': API_KEY, 'url': url,
               'autoparse': 'true', 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


def create_google_url(query, site=''):
    google_dict = {'q': query, 'num': 100, }
    if site:
        web = urlparse(site).netloc
        google_dict['as_sitesearch'] = web
        return 'https://www.google.com/search?' + urlencode(google_dict)
    return 'https://www.google.com/search?' + urlencode(google_dict)


class GoogleSpider(scrapy.Spider):
    name = 'google'
    allowed_domains = ['api.scraperapi.com']
    custom_settings = {'ROBOTSTXT_OBEY': False, 'LOG_LEVEL': 'INFO',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
                       'RETRY_TIMES': 5}

    def start_requests(self):
        # Enter keywords
        queries = [
            'essayoneday.com', 'essaypro.com', 'essayontime.com',
            'proessaywriting.com', 'essayassist.com', 'power-essays.com',
            'bestessays.com', 'a-writer.com', 'reviewingwriting.com',
            'write-paper-for-me.online', 'iqessay.com', 'lowriting.com',
            'cheapapers.com', 'urpapers.com', 'essaypro.me', 'paperwriting.online',
            'essaytown.com','rushessay.com','superiorpapers.com',
            'termpaperscorner.com','masterpaper.com','bestdissertation.com',
            'paper-helper.com', 'superbpapers.com'
        ]

        edu_param = 'site:*.edu/* -academia.edu '
        for query in queries:
            query = edu_param+'\"'+query+'\"'

            url = create_google_url(query)
            
            yield scrapy.Request(get_url(url),
                                  callback=self.parse,
                                  meta={
                                    'pos': 0,
                                    'url': query[29:]
                                  }
                                )

    def parse(self, response):
        di = json.loads(response.text)
        pos = response.meta['pos']
        q_url = response.meta['url']
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for result in di['organic_results']:
            title = result['title']
            snippet = result['snippet']
            link = result['link']
            item = {
              'target_pm': q_url,
              'title': title, 
              'snippet': snippet,
              'link': link, 
              'position': pos, 
              'date': dt
            }
            pos += 1
            yield item
        
        next_page = di['pagination']['nextPageUrl']
        
        if next_page:
            yield scrapy.Request(get_url(next_page),
                                  callback=self.parse, 
                                  meta={
                                    'pos': pos,
                                    'url': q_url
                                })
