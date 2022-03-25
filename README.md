# Rhetops Papermill Scraper

Repository of code and data used in the following study:

> Ridolfo, Jim, Hart-Davidson, William, and Chris Lindgren. (2022). [“Hello, Is This the Writing Center?”: Illicit Paper Mill Activity and the Compromised Recomposition of College and University Websites.](https://praxis.technorhetoric.net/tiki-index.php?page=PraxisWiki:_:PaperMills)
*Kairos: A Journal of Rhetoric, Technology, and Pedagogy*, 26.2.

## Coding Files


### `google-scraper`

The `google.py` and `google_ca.py` spiders scrape Google's search engine results API. See the README file for a more general operation of Python's Scrapy code library.

### `scrape_link_context.py`

The follow-up 'scrape_link_context.py' scraper performs the following checks on the new corpus:

1. Codes data for: 
   - pdf_files: PDF with possible embedded scripts;
   - search_404: checks for the 's=' query in a URL and isolates its emojis in a separate column;
   - redirect: Search for any hyperlinked papermill mentions on a page. Then, it tests that linked text for redirected URLS. Even if it isn't a redirect, the parent element content and HTML are logged; or 
   - to_code: If we can't categorize it by the above, collect any relevant info possible to help hand code it later.
2. Downloads PDFs for later analysis. There are some tools that can test it for malicious code.
3. Tests and records if links are 'active' or 'inactive'
4. During redirect testing, it collects parent element of identified papermill links for more context about redirects or links on page
5. If a search_404 page attack, it isolates and records emojis from search_404 attack links
6. Marks attacks as 'to_code', if no response from URL request. But, the request exception types are specific to the check type.

## Other Related Data 

Below are spreadsheets outsourced for qualitative coding and other uses for sharing our information with others:

1. Qualitatively coded attacks for the third scan: [Google Sheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2Wz9kqBxDvAYaALhlAEZyDYcG2E4Lzjd7Iil-KxQ6BHRsvo-nNFi1bJl4_WllESwXMbiEjyq8IerD/pubhtml).

## Scan Information

### Canadian University 09-02-2021 Scan

**Query Format**: 

`https://www.google.com/search?q=site%3UNIVERSITY_URL_HERE+-academia.edu+%22PAPER_MILL_URL_HERE%22&num=10&exactTerms=PAPER_MILL_URL_HERE`


**Scrapy stats**:

```
{
   'downloader/request_bytes': 5114292,
   'downloader/request_count': 8872,
   'downloader/request_method_count/GET': 8872,
   'downloader/response_bytes': 14645193,
   'downloader/response_count': 8872,
   'downloader/response_status_count/200': 6979,
   'downloader/response_status_count/500': 1893,
   'dupefilter/filtered': 52,
   'elapsed_time_seconds': 47956.884562,
   'feedexport/success_count/FileFeedStorage': 1,
   'finish_reason': 'finished',
   'finish_time': datetime.datetime(2021, 9, 3, 10, 47, 25, 804957),
   'httpcompression/response_bytes': 17152692,
   'httpcompression/response_count': 8872,
   'httperror/response_ignored_count': 8,
   'httperror/response_ignored_status_count/500': 8,
   'item_scraped_count': 14390,
   'log_count/ERROR': 8,
   'log_count/INFO': 818,
   'memusage/max': 103841792,
   'memusage/startup': 102334464,
   'request_depth_max': 18,
   'response_received_count': 6987,
   'retry/count': 1885,
   'retry/max_reached': 8,
   'retry/reason_count/500 Internal Server Error': 1885,
   'scheduler/dequeued': 8872,
   'scheduler/dequeued/memory': 8872,
   'scheduler/enqueued': 8872,
   'scheduler/enqueued/memory': 8872,
   'start_time': datetime.datetime(2021, 9, 2, 21, 28, 8, 920395)
}
2021-09-03 06:47:25 [scrapy.core.engine] INFO: Spider closed (finished)
```

### Scan Memos

- This scan differs from the *.edu in that it uses the Google Search API to scrape each specific university site, rather than the top-level *.edu.
- To mitigate false positives, I will probably need to use another script to filter out false positives.
