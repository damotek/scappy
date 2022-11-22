import requests
from bs4 import BeautifulSoup
import time
import sqlite3 as sl
from selenium import webdriver
import asyncio
import telegram

URL_SAPO = "https://casa.sapo.pt/alugar-apartamentos/t3,t4,t5,t6-ou-superior/lisboa/?gp=1200"
headers_sapo = {"Referer": "https://casa.sapo.pt/alugar-apartamentos/t3/ofertas-recentes/lisboa/", "User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

URL_IDEALISTA = "https://www.idealista.pt/arrendar-casas/lisboa/com-preco-max_1200,t3,t4-t5/"
headers_idealista = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

URL_IMOVIRTUAL = "https://www.imovirtual.com/arrendar/apartamento/lisboa/?search%5Bfilter_float_price%3Ato%5D=1200&search%5Bfilter_enum_rooms_num%5D%5B0%5D=3&search%5Bfilter_enum_rooms_num%5D%5B1%5D=4&search%5Bregion_id%5D=11&search%5Bsubregion_id%5D=153"
headers_imovirtual = {"Referer": "https://www.idealista.pt/","user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36", 'referer': 'https://www.google.com/'}

TELEGRAM_TOKEN = "5778738247:AAER8-DAa5UkRC5vQvjdmSNDewoJHiQbdv4"

async def main():
    bot = telegram.Bot(TELEGRAM_TOKEN)

    async with bot:
        await bot.send_message(text='Bot á Procura de casas', chat_id=440147535)

    con = sl.connect('casas.db')
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS casas (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    tipologia TEXT,
                    location TEXT,
                    price INTEGER,
                    size INTEGER,
                    site TEXT,
                    link TEXT   
            );""")

    while(True):
        finderSapo(con,bot)
        finderImovirtual(con,bot)
        time.sleep(100)

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

async def finderSapo(bot,con): 
    response = requests.get(URL_SAPO,headers=headers_sapo)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("div", class_="property")

    for result in results:
        tipologia_element = result.find("div", class_="property-type")
        location_element = result.find("div", class_="property-location")
        price_element = result.find("div", class_="property-price-value")
        size_element = result.find("div", class_="property-features-text")
        
        link_element = result.find('a',href=True)

        id = result.find('div', class_="property-owner-contact")

        id = id.span.attrs["onclick"][id.span.attrs["onclick"].rfind("uid : '")+7:id.span.attrs["onclick"].rfind("',")]


        insert(con=con,
                bot=bot,
                id = id,
                name=tipologia_element.text.split()[1],
                location=location_element.text.split()[0],
                price=price_element.text,
                size=size_element.text.split()[0],
                site="casa.sapo.pt",
                link="www.casa.sapo.pt"+link_element['href'],
                tipologia=tipologia_element.text.split()[1])
        

async def finderImovirtual(bot, con): 
    response = requests.get(URL_IMOVIRTUAL,headers=headers_imovirtual)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("article", class_="offer-item")

    for result in results:
        title_element = result.find("span", class_="offer-item-title")
        location_element = result.find("p", class_="text-nowrap")
        location = location_element.text[location_element.text.rfind(":")+1:location_element.text.rfind(",")]

        price_element = result.find("li", class_="offer-item-price")
        tipologia_element = result.find("li", class_="offer-item-rooms hidden-xs")
        size_element = result.find("li", class_="hidden-xs offer-item-area")
        link_element= result['data-url']
        id = link_element[link_element.rfind("ID"):link_element.rfind(".")]
        insert(con=con,
                bot=bot,
                id=id,
                name=title_element.text,
                location=location,
                price=price_element.text.split()[0]+""+price_element.text.split()[1],
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

def isInTable(db,data,query,con):
    cursor= db.cursor()
    cursor.execute("SELECT * FROM casas WHERE id = %s",data[0])
    result = cursor.fetchall()
    if result.size() == 0 :
        with con:
            con.executemany(sql, data)
    #print(result)
    #print(data)
    return False


#,price,size,site,link
async def insert(bot,con,id, name,location,price,size,site,link,tipologia):

    sql = 'INSERT OR IGNORE INTO casas (id, name, tipologia, location, price, size, site, link) values(?, ?, ?, ?, ?, ?, ?, ?) '
    data = [
        (id, name, tipologia, location, price, size, site, link)
    ]
    cursor= con.cursor()

    t = 'SELECT id FROM casas'

    cursor.execute(t)

    myresult = cursor.fetchall()

    async with bot:
        await bot.send_message(text='passou aqui', chat_id=440147535)

    for x in myresult:
        if x[0] == data[0][0]:
            #print(x[0]+"=="+data[0][0])
            return

    print("Nova Casa")
    with con:
        con.executemany(sql, data)
    
    async with bot:
        await bot.send_message(text='Hi John!', chat_id=440147535)

    printLine(id,name,location,price,size,site,tipologia)
    
def printLine(id, name,location,price,size,site,tipologia):
    print(id+ " | "+tipologia+" | "+price+" | "+name+" | "+location)


if __name__ == "__main__":
    asyncio.run(main())


