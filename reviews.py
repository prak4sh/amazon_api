import requests
from rich import print
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os
import time
import csv
import random

load_dotenv()
api = os.getenv('API_KEY')
session = requests.Session()

amazon_domains = [
    ('wwww.amazon.com', 'US'),
    ('wwww.amazon.co.uk', 'UK'),
    ('wwww.amazon.ca', 'CA'),
    ('wwww.amazon.de', 'DE'),
    ('wwww.amazon.fr', 'FR'),
    ('wwww.amazon.co.jp', 'JP'),
    ('wwww.amazon.in', 'IN'),
    ('wwww.amazon.com.au', 'AU'),
    ('wwww.amazon.cn', 'CN'),
    ('wwww.amazon.it', 'IT'),
    ('wwww.amazon.es', 'ES'),
    ('wwww.amazon.com.br', 'BR'),
    ('wwww.amazon.com.mx', 'MX')
]

headers = {
            'authority': 'www.amazon.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-gpc': '1',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
        }

def get_UA():
    UserAgents_csv = "userAgent.csv"
    dir_script = os.path.dirname(os.path.abspath(__file__))
    path_csv = os.path.join(dir_script, UserAgents_csv)
    random_user_agent_list = []
    with open(path_csv, 'r', encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile)
        random_user_agent_list = [
            item for row in csv_reader for item in row]
    ua = random.choice(random_user_agent_list)
    return ua

def get_domain(code):
    result = None
    for domain in amazon_domains:
        if code == domain[1]:
            result = domain[0]
    return result

def _request_via_api(url):
    payload = {'api_key': api, 'url': url}
    headers['referer'] = url
    headers['user-agent'] = get_UA()
    while True:
        response = requests.get('http://api.scraperapi.com',params=payload, headers=headers)
        print(f'Url: {url}, {response.status_code}')
        if response.status_code == 200:
            break
        else:
            time.sleep(2)
    return response

def _requests(url, domain):
    global session
    headers['authority'] = domain
    headers['referer'] = url
    headers['user-agent'] = get_UA()
    response = requests.get(url, headers=headers)
    print(f'Url: {url}, {response.status_code}')
    if check_title(response):
        return response
    else:
        return _request_via_api(url)

def _soup(response):
    return BeautifulSoup(response.text, 'html.parser')

def check_title(response):
    soup = _soup(response)
    title = soup.find(class_="product-title")
    if title:
        return True
    else:
        return False

def get_reviews(asin, domain_code='US',page=1):
    domain = get_domain(domain_code)
    if not domain:
        print('Domain not in list')
        return None
    url = f'https://{domain}/product-reviews/{asin}?pageNumber={page}'
    response = _requests(url, domain)
    soup = _soup(response)
    title = soup.find(class_="product-title")
    if title:
        title = title.a.get_text()
    review_section = soup.find(id='cm_cr-review_list')
    nextPage = review_section.find(class_="a-last")
    print(nextPage)
    review_divs = review_section.find_all(class_='review')
    for review_div in review_divs:
        author = review_div.find(class_="a-profile-name").get_text()
        title = review_div.find(class_='review-title')
        if title:
            title = title.find_all('span')[-1].get_text().strip()
        rating = review_div.find(class_='review-rating').span.get_text()
        rating = rating.split(' ')[0]
        detail = review_div.find(class_="review-text").get_text().strip()
        review_date = review_div.find(class_='review-date').get_text()
        date_path = r'(?= on )(.*)'
        date = re.search(date_path, review_date).group(0).replace('on','').strip()
        review = {
            'Author': author,
            'Title': title,
            'Date': date,
            'Rating':rating,
            'Review': detail
        }
        print(title)

if __name__== "__main__":
    get_UA()