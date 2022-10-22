import re
import json
import shutil
import requests
import unidecode
import pandas as pd
from bs4 import BeautifulSoup
import os


def count_pages(url: str) -> int:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42",
    }

    params = {
        "pe": "1200",
        "sp": "2"
    }

    resp = requests.get(url, headers=headers, params=params)

    soup = BeautifulSoup(resp.text, 'html.parser')
    last_link = soup.find("a", string="Última pagina")['href']
    last_page_param = re.search("\?o=\d+&", last_link)
    last_page_param = re.search("\d+", last_page_param.group())
    last_page = int(last_page_param.group())
    return last_page


def get_all_ads(url: str, last_page: int) -> list:
    ad_lists = []
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42",
    }
    params = {
        "pe": "1200",
        "sp": "2",
    }

    for i in range(1, last_page+1):
        params["o"] = i

        res = requests.get(url, headers=headers, params=params)
        print(res.request.url)
        soup = BeautifulSoup(res.text, 'html.parser')
        ad_lists.append(soup.find(id='ad-list'))

    return ad_lists


def filter_ads(ad_lists: list, not_contain_words: list) -> list:
    filtered_itens = []
    for ad_list in ad_lists:
        for li in ad_list.find_all('li'):
            try:
                title = li.find('h2').text
                title = unidecode.unidecode(title.lower())
                link = li.find('a')['href']

                price_class = "m7nrfa-0 eJCbzj sc-ifAKCX ANnoQ"
                value = li.find("span", class_=price_class).text
                value = re.sub(r'[^\d]', '', value)
                value = float(value)

                location_class = "sc-1c3ysll-1 cLQXSQ sc-ifAKCX fCbscF"
                location = li.find("span", class_=location_class)["aria-label"]
                location = unidecode.unidecode(location.lower())
                location = location.replace("localizacao: ", "")

                if not any(s for s in not_contain_words if s in title or s in location):
                    obj = {
                        "title": title,
                        "link": link,
                        "value": value,
                        "location": location,
                    }
                    filtered_itens.append(obj)

            except:
                continue
    return filtered_itens


def write_today_ads(ads):
    try:
        shutil.copyfile("./today_ads.json", "./yesterday_ads.json")
    except FileNotFoundError:
        pass
    finally:
        with open("today_ads.json", "w") as out_file:
            json.dump(ads, out_file, indent = 4)


def compare_ads(ads):
    '''
        Show news results
    '''
    today_json = './today_ads.json'
    isExist = os.path.exists(today_json)
    if not isExist:
        return None

    yesterday_ads = pd.read_json(today_json)
    today_ads = pd.DataFrame.from_dict(ads)

    ads_diff = pd.concat([today_ads, yesterday_ads]).drop_duplicates(keep=False)
    with open('./compared_ads.json', mode='w', encoding='utf-8') as f:
        json.dump(ads_diff.to_dict(orient = 'records'), f, indent=4)


def main():
    url = 'https://rj.olx.com.br/norte-do-estado-do-rio/regiao-dos-lagos/cabo-frio/imoveis/aluguel?'
    page = count_pages(url)

    ads = get_all_ads(url, page)

    stop_words = ["unamar", "pero", "tamoios", "jacare", "porto do carro", "jardim esperanca", "temporada"]
    filtered_ads = filter_ads(ads, stop_words)

    compare_ads(filtered_ads)
    write_today_ads(filtered_ads)


main()