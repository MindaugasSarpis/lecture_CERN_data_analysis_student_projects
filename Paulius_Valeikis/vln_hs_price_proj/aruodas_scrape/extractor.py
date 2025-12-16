import asyncio
from rnet import Impersonate, Client, BlockingClient
from tenacity import retry, stop_after_attempt
from logger import logger




class Extractor: 
    #kad inicializuojant objekta buti aktyvi ta pati sesija ir enreiktu passinti per funkcijas
    def __init__(self) -> None:
        self.session = Client()
        self.session.update(
            impersonate=Impersonate.Firefox139
        )
        logger.info("Session created")
        self.blocking = BlockingClient()
        self.blocking.update(
            impersonate=Impersonate.Firefox139
        )
    @retry(stop=stop_after_attempt(3))
    async def fetch(self, url):
        logger.info(f"requasting url: {url}")
        
        resp = await self.session.get(url)
        #print("status:", resp.status)
        # print("final_url:", str(resp.url))
        
        html = await resp.text()

        # print("len(html):", len(html))
        # print(html[:400])  # look 
        return html, resp.status
    
    async def fetch_all(self, urls, conc):
        #limituoja requestu skaiciu vienu metu
        sem = asyncio.Semaphore(conc) 
        async def safe_fetch(url):
            async with sem:
                
                #eat status code her meibe
                return await self.fetch(url)

        tasks = [safe_fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return  results
    
    def blocking_fetch(self, url):
        logger.info(f"requasting url: {url}")
        resp = self.blocking.get(url)
        return resp.text()
    

# async def main():

#     e = Extractor()
#     urls = [
#         "https://m.aruodas.lt/namu-nuoma-vilniuje-baltupiuose-kolektyvo-g-isnuomojamas-kambariu-namas-kolektyvo-g-5-92500/",
#         "https://m.aruodas.lt/namu-nuoma-vilniuje-pilaiteje-romintos-g-isnuomojamas-visiskai-naujas-jaukus-namas-5-92486/",
#         "https://m.aruodas.lt/namu-nuoma-vilniuje-antakalnyje-virsupio-sodu-9-oji-g-kambariu-namas-antakalnyje-virsupio-sodu-5-92452/",
#         "https://m.aruodas.lt/namu-nuoma-vilniuje-pavilnyje-pranciskaus-petro-bucio-g-ilgalaikei-nuomai-isnuomojamas-erdvus-5-92426/"
#     ]

#     htmls = await e.fetch_all(urls, 4)
#     for html in htmls:
#         print(f"type : {html[0]} status is prolly this {html[1]}")

# if __name__ == "__main__":
#     asyncio.run(main())
     


    

    


