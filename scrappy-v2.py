import requests
from bs4 import BeautifulSoup
import time
import sqlite3 as sl
from selenium import webdriver
import json
import http.client
import ssl
import urllib.request

CORE_LINK = "https://pt-houseid-core.onrender.com/propertie"
CHAT_ID = "-1001671165112"
API_KEY = "5778738247:AAER8-DAa5UkRC5vQvjdmSNDewoJHiQbdv4"

headers = {"Content-Type": "application/json; charset=utf-8"}
URL_SAPO = "https://casa.sapo.pt/alugar-apartamentos/t4,t5,t6-ou-superior/lisboa/?gp=1600"
headers_sapo = {"Referer": "https://https://casa.sapo.pt/alugar-apartamentos/t4,t5,t6-ou-superior/lisboa/", "User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

URL_IDEALISTA = "https://www.idealista.pt/arrendar-casas/lisboa/com-preco-max_1200,t3,t4-t5/"
headers_idealista = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

URL_IMOVIRTUAL = "https://www.imovirtual.com/arrendar/apartamento/?page="
headers_imovirtual = {"Referer": "https://www.idealista.pt/","user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36", 'referer': 'https://www.google.com/'}

TELEGRAM_TOKEN = "5778738247:AAER8-DAa5UkRC5vQvjdmSNDewoJHiQbdv4"

def main():
    for i in range(10000000):
        finderImovirtual(i)
def dbCreate(con):
    with con:
        con.execute("""
            CREATE TABLE casas (
                    id TEXT PRIMARY KEY
                    name TEXT,
                    tipologia TEXT,
                    location TEXT,
                    price INTEGER,
                    size INTEGER,
                    site TEXT,
                    link TEXT,      
            );
        """)

        

def finderImovirtual(page): 


    response = requests.get(URL_IMOVIRTUAL+str(page),headers=headers_imovirtual, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("article", class_="offer-item")
    print("aqui")
    for result in results:
        title_element = result.find("span", class_="offer-item-title")
        location_element = result.find("p", class_="text-nowrap")
        countie = location_element.text[location_element.text.rfind(":")+1:location_element.text.rfind(",")]
        district = location_element.text[location_element.text.rfind(",")+2:]

        price_element = result.find("li", class_="offer-item-price")
        tipologia_element = result.find("li", class_="offer-item-rooms hidden-xs")
        size_element = result.find("li", class_="hidden-xs offer-item-area")
        link_element= result['data-url']
        imgs = result.find_all('img')
        src = []
        for img in imgs:
            src.append(img.get('src'))

        foto= result.find("span", class_="img-cover lazy")
        id = link_element[link_element.rfind("ID"):link_element.rfind(".")]

        image_links = result.find_all("figure", class_="offer-item-image")
        img_link2 = ''
        for image_link in image_links:
            # Extract the image link
            img_link = image_link["data-quick-gallery"]
            img_link = img_link.split('photo":"')[1].split('","thumb"')[0]

            # Extract the image name
            img_name = img_link.split("/")[-1]

            img_link = fix_link(img_link)
            img_link2 = img_link 
            #print("Image Link:", img_link)
            #print("Image Name:", img_name)
            #print("-------------------")

        
        final_price = price_element.text.split()[0]+""+price_element.text.split()[1]
        final_price = final_price.replace('€', '')
        final_price = final_price.replace('Preçosob','0')
        print("----------------")
        print("nome: "+ title_element.text)
        print("tipologia: " + tipologia_element.text)
        print("price: "+ final_price)
        print("listPrice :" + "RENT")
        print("district :"+ district.upper()+"!!")
        print("countie :"+ countie)
        print("link :"+ link_element)
        print("Image Link:", img_link2)
        print("PROVIDER: "+ "IMOVIRTUAL")
        print("area :"+ size_element.text[0:3])
        print("----------------")

        headers = {'Content-type': 'application/json'}
        bodycontent = {
                'price': int(final_price),
                'countie':countie,
                'listType':"RENT",
                'tipology':tipologia_element.text,
                'district': district.upper(),
                'link': link_element,
                'provider': "IMOVIRTUAL",
                'images': img_link2,
                'area':size_element.text[0:3]}
        url = 'https://pt-houseid-core.onrender.com/propertie'
        requests.put(CORE_LINK, json=bodycontent, headers=headers, params= bodycontent)


def fix_link(link):
    fixed_link = link.replace('\\/', '/')
    fixed_link = fixed_link.split(';')[0]
    return fixed_link


if __name__ == "__main__":
    main()


