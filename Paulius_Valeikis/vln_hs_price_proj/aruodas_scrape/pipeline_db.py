import asyncio
import random
from .extractor import Extractor
from .html_parse import Html_ext
from logger import logger
from .DB_manage import DBManager

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
    db = DBManager()

    db.ensure_schema()

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
        
        total_pages = max(0, page_no - 1)
        db.start_task(category=key, pages=total_pages)
        db.begin_run()
        try:
            #breakina jei praeina sarasas be linku
            if len(all_cat_links) > 0:
                links_chunked = chunks(all_cat_links, CHUNK)
                    
                for chunk in links_chunked:
                    # asynchronous laukiam keliu puslapiu duomenu
                    data = await e.fetch_all(chunk, 6)

                    #nebandom istraukineti is html is ne html
                    for html, status in data:
                        if status == 200:
                            row = h.ext_data(html)
                            db.insert_row(row,key)
                db.finalize()
            
            db.finish_task()
        
        except Exception as err:
            # log both to console and tasks table
            logger.error(f"Error in category {key}: {err}")
            db.finish_task(records=0, error=str(err))
    
    db.close()

#kad cli veikia reikia synchronous funkcijos
def run_pipeline():
    asyncio.run(main())


if __name__ == "__main__":
    run_pipeline()