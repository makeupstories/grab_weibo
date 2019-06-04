from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
import pymongo

basic_url = "https://m.weibo.cn/api/container/getIndex?"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Referer": "https://m.weibo.cn/u/2830678474",
}

client = pymongo.MongoClient(host='localhost',port=27017)
database = client["weibo"]
collection = database["weibo"]

def get_page(page):
    params = {
        "type": "uid",
        "value": "2830678474",
        "containerid": "1076032830678474",
        "page": page,
    }
    url = basic_url + urlencode(params)
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            print(f"这是第{page}页")
            return response.json()
    except requests.ConnectionError as e:
        print('Error:', e.args)

def parse_page(json):
    if json:
        items = json.get('data').get('cards')
        for item in items:
            item = item.get('mblog')
            weibo = {}
            weibo['id'] = item.get('id')
            weibo['text'] = BeautifulSoup(item.get('text'),'lxml').get_text()
            weibo['attitudes'] = item.get('attitudes_count')
            weibo['comments'] = item.get('comments_count')
            weibo['reposts'] = item.get('reposts_count')
            yield weibo

def save_to_mongo(result):
    if collection.insert(result):
        print('Save to Mongo!')

if __name__ == '__main__':
    for page in range(1,11):
        json = get_page(page)
        results = parse_page(json)
        for result in results:
            print(result)
            save_to_mongo(result)
