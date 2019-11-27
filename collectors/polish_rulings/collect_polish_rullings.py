#!/usr/bin/python3
import argparse
import requests
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from bs4 import BeautifulSoup
from collections import deque

SEARCH_PAGE_URL_FORMAT = ('http://orzeczenia.ms.gov.pl/search/advanced/$N/$N' +
'/$N/$N/$N/$N/$N/{date_from}/{date_to}/$N/$N/$N/$N/$N/$N/score/descending/')
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def main(collect_all, date_from, date_to):
    data = {}
    if not any((collect_all, date_from, date_to)):
        print("You have to set at least one parameter")
        return
    search_page_url = prepare_search_page_url(collect_all, date_from, date_to)
    for url in DocURLGetter(search_page_url):
        data[url] = {}
        details_url = url
        content_url = url.replace('details', 'content')
        regulations_url = url.replace('details', 'regulations')

        print(details_url, content_url, regulations_url)


        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(parse_details_page, details_url),
                executor.submit(parse_content_page, content_url),
                executor.submit(parse_regulations_page, regulations_url),
            ]
            for future in as_completed(futures):
                data[url].update(future.result())
        

def prepare_search_page_url(collect_all, date_from, date_to):
    if collect_all:
        date_from = '1900-01-01'
        date_to = None
    for d in date_from, date_to:
        if not d:
            d = '$N'
    return SEARCH_PAGE_URL_FORMAT.format(date_from=date_from, date_to=date_to) + '{}'

def parse_details_page(url):
    return {}

def parse_content_page(url):
    return {}

def parse_regulations_page(url):
    return {}
        

class DocURLGetter():
    def __init__(self, url):
        self.url = url
        self.page = None
        self.page_nr = 1
        self.links = None

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.links:
                return self.links.popleft()
            else:
                response = requests.get(self.url.format(self.page_nr))
                if not response:
                    raise StopIteration
                self.page_nr += 1
                self.page = BeautifulSoup(response.text, 'html.parser')
                self.links = filter(
                    lambda l: l.attrs.get('href', '').startswith('/details'), 
                    self.page.find_all('a')
                )
                print(self.links)
                self.links = deque(map(lambda l: l.attrs['href'], self.links))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect polish court rullings')
    parser.add_argument('--all', dest='collect_all', default=False, 
                        action='store_true', help='collect all documents')
    parser.add_argument('--from', dest='date_from',
                        help='collect rulings from date specified in this param,' 
                             'format yyyy-mm-dd')
    parser.add_argument('--to', dest='date_to',
                        help='collect rulings before date specified in this param,'
                             'format yyyy-mm-dd')

    args = parser.parse_args()
    main(args.collect_all, args.date_from, args.date_to)