"""
4. condition:
    a. 10 new
    b. 20 like new
    c. 30 excellent
    d. 40 good
    e. 50 fair
    f. 60 salvage
"""
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import requests
import unicodedata
import urllib
from argparse import ArgumentParser
from bs4 import BeautifulSoup as bs
from os.path import join


def get_average(query, city, condition, min_price,
                postal, search_distance,
                target_folder='.'):
    table_path = join(target_folder, 'describe.csv')
    image_path = join(target_folder, 'prices.png')
    items_path = join(target_folder, 'items.csv')
    parameter = {'query': query,
                 'condition': condition,
                 'min_price': min_price,
                 'postal': postal,
                 'search_distance': search_distance}
    url = "http://{0}.craigslist.org/search/sss".format(city.strip().lower().replace(' ', ''))
    r = requests.get(url, parameter)
    s = bs(r.text, 'html.parser')

    rows = s.find_all(class_='result-row')
    data = []
    for row in rows:
        name = row.find(class_='result-title')
        name = unicodedata.normalize('NFKD', name.text.strip()).encode('ASCII', 'ignore') if name else ''
        url = 'https://craigslist.com'
        href = row.find(class_='result-title')
        href = str(url + href.attrs.get('href', '').strip()) if href else ''
        price = row.find(class_='result-price')
        price = str(price.text[1:].strip()) if price else ''
        location = row.find(class_='result-hood')
        location = str(location.text.strip()) if location else ''
        data.append((name, href, price, location))
    d = pd.DataFrame(data, columns=['title', 'url', 'price', 'location'])
    d.to_csv(items_path, index=False)

    r = s.find_all(class_='result-price')
    prices = [int(a.text[1:]) for a in r]
    average = sum(prices) / len(prices)
    df = pd.DataFrame(prices, columns=["price"])
    df.describe().to_csv(table_path)
    image = df.groupby(['price'])['price'].count()
    image = pd.DataFrame(zip(image.index, image), columns=['price', 'count'])
    image = image.plot(x='price', y='count')
    image.set_title(query, fontsize=20)
    image.set_xlabel('Price', fontsize=18)
    image.set_ylabel('Count', fontsize=18)
    figure = image.get_figure()
    figure.savefig(image_path)
    print "average_price = ${0}".format(average)
    print "items_table_path = {0}".format(items_path)
    print "description_table_path = {0}".format(table_path)
    print "prices_image_path = {0}".format(image_path)
    return average


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument('query')
    argument_parser.add_argument('--condition', '-c', type=int, choices=[10, 20, 30, 40, 50], default=30)
    argument_parser.add_argument('--min_price', '-m')
    argument_parser.add_argument('--postal', '-p')
    argument_parser.add_argument('--search_distance', '-d', default=20)
    argument_parser.add_argument('--city', default="newyork")
    argument_parser.add_argument('--target_folder')
    args = argument_parser.parse_args()
    query = get_average(args.query, args.city, args.condition, args.min_price, args.postal, args.search_distance, args.target_folder)
