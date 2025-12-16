import asyncio
import random
import csv
import os
from extractor import Extractor
from html_parse import Html_ext
from logger import logger
#Pagrindine puslapio nuoroda
URL_HEAD = "https://m.aruodas.lt"
#Skelbimu kategorijos
CATEGORIES = {
    "RENT_HOUSE": "/namu-nuoma/vilniuje",
    "SELL_HOUSE": "/namai/vilniuje",
    "RENT_FLAT": "/butu-nuoma/vilniuje",
    "SELL_FLAT": "/butai/vilniuje"
    }

CHUNK = 10

#PAGALBINE funkcija procesuoti linkus gabalais
def chunks(lst, n):
    for i in range(0, len(lst), n):
        #sugrazina iteruojama atkarpom lista
        yield lst[i:i + n]

async def main():

    e = Extractor()
    h = Html_ext()

    #kekvienaam tipui is objektu
    for key in CATEGORIES:
        url = f"{URL_HEAD}{CATEGORIES[key]}"
        page_no = 1
        all_cat_links = []
        #pirmo  puslapio urlas
        page_url = f"{url}/"
        #surenkame pacias nuorodas i house listingus
        while True:
            
            try:
                html, status = await e.fetch(page_url)
                #gali sustoti jei url blogas ir bus redirectinamas
                if status == 302:
                    logger.info(f"last page for cattegory {key} is {page_no}/ or got redirected")
                    break
                links_raw = h.ext_links(html)
                links = [URL_HEAD + url for url in links_raw]
                all_cat_links.extend(links)
            except Exception as err:
                logger.info(f"Exception {err}")
                break

            

            #limiting    
            base_delay = random.uniform(1, 2)
            await asyncio.sleep(base_delay + random.random() * 0.5)

            page_no += 1
            page_url = f"{url}/puslapis/{page_no}/"
        
        
        #breakina jei praeina sarasas be linku
        if len(all_cat_links) > 0:
            result = f"result_data/{key}.csv"
            write_header = not os.path.exists(result) or os.path.getsize(result) == 0

            with open(result,"w",newline="",encoding="utf-8") as f:
                #pagal   html_parse shema padarom laukelius pavadinimus
                w = csv.DictWriter(f, fieldnames=h.schema, extrasaction="ignore")
                if write_header: 
                    w.writeheader()
                links_chunked = chunks(all_cat_links, CHUNK)

                
                for chunk in links_chunked:
                    # asynchronous laukiam keliu puslapiu duomenu
                    data = await e.fetch_all(chunk, 6)

                    rows = []
                    #nebandom istraukineti is html is ne html
                    for html, status in data:
                        if status == 200:
                            row = h.ext_data(html)
                            rows.append(row)
                    w.writerows(rows)
            
    # url = "https://m.aruodas.lt/butu-nuoma/vilniuje/puslapis/2/"
    # url = "https://m.aruodas.lt/butu-nuoma-vilniuje-seskineje-buivydiskiu-g-vieno-kambario-butas-su-grazia-panorama-pro-4-1432650/"

    # e = Extractor()
    # h = Html_ext()
    # data = await e.fetch(url)

    # soup = BeautifulSoup(data, "html.parser")   # no lxml needed

    # # save pretty (optional)
    # with open("listing.html", "w", encoding="utf-8") as f:
    #     f.write(soup.prettify())

    

        


if __name__ == "__main__":
    asyncio.run(main())
