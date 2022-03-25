# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
import json
import pandas as pd
from datetime import datetime

# Insert Scraperapi API key here. Signup here for free trial with 1,000 requests: 
# https://www.scraperapi.com/signup
API_KEY = 'ENTER_KEY'

# Import Canadian university list, since they do not use .edu
__ca_unis_file__ = '../../data/metadata/canadian_heis.csv'

list_of_ca_unis = pd.read_csv(__ca_unis_file__, delimiter=',')

clean_ca_url_list = list_of_ca_unis['clean_url'].to_list()

def get_url(url):
    
    payload = {
        'api_key': API_KEY, 
        'url': url,
        'autoparse': 'true',
        'country_code': 'ca'
    }

    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    
    return proxy_url


def create_google_url(query, papermill, site=''):
    
    google_dict = {
        'q': query,
        'num': 10,
        'exactTerms': papermill
    }

    if site:
        web = urlparse(site).netloc
        google_dict['as_sitesearch'] = web
        
        return 'https://www.google.com/search?' + urlencode(google_dict)
    
    return 'https://www.google.com/search?' + urlencode(google_dict)


class GoogleSpider(scrapy.Spider):
    name = 'google_ca'
    allowed_domains = ['api.scraperapi.com']
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'RETRY_TIMES': 5
    }

    def start_requests(self):
        # Enter papermill keywords
        papermills = [
            'essayoneday.com', 'essaypro.com', 'essayontime.com', 'essaypro.me',
            'proessaywriting.com', 'essayassist.com', 'power-essays.com', 'essayauthor.com',
            'bestessays.com', 'a-writer.com', 'reviewingwriting.com',
            'write-paper-for-me.online', 'iqessay.com', 'lowriting.com',
            'cheapapers.com', 'urpapers.com', 'paperwriting.online',
            'essaytown.com','rushessay.com','superiorpapers.com',
            'termpaperscorner.com','masterpaper.com','bestdissertation.com',
            'dissertationhelp.com','paper-helper.com', 'superbpapers.com'
        ]

        # Loop thru each uni, then each papermill to build full query for Request
        for cau in clean_ca_url_list:

            edu_param = 'site:'+cau+' -academia.edu '
            
            for pm_param in papermills:

                query = edu_param+'\"'+pm_param+'\"'

                # stripped_url_value = query.split('\"')[1].strip()

                url = create_google_url(query, pm_param)

                # Review status
                print(url)
                
                yield scrapy.Request(
                    get_url(url),
                    callback=self.parse,
                    meta={
                        'pos': 0,
                        'url': pm_param
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
            yield scrapy.Request(
                get_url(next_page),
                callback=self.parse,
                meta={
                    'pos': pos,
                    'url': q_url
                })
