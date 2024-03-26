import requests
from rich import print
from bs4 import BeautifulSoup
import re

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

def _requests(url):
    headers['referer'] = url
    response = requests.get(url, headers=headers)
    print(f'Url: {url}, {response.status_code}')
    return response

def _soup(response):
    return BeautifulSoup(response.text, 'html.parser')

def get_reviews(asin, page=1):
    url = f'https://www.amazon.com/product-reviews/{asin}?pageNumber={page}'
    response = _requests(url)
    with open('test.html','w') as f:
        f.write(response.text)
    soup = _soup(response)
    title = soup.find(class_="product-title")
    print(title)
    if title:
        title = title.a.get_text()
    review_section = soup.find(id='cm_cr-review_list')
    # review_section = soup.find(class_='review-views')
    print(review_section)
    review_divs = review_section.find_all(class_='review')
    for review_div in review_divs:
        author = review_div.find(class_="a-profile-name").get_text()
        title = review_div.find(class_='review-title').span.get_text()
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
        print(review)

if __name__== "__main__":
    asin = '1546017453'
    get_reviews(asin, 2)