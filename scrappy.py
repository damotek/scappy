import requests
from bs4 import BeautifulSoup
import time
import sqlite3 as sl
from selenium import webdriver

URL_SAPO = "https://casa.sapo.pt/alugar-apartamentos/t3,t4,t5,t6-ou-superior/lisboa/?gp=1200"
headers_sapo = {"Referer": "https://casa.sapo.pt/alugar-apartamentos/t3/ofertas-recentes/lisboa/", "User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

URL_IDEALISTA = "https://www.idealista.pt/arrendar-casas/lisboa/com-preco-max_1200,t3,t4-t5/"
headers_idealista = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

URL_IMOVIRTUAL = "https://www.imovirtual.com/arrendar/apartamento/lisboa/?search%5Bfilter_float_price%3Ato%5D=1200&search%5Bfilter_enum_rooms_num%5D%5B0%5D=3&search%5Bfilter_enum_rooms_num%5D%5B1%5D=4&search%5Bregion_id%5D=11&search%5Bsubregion_id%5D=153"
headers_imovirtual = {"Referer": "https://www.idealista.pt/","user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36", 'referer': 'https://www.google.com/'}

def main():
    con = sl.connect('casas.db')
    finderIdealista()
    #while(True):
    #    finderSapo()
    #    time.sleep(300)


def finderSapo(): 
    print("Casas descobertas:")
    response = requests.get(URL_SAPO,headers=headers_sapo)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("div", class_="property")

    for result in results:
        tipologia_element = result.find("div", class_="property-type")
        location_element = result.find("div", class_="property-location")
        price_element = result.find("div", class_="property-price-value")
        size_element = result.find("div", class_="property-features-text")
        link_element = result.find('a',href=True)
        insert(name=tipologia_element.text.split()[1],
                location=location_element.text.split()[0],
                price=price_element.text,
                size=size_element.text.split()[0],
                site="casa.sapo.pt",
                link="www.casa.sapo.pt"+link_element['href'],
                tipologia=tipologia_element.text.split()[1])
        

def finderImovirtual(): 
    print("Casas descobertas:")
    response = requests.get(URL_IMOVIRTUAL,headers=headers_imovirtual)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("article", class_="offer-item")
    for result in results:
        title_element = result.find("span", class_="offer-item-title")
        location_element = result.find("span", class_="hidden-xs")
        price_element = result.find("li", class_="offer-item-price")
        tipologia_element = result.find("li", class_="offer-item-rooms hidden-xs")
        size_element = result.find("li", class_="hidden-xs offer-item-area")
        link_element= result['data-url']
        insert(name=title_element.text,
                location=location_element.text,
                price=price_element.text.split()[0]+"",
                tipologia=tipologia_element.text,
                size=size_element.text,
                site="imovirtual.com",
                link=link_element
                )


def finderIdealista(): 
    print("Casas descobertas:")
    path = "/home/andre/chromedriver"
    driver = webdriver.Chrome(path)
    url = driver.command_executor._url       #"http://127.0.0.1:60622/hub"
    session_id = driver.session_id 

    driver = webdriver.Remote(command_executor=url,desired_capabilities={})
    driver.close()   # this prevents the dummy browser
    driver.session_id = session_id  
    driver.get("www.google.pt")
    #response = requests.get(URL_IDEALISTA,headers=headers_idealista)
    #print(response.status_code)
    #soup = BeautifulSoup(response.content, "html.parser")
    #results = soup.find_all("article", class_="offer-item")




#,price,size,site,link
def insert(name,location,price,size,site,link,tipologia):
    print(site)
    print(name)
    print(tipologia)
    print(location)
    print(price)
    print(size)
    print(link)
    print()

if __name__ == "__main__":
    main()

