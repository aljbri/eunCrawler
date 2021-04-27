# -*- coding: utf-8 -*-
"""eunCrawler

# Grep News
This code crawle throw [EruoNews](https://euronews.com/) wabsite to extract all the news information and collect them to be saved as **JSON** file.

This Code was writtin to collect the data from [Arabic Editoin](https://arabic.euronews.com/) website. 

tested and validated with Arabic, yet it can work with any other language.
To extract the news for the language you want pass the Language paramater

the supported Languages:

1. [English](https://www.euronews.com) -> www
2. [Français](https://fr.euronews.com) -> fr
3. [Deutsch](https://de.euronews.com) -> de
4. [Italiano](https://it.euronews.com) -> it
5. [Español](https://es.euronews.com) -> es
6. [Português](https://pt.euronews.com) -> pt
7. [Русский](https://ru.euronews.com) -> ru
8. [Türkçe](https://tr.euronews.com) -> tr
9. [Ελληνικά](https://gr.euronews.com) -> gr
10. [Magyar](https://hu.euronews.com) -> hu
11. [فارسی](https://per.euronews.com) -> per
12. [العربية](https://arabic.euronews.com) -> arabic
"""

#@title importing modules
import os
import json
import pickle
import urllib3

from bs4 import BeautifulSoup
from tqdm import tqdm
from calendar import monthrange

"""**Here** was initialize the http client"""

#@title initial http Client
UserAgent = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'}
urllib3.disable_warnings()
agent = urllib3.PoolManager(headers=UserAgent)

#@title inital the archive URLs
nagency = 'https://{0}.euronews.com'
years = [f'{y:04d}' for y in [*range(2001, 2022, 1)]]
months = [f'{m:02d}' for m in [*range(1, 13, 1)]]
days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

"""**parserLink** : return the response's page as *BeautifulSoup* object"""

#@title ***parserLink*** Function
def parserLink(url: str):
    page = agent.request('GET', f'{nagency}{url}').data.decode('utf-8')
    return BeautifulSoup(page, 'html.parser')

"""**getNews** : function validet the page and Extract the news info as a ***JSON*** Object"""

#@title ***getNews*** Function
def getNews(url: str, news=False):
    news = parserLink(url).find('main', {'id': 'enw-main-content'})

    if news:
        if news.find('section', {'class': 'enw-block-error'}):
            return None
        total_result = int(news.find('section')['data-total-result'])
        if not total_result:
            return None
        jnews = news.find('section', {
            'class': 'qa-listingBlock'
        }).find('div', {'class': ''})
        jnews = json.loads(jnews['data-content'])
        if total_result > 30:
            paginator = len(news.find('ul', {'class': 'c-paginator'})) - 1
            for p in range(2, paginator + 1):
                news = parserLink(f'{url}?p={p}').find(
                    'main', {'id': 'enw-main-content'})
                news = news.find('section', {
                    'class': 'qa-listingBlock'
                }).find('div', {'class': ''})
                jnews.extend(json.loads(news['data-content']))
                del news
        return jnews
    return None

"""**eunCrawler** : it gother all the news pages informaton and save it as **JSON** file

You can pass one of the following value as string:

[www, fr, de, it, es, pt, ru, tr, gr, hu, per, arabic]
"""

#@title ***eunCrawler*** Function 
## Paramater *language*
def eunCrawler(language:str='arabic'):
    global nagency
    
    jNews = []
    nagency = nagency.format(language)
    yrs = tqdm(years, position=0)
    for year in yrs:
        yrs.set_description(f'Processing {year} news')
        for i, month in enumerate(months):
            if i == 1:
                dy = monthrange(int(year), int(month))[1]
            else:
                dy = days[i] + 1
            for day in tqdm(range(1, dy),
                            desc=f'Processing days {year}/{month}',
                            position=1,
                            leave=False):
                news = getNews(f'/{year}/{month}/{day:02d}/')
                if not news:
                    continue
                jNews.extend(news)
                print(end='\r', flush=True)
            print(end='\r', flush=True)
    with open('myfile.json', 'w', encoding='utf8') as jFile:
        json.dump(jNews, jFile, ensure_ascii=False)

#@title Run execution
if __name__ == '__main__':
    eunCrawler()