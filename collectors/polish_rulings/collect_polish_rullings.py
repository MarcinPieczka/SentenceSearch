#!/usr/bin/python3
import argparse
import requests
import datetime
import logging
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from bs4 import BeautifulSoup
from collections import deque
from pprint import pprint

URL_BASE = 'http://orzeczenia.ms.gov.pl'
SEARCH_PAGE_URL_FORMAT = ('http://orzeczenia.ms.gov.pl/search/advanced/$N/$N' +
'/$N/$N/$N/$N/$N/{date_from}/{date_to}/$N/$N/$N/$N/$N/$N/score/descending/')

TOO_MUCH_REQUESTS_IDENTIFIER = "Wykryliśmy zbyt dużą liczbę zapytań"


def main(collect_all, date_from, date_to):
    conf = {'sleep_time': 30}
    data = {}
    if not any((collect_all, date_from, date_to)):
        print("You have to set at least one parameter")
        return
    search_page_url = prepare_search_page_url(collect_all, date_from, date_to)
    for url, requests_restricted in DocURLGetter(search_page_url):
        if requests_restricted:
            restriction_management(conf)
            continue

        sleep(conf.get('sleep_time', 0))
        print(f'url: {url}')
        data[url] = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fn, url) for fn in 
            (parse_details_page, parse_content_page, parse_regulations_page)]
            for future in as_completed(futures):
                data[url].update(future.result())
        pprint(data)

def restriction_management(conf):
    conf['sleep_time'] * 1.5
    print(f"Too much requests, sleeping {conf['sleep_time']}s")
    sleep(conf.get('sleep_time', 0))


def prepare_search_page_url(collect_all, date_from, date_to):
    if collect_all:
        date_from = '1900-01-01'
        date_to = None
    for d in date_from, date_to:
        if not d:
            d = '$N'
    return SEARCH_PAGE_URL_FORMAT.format(date_from=date_from, date_to=date_to) + '{}'

def parse_details_page(url):
    result = {}
    url = URL_BASE + url
    page = url_to_bs4(url)
    if not page:
        return {}
    try:
        elems = (page.find_all('div', {'class': 'single_result'})[0]
            .find_all(['dd', 'dt']))
    except:
        print(f'THIS IS THE PAGE: {page}')
        raise
    current = None
    for elem in elems:
        print('#############################################################')

        if elem.name == 'dt':
            current = str(elem.content)
            result[current] = []
        else:
            print('ELSE_____________')
            print(elem)
            if len(list(elem)) == 1:
                result[current].append(list(elem)[0])
            else:
                print('STRANGE_______BR_______________________!!!!!!!!!!!!_')
                content = list(filter(lambda x: bool(x), [s.replace('<dd>', '')
                    .replace('<dd/>', '').replace('</dd>', '').strip() for s in 
                    list(filter(lambda x: bool(x), str(elem).split('<br/>')))
                ]))
                print(content)
                result[current].extend(content)


    return {'details': list(result)}

def parse_content_page(url):
    url = URL_BASE + url.replace('details', 'content')
    return {}


def parse_regulations_page(url):
    url = URL_BASE + url.replace('details', 'regulations')
    return {}
        
def url_to_bs4(url):
    response = requests.get(url)
    if response:
        page = BeautifulSoup(response.text, 'html.parser')
        if page.find_all('div', {'class': 'single_result'}):
            DocURLGetter.append_left_to_queue(url)
        else:
            return page
        


class DocURLGetter():
    links = deque()

    def __init__(self, url):
        self.url = url
        self.page = None
        self.page_nr = 1

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if DocURLGetter.links:
                return DocURLGetter.links.popleft(), False
            else:
                self.page = url_to_bs4(self.url.format(self.page_nr))
                if not self.page:
                    self.links = deque()
                    return {}, True
                self.page_nr += 1
                links = filter(
                    lambda l: l.attrs.get('href', '').startswith('/details'), 
                    self.page.find_all('a')
                )
                DocURLGetter.links.extend(deque(map(lambda l: l.attrs['href'], links)))

    @classmethod
    def append_left_to_queue(cls, url):
        DocURLGetter.links.appendleft(
            '/'.join(url.replace('regulations', 'details')
            .replace('content', 'details').split('/')[:-1])
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