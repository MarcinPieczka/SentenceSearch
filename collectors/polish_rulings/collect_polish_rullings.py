#!/usr/bin/python3
import argparse
import requests
import datetime
import logging
from bs4 import BeautifulSoup
from collections import deque

SEARCH_PAGE_URL_FORMAT = ('http://orzeczenia.ms.gov.pl/search/advanced/$N/$N' +
'/$N/$N/$N/$N/$N/{date_from}/{date_to}/$N/$N/$N/$N/$N/$N/score/descending/')
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def main(collect_all, date_from, date_to):
    if not any((collect_all, date_from, date_to)):
        print("You have to set at least one parameter")
        return
    search_page_url = prepare_search_page_url(collect_all, date_from, date_to)
    for url in document_urls_generator(search_page_url):
        print(url)

def prepare_search_page_url(collect_all, date_from, date_to):
    if collect_all:
        date_from = '1900-01-01'
        date_to = None
    for d in date_from, date_to:
        if not d:
            d = '$N'
    return SEARCH_PAGE_URL_FORMAT.format(date_from=date_from, date_to=date_to) + '{}'
        

class document_urls_generator():
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
                print(self.url.format(self.page_nr))
                response = requests.get(self.url.format(self.page_nr))
                if not response:
                    raise StopIteration
                self.page_nr += 1
                self.page = BeautifulSoup(response.text, 'html.parser')
                self.links = list(self.page.find_all('a'))
                for link in self.links:
                    print(list(link))
                    print(link.attrs.get('href'))
                self.links = deque(
                    filter(lambda l: l.attrs.get('href', '').startswith('/details'), self.links)  # .startswith('/details')
                )


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