import os
from csv import DictWriter
import requests
from fake_useragent import UserAgent
import shutil
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
import urllib3
from urllib.parse import urlencode
urllib3.disable_warnings()
from urllib3.util import Retry
from urllib.parse import unquote
import PyPDF2
from PyPDF2.utils import PdfReadError
import re
import emoji
from pm_scraper.get_ua import get_ua_string

# Insert Scraperapi API key here. Signup here for free trial with 1,000 requests: 
# https://www.scraperapi.com/signup
API_KEY = 'ENTER_KEY'

# How to handle request retries/fails
retry_strategy = Retry(
  total=3,
  backoff_factor=10,#change if too many MaxRetryErrors
  status_forcelist=[429, 500, 502, 503, 504],
  method_whitelist=["HEAD", "GET", "OPTIONS"]
)

def get_url(url):
    
  payload = {
      'api_key': API_KEY, 
      'url': url,
      'autoparse': 'true'
      # 'country_code': 'ca'
  }

  proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
  
  return proxy_url

'''
SHARED FUNCTIONS
'''

def request_attack(url):
  '''
  Fulfills requests for all types of attack types
  '''
  # TODO: 
  #   - Proxy messing with PDF streaming
  #   - Bypass for now
  # proxy_url = get_url(url)
  proxy_url = url

  ua_string = get_ua_string()

  # Instantiate and mount adapter
  adapter = HTTPAdapter(max_retries=retry_strategy)
  http = requests.Session()
  http.mount("https://", adapter)
  http.mount("http://", adapter)

  response = http.get(
    proxy_url,
    verify=False,
    headers={
      'User-Agent': ua_string
    },
    stream=True,
    allow_redirects=True
    # timeout=None
  )

  try:

    # Test response and return
    response.raise_for_status()

    return response
    
  except requests.exceptions.HTTPError as http_e:

    print('\nError: ', str(http_e), '\n')
    
    return 'http_error'

  except urllib3.exceptions.ResponseError as re:

    print('\nError: ', str(re), '\n')
    
    return 'http_error'

  except requests.exceptions.Timeout as te:

    print('\nError: ', str(te), '\n')
    
    return 'timeout_error'

  except requests.exceptions.ConnectionError as ce:

    print('\nError: ', str(ce), '\n')
    
    return 'connection_error'

  except urllib3.exceptions.NewConnectionError as ce:

    print('\nError: ', str(ce), '\n')
    
    return 'connection_error'

  except requests.exceptions.RetryError as re:

    print('\nError: ', str(re), '\n')
    
    return 'retry_error'

  except urllib3.exceptions.MaxRetryError as mre:

    print('\nError: ', str(mre), '\n')
    
    return 'retry_error'
    
  except urllib3.exceptions.NewConnectionError as nce:
    
    print('\nError: ', str(nce), '\n')

    return 'new_connection_error'

  except urllib3.exceptions.ConnectTimeoutError as cte:
    
    print('\nError: ', str(cte), '\n')

    return 'timeout_error'

  except urllib3.exceptions.TimeoutError as ute:
    
    print('\nError: ', str(ute), '\n')

    return 'timeout_error'
  
  except Exception as ee:

    print('\n\ngeneral exception error: ', ee)
    
    return 'general_exception'

def append_to_csv(**kwargs):

  # Create new dict to update to existing row dict
  new_row_info = {
    'attack_type': kwargs['attack_type'],
    'status_code': kwargs['status_code'],
    'active_status': kwargs['active_status'],
    'raise_for_status': kwargs['raise_for_status'],
    'other_redirect_link': kwargs['other_redirect_link'],
   'link_context': kwargs['link_context'],
    'emojis': kwargs['emojis'],
    'page_type': kwargs['page_type']
  }

  # Update to current and pre-existing row
  for new_item_key in new_row_info:

    kwargs['current_row'].update({
      new_item_key: new_row_info[new_item_key]
    })

  print('Row to write: ', kwargs['current_row'])
  
  # Write to CSV
  field_names = [
    'index','target_pm','title','snippet','link','position',
    'date','attack_type','status_code','active_status',
    'raise_for_status','other_redirect_link','link_context','emojis','page_type'
  ]

  with open(kwargs['csv_path'], 'a+', newline='') as write_obj:
    # Create a writer object from csv module
    dict_writer = DictWriter(write_obj, fieldnames=field_names)
    # Add dictionary as row in the csv
    dict_writer.writerow(kwargs['current_row'])

  return


'''
PDF ATTACK FUNCTIONS
'''

def download_pdf(pdf_path, pdf_raw):
  '''
    Downloads PDF file to computer for analysis later
    Params: pdf_raw, pdf_path
  '''
  with open(pdf_path, 'wb') as f:
    shutil.copyfileobj(pdf_raw, f)

  return True

def check_pdf_for_pm(pdf_path, papermill_keywords):

  print('\nChecking PDF file for PM\n')

  '''
    Parse and search PDF text for papermill
    keywords.
  '''
  
  # open the pdf file
  try:  
    
    pdf_object = PyPDF2.PdfFileReader(pdf_path, strict=False)

    if pdf_object != None:

      # get number of pages for parsing
      num_pages = pdf_object.getNumPages()

      # extract text and do the search
      for i in range(0, num_pages):
        
        # Create PDF obj
        page_obj = pdf_object.getPage(i)

        # Make sure page is not null
        if page_obj != None:
        
          # Get text to search
          page_text = page_obj.extractText()

          # Parse text and search for papermill
          for pm in papermill_keywords:
            
            pm_search = re.search(pm, page_text)

            if pm_search:
              
              # PM found
              return True

          # No PM found, delete PDF
          os.remove(pdf_path)

          # Return false
          return False

    elif pdf_object == None:

      return 'Other_Error'
    
  except PdfReadError as pre:
    
    print('\nError: ', str(pre), '\n')

    if str(pre) == 'EOF marker not found':

      def reset_eof_of_pdf_return_stream(pdf_stream_in:list):

        # find the line position of the EOF
        for i, x in enumerate(txt[::-1]):
          
          if b'%%EOF' in x:

            print(x)
            
            actual_line = len(pdf_stream_in)-i

            print('\n\n\n\n',actual_line)

            print(f'EOF found at line position {-i} = actual {actual_line}, with value {x}')

            print(pdf_stream_in[:actual_line])
            
            # return the list up to that point
            return pdf_stream_in[:actual_line]
          
          else:
            # None found
            return None

      # Open broken file for reading
      with open(pdf_path, 'rb') as p:
        txt = (p.readlines())

      # Isolate a new list that terminates correctly
      txtx = reset_eof_of_pdf_return_stream(txt)

      if txtx == None:

        print('None')

      elif txtx != None:

        # write to new pdf
        fixed_pdf_path = pdf_path[:-4]+'_fixed.pdf'

        with open(fixed_pdf_path, 'wb') as f:

          print(txtx)

          f.writelines(txtx)

        fixed_pdf_object = PyPDF2.PdfFileReader(fixed_pdf_path)

        # get number of pages for parsing
        num_pages = fixed_pdf_object.getNumPages()

        # extract text and do the search
        for i in range(0, num_pages):
          
          # Create PDF obj
          page_obj = fixed_pdf_object.getPage(i)
          
          # Get text to search
          page_text = page_obj.extractText()

          # Parse text and search for papermill
          for pm in papermill_keywords:
            
            pm_search = re.search(pm, page_text)

            if pm_search:
              
              # PM found
              return True

          # No PM found, delete PDFs
          os.remove(pdf_path)
          os.remove(fixed_pdf_path)

          # Return false
          return False
      
    else:

      print('\nOther_Error\n')

      # Another more complicated error to parse out
      return 'Other_Error'

    
  except TypeError as pre:
    
    print('\nError: ', str(pre), '\n')
    
    # Another more complicated error to parse out
    return 'Other_Error'


'''
SEARCH QUERY PAGE ATTACK FUNCTIONS
'''

def parse_emojis(s):
  
  print('\n\nChecking for emojis: ',s)
  
  em = ''.join(c for c in s if c in emoji.UNICODE_EMOJI['en'])
  
  print('\n\n',em,'\n\n')
  
  return ''.join(c for c in s if c in emoji.UNICODE_EMOJI['en'])

def extract_emojis(s):
  emojis = ''
  emoji_string = parse_emojis(s)

  # If emojis
  if len(emoji_string) > 0:
    
    for emoji in emoji_string:
      
      emojis = emojis+','+emoji
    
    return emojis

  # If no emojis
  elif len(emoji_string) == 0:
    
    emojis = 'None'
    
    return emojis

def check_mal_search_attack(url):
  
  # Convert URL string to encoded any possible emojis
  url = unquote(unquote(url))
  
  # Extract any emojis, if present into an array
  emojis = extract_emojis(url)

  return emojis


'''
CHECK IF WP,WIKI,EVENT TYPES
'''

def check_site_installation(html_head):

  # Check wordpress
  any_wordpress = html_head.find_all('link', { 'href': 'wp-content' })

  # Check event/calendar
  any_localist = html_head.find_all('script', { 'src': 'localist' })

  if len(any_wordpress) > 0:

    return 'wordpress'

  elif len(any_localist) > 0:

    return 'event_page'

  elif len(any_wordpress) == 0 and len(any_localist) == 0:

    return 'not_wp_or_localist'

def check_actual_404(response):

  # 1. Check for regular 404 status
  if repr(response.status_code) == '404':
    
    return True
  
  # No 404 caught
  else:
    
    return False

def check_redirected_link(pm_href):
  '''
    Requests a found papermill link for a redirect.

    Params: 
      - pm_href: String. Paper mill URL

    Returns:
      - If True: Tuple (status code, rediirected URL)
      - If False: Boolean (False)
      - If exception: String. Name of exception code.
  '''

  print('\n\nChecking for redirected link\n\n')

  # Request papermill link for redirects
  redirect_response = http.get(
    pm_href,
    verify=False,
    headers={
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:41.0) Gecko/20100101 Firefox/41.0'
    },
    allow_redirects=True,
    timeout=None
  )
  
  try:
    
    redirect_response.raise_for_status()
    
    redirected_url = ''
    stream_check = redirect_response.history

    for response_code in stream_check:
      
      # Check if a redirect
      if (repr(response_code) == '<Response [301]>') or (repr(response_code) == '<Response [302]>'):
        
        redirected_url = redirect_response.url

        # Assign other variables
        return ( str(redirect_response.status_code), redirected_url )

      else:

        return False

  except (NewConnectionError, ConnectionError, ConnectTimeoutError, Timeout, MaxRetryError, RequestError, IOError) as r:

    print('\nConnection error: ', str(r), '\n')
    
    return 'timeout_error'

  except HTTPError:
    
    return 'http_error'
  
  except:
    
    return 'general_exception'

