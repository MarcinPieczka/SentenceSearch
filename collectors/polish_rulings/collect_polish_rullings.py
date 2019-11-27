#!/usr/bin/python3
import argparse
import requests
import datetime

unflitered_search_page_url = f'http://orzeczenia.ms.gov.pl/search/advanced/$N/$N'
    '/$N/$N/$N/$N/$N/{date_from}/{date_to}/$N/$N/$N/$N/$N/$N/score/descending/'

def main(collect_all, date_from, date_to):
    if collect_all:
        date_from = datetime.datetime(1900, 1, 1)
        date_to = None
    

def get_unfiltered_search_page()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Collect polish court rullings')
    parser.add_argument('--all', dest='collect_all', default=False, 
                        action='store_true', help='collect all documents')
    parser.add_argument('--from', dest='date_from',
                        help='collect rulings from date specified in this param,' 
                             'format yyyy-mm-dd',
                        type=(lambda d:datetime.datetime.strptime(d, '%Y-%m-%d')))
    parser.add_argument('--to', dest='date_to',
                        help='collect rulings before date specified in this param,'
                             'format yyyy-mm-dd',
                        type=(lambda d:datetime.datetime.strptime(d, '%Y-%m-%d')))

    args = parser.parse_args()
    main(args['collect_all'], args['date_from'], args['date_to'])