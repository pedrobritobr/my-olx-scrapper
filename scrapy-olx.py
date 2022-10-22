import re
import requests
from bs4 import BeautifulSoup


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


def main():
    url = 'https://rj.olx.com.br/norte-do-estado-do-rio/regiao-dos-lagos/cabo-frio/imoveis/aluguel?'
    page = count_pages(url)


main()