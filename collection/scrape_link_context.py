import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urlencode
from urllib.parse import urlsplit
from pm_scraper.scraper_filter import check_site_installation, request_attack, download_pdf, check_pdf_for_pm, check_mal_search_attack, check_actual_404, check_redirected_link, append_to_csv


class Webscraping(object):
    
    """Docstring for Webscraping. """
    def __init__(self):

        # TODO: update with random_user_agent
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'


    def crawl(self):
        """
        crawl: Crawl each URL in the corpus and gather contextual 
               content and information about the attack type.
        """

        EXPORT_CSV_PATH = '../data/serps_ca_20210929_filter_and_code_4.csv'
        
        # Retrieve list of links from csv
        links_df = pd.read_csv(
          '../data/original/canadian_hei_20210902_index.csv', 
          delimiter=',')

        # Papermills
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
        papermills_no_domain = [
            'essayoneday', 'essaypro', 'essayontime', 'essaypro',
            'proessaywriting', 'essayassist', 'power-essays', 'essayauthor',
            'bestessays', 'a-writer', 'reviewingwriting',
            'write-paper-for-me', 'iqessay', 'lowriting',
            'cheapapers', 'urpapers', 'paperwriting',
            'essaytown','rushessay','superiorpapers',
            'termpaperscorner','masterpaper','bestdissertation',
            'dissertationhelp','paper-helper', 'superbpapers'
        ]

        # Connect and check each link in corpus
        for row in links_df.to_dict('records'):
          
          '''
            HACK: Change row index based on the last
            error position
          '''
          # Unhandled rows
          # 10971-11007 - substancedev.etsmtl.ca == def hacked site, but taken down
          # 11152-11155,11196-11207,11218-11221,11256-11257: jouerpourapprendre.uqtr.ca; not active; essaygoose.net, papergraders.net; dissertationhelp.com
          # 10208-10209: studiumfc.umontreal.ca/blog; not active; dissertationhelp.com
          # 12461-12472: dev3.cegepsl.qc.ca; paperwriting.online, power-essays.com
          skippers = [845,1158,1372,1422,1441,1487,1488,1489,1490,1592,1633,1819,1846,1864,1865,2298,2849,2971,3026,3314,3693,3719,3720,3723,3737,3800,3996,4003,4008,4109,4111,4113,4180,4205,4206,4207,4209,4210,4211,4212,4213,4214,4232,4258,4296,4297,4439,4671,4765,4785,4959,5004,5636,5808,5859,5893,6272,6309,6727,6765,6819,6824,6825,6826,6828,6841,6845,6846,6851,7076,7112,7123,7156,7176,7205,7208,7253,7265,7272,7307,7584,7587,8718,8985,9548,9586,9624,9845,9987,10335,10344,10394,10443,10454,10565,10698,10751,10824,10852,10853,10854,10855,10856,10857,10858,10859,10861,10866,10878,10898,10902,10910,10971,10972,10973,10974,10975,10976,10977,10978,10979,10980,10981,10982,10983,10984,10985,10986,10987,10988,10989,10990,10991,10992,10993,10994,10995,10996,10997,10998,10999,11000,11001,11002,11003,11004,11005,11006,11007,11058,11152,11158,11160,11173,11196,11197,11198,11199,11200,11201,11202,11203,11204,11205,11206,11207,11218,11219,11220,11221,11243,11256,11257,11267,11272,11328,11362,11520,11525,11544,11548,11564,11565,11566,11567,11568,11569,11582,11587,11588,11589,11591,11592,11594,11596,11614,11821,12461,12462,12463,12464,12465,12466,12467,12468,12469,12470,12471,12472,12542,12546,12547,12568,12575,12576,12588,12589,12590,12591,12598,12599,12600,12601,12868,12998,13054,13075,13077,13086,13144,14086,14353]

          if int(row['index']) >= 14353 and int(row['index']) not in skippers:
            
            print('\nRow index: ',row['index'],'\n')
            
            # for row in urls:
            url = str(row['link'])

            '''
              1. CHECK IF PDF, before sending request
            '''
            re_pdf_file = r"\.pdf|filetype=pdf|type=pdf|cgi\/viewcontent\.cgi"
            
            pdf_matches = re.search(re_pdf_file, url)

            # IF link a PDF
            if pdf_matches:

              print('PDF')

              # Attempt to request PDF
              pdf_response = request_attack(url)

              if type(pdf_response) == str:
                
                # Append exception row
                append_to_csv(
                  current_row=row,
                  csv_path=EXPORT_CSV_PATH,
                  attack_type='unknown',
                  status_code=pdf_response,
                  active_status='not_active',
                  raise_for_status='unknown',
                  other_redirect_link='unknown',
                  link_context='None',
                  emojis='None',
                  page_type='pdf'
                )
              
              # Download and check PDF
              else:

                pdf_dir_path = 'pdfs/ca_scan/'
                
                # Create file name from row index
                pdf_filename = str(row['index'])+'.pdf'

                # Full absolute file path
                pdf_path = pdf_dir_path + pdf_filename

                completed_download = download_pdf(pdf_path, pdf_response.raw)

                if completed_download == True:
              
                  # Check PDF for PM keywords
                  ## Returns True or False
                  boolean_pdf_check = check_pdf_for_pm(pdf_path, papermills_no_domain)

                  if boolean_pdf_check == True:

                    # Append Postive
                    append_to_csv(
                      current_row=row,
                      csv_path=EXPORT_CSV_PATH,
                      attack_type='pdf',
                      status_code='None',
                      active_status='active',
                      raise_for_status=pdf_response.raise_for_status,
                      other_redirect_link='None',
                      link_context='None',
                      emojis='None',
                      page_type='pdf'
                    )

                  elif boolean_pdf_check == False:

                    # Append False Positve
                    append_to_csv(
                      current_row=row,
                      csv_path=EXPORT_CSV_PATH,
                      attack_type='false_positive',
                      status_code='None',
                      active_status='None',
                      raise_for_status=pdf_response.raise_for_status,
                      other_redirect_link='None',
                      link_context='None',
                      emojis='None',
                      page_type='pdf'
                    )
                
                  elif boolean_pdf_check == 'Other_Error':

                    # Append False Positve
                    append_to_csv(
                      current_row=row,
                      csv_path=EXPORT_CSV_PATH,
                      attack_type='check_pdf',
                      status_code='None',
                      active_status='None',
                      raise_for_status=pdf_response.raise_for_status,
                      other_redirect_link='None',
                      link_context='None',
                      emojis='None',
                      page_type='pdf'
                    )

                  continue

            # If not a PDF
            elif not pdf_matches:
              
              # Request attack
              response = request_attack(url)

              # If response error returned as a string value
              if type(response) == str:

                print('\n\nresponse error to append',type(response),'\n\n')

                # Append exception row
                append_to_csv(
                  current_row=row,
                  csv_path=EXPORT_CSV_PATH,
                  attack_type='unknown',
                  status_code=response,
                  active_status='None',
                  raise_for_status=response,
                  other_redirect_link='None',
                  link_context='None',
                  emojis='None',
                  page_type='NA'
                )
                
              elif type(response) != str:

                print('\n\nSearch for s=?\n\n')

                '''
                  CHECK IF SEARCH QUERY PAGE
                '''
                # Check for s= string
                parsed = urlsplit(url)

                print(parsed)
                
                # If s=
                if parsed.query[:2] == 's=':

                  print('\n\nFound Search Query Page\n\n')
                  
                  any_emojis = check_mal_search_attack(url)
                  
                  # Append inactive search query page
                  if len(any_emojis) > 0:

                    append_to_csv(
                      current_row=row,
                      csv_path=EXPORT_CSV_PATH,
                      attack_type='search_query_page',
                      status_code=response,
                      active_status='active',
                      raise_for_status=response.raise_for_status,
                      other_redirect_link='None',
                      link_context='None',
                      emojis=any_emojis,
                      page_type='NA'
                    )

                    continue
                
                # If NOT s=
                elif parsed.query[:2] != 's=':

                  print('\n\nSearch on requested page\n\n')

                  # Search for PM
                  content = response.text
                  soup = BeautifulSoup(content, 'html.parser')

                  # Check for type of page
                  page_type = check_site_installation(soup)

                  # Check for papermill keyword
                  pm_tags = []
                  for pm in papermills_no_domain:
                    
                    tags = soup.find_all('td', text=lambda t: t and pm in t)

                    if len(tags) > 0:

                      pm_tags.append(tags)

                  # Verify list for papermill keyword
                  verified_pm_tags = []
                  for pp in pm_tags:
                    for p in pp:
                      if (p) > 0:
                        verified_pm_tags.append(p)
                  
                  print('\n\nverified_pm_tags: ', verified_pm_tags, '\n\n')

                  # If papermill not found, append false positive
                  if len(verified_pm_tags) == 0:
                    
                    # Append False Positve
                    append_to_csv(
                      current_row=row,
                      csv_path=EXPORT_CSV_PATH,
                      attack_type='false_positive',
                      status_code='None',
                      active_status='None',
                      raise_for_status=response.raise_for_status,
                      other_redirect_link='None',
                      link_context='None',
                      emojis='None',
                      page_type=page_type
                    )
                  
                  # If papermill found, continue
                  elif len(verified_pm_tags) > 0:

                    print('Papermill found!')
                    
                    # Retrieve all links on page
                    all_links = soup('a')
                      
                    '''
                      CHECK IF 404
                    '''
                    check_404_response = check_actual_404(response)

                    # If 404 found, append to csv
                    if check_404_response == True:
                      
                      append_to_csv(
                        current_row=row,
                        csv_path=EXPORT_CSV_PATH,
                        attack_type='unknown',
                        status_code=response.status_code,
                        active_status='inactive',
                        raise_for_status=response.raise_for_status,
                        other_redirect_link='unknown',
                        link_context='None',
                        emojis='None',
                        page_type=page_type
                      )

                      continue
                    
                    # If 404 not found, search for papermills
                    else:
                      
                      # Any papermills in links
                      for a in all_links:
                        
                        for papermill in papermills_no_domain:
                          
                          # If papermill found
                          if a.text.lower() == papermill:

                            # Extract href
                            pm_href = a.get('href')
                            
                            # Extract parent
                            pm_parent = a.find_parent()

                            # Test found link for redirects
                            redirect_response = check_redirected_link(pm_href)

                            # If False
                            if redirect_response == False:
                      
                              append_to_csv(
                                current_row=row,
                                csv_path=EXPORT_CSV_PATH,
                                attack_type='unknown',
                                status_code=response.status_code,
                                active_status='active',
                                raise_for_status=response.raise_for_status,
                                other_redirect_link='None',
                                link_context='None',
                                emojis='None',
                                page_type=page_type
                              )

                              continue
                            
                            # If exception
                            if type(redirect_response) == str:
                      
                              append_to_csv(
                                current_row=row,
                                csv_path=EXPORT_CSV_PATH,
                                attack_type='unknown',
                                status_code=redirect_response,
                                active_status='unknown',
                                raise_for_status=response.raise_for_status,
                                other_redirect_link='unknown',
                                link_context='None',
                                emojis='None',
                                page_type=page_type
                              )

                              continue

                            # If Redirect
                            if type(redirect_response) == tuple:
                      
                              append_to_csv(
                                current_row=row,
                                csv_path=EXPORT_CSV_PATH,
                                attack_type='redirect',
                                status_code=redirect_response[0],
                                active_status='unknown',
                                raise_for_status=response.raise_for_status,
                                other_redirect_link=redirect_response[1],
                                link_context=pm_parent,
                                emojis='None',
                                page_type=page_type
                              )

                              continue

scrape = Webscraping()
scrape.crawl()